import json
import os
import sys
from datetime import datetime, timedelta

from app.bot import (generate_followup_question, generate_jira_structure,
                     modify_sprint)
from app.jira import create_jira_issues_from_structure, jira_is_configured
from app.memory import (get_monthly_report, get_open_blockers,
                        get_today_report, get_user_history, get_weekly_report,
                        get_yearly_report, get_yesterday_report, start_session)
from app.reports.report_generator import create_doc
from app.slack_blocks import create_standup_block
from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slack_sdk import WebClient

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REPORT_DIR = os.path.join(BASE_DIR, "generated_reports")

os.makedirs(REPORT_DIR, exist_ok=True)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

client = WebClient(token=SLACK_BOT_TOKEN)

app = FastAPI()

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

ASSISTANT_TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "index.html")

with open(ASSISTANT_TEMPLATE_PATH, "r", encoding="utf-8") as f:

    ASSISTANT_TEMPLATE = f.read()

app.mount(
    "/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static"
)


def log_debug(*messages):

    sys.stderr.write("[APP DEBUG] " + " ".join(str(x) for x in messages) + "\n")

    sys.stderr.flush()


log_debug("SprintOps starting...")


def format_display_date(date_string):
    """
    Converts

    2026-06-28

    into

    28 June 2026
    """

    try:

        return datetime.strptime(date_string, "%Y-%m-%d").strftime("%d %B %Y")

    except Exception:

        return date_string


def current_date():

    return datetime.now().strftime("%d %B %Y")


def current_month():

    return datetime.now().strftime("%B %Y")


def current_year():

    return datetime.now().strftime("%Y")


def weekly_range():

    today = datetime.now()

    start = today - timedelta(days=6)

    return (start.strftime("%d %b %Y"), today.strftime("%d %b %Y"))


def generate_doc_report(report, report_type):

    filename = os.path.join(
        REPORT_DIR, f"{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    )

    create_doc(report, filename, report_type)

    return filename


def upload_report_to_slack(channel_id, file_path, title):

    try:

        client.files_upload_v2(channel=channel_id, file=file_path, title=title)

        return True

    except Exception as ex:

        log_debug(ex)

        return False


@app.get("/")
async def home():

    return RedirectResponse(
        url="https://app.slack.com/client/T0B9BN3GCDC/C0B9HCWP5LL", status_code=302
    )


@app.get("/assistant", response_class=HTMLResponse)
async def assistant_ui(request: Request):

    return ASSISTANT_TEMPLATE


@app.post("/generate")
async def generate(request: Request, prompt: str = Form(...)):

    log_debug("Generating Jira...")

    structure = generate_jira_structure(prompt)

    jira_response = None

    if jira_is_configured():

        jira_response = create_jira_issues_from_structure(structure)

    if jira_response and jira_response.get("success"):

        return RedirectResponse(url=jira_response["issue_url"], status_code=302)

    return JSONResponse({"success": False, "jira": jira_response})


@app.post("/modify")
async def modify(
    original_prompt: str = Form(...), modification_prompt: str = Form(...)
):

    updated = modify_sprint(original_prompt, modification_prompt)

    return JSONResponse({"success": True, "updated": updated})


@app.post("/slack/events")
async def slack_events(request: Request):

    data = await request.json()

    if "challenge" in data:
        return JSONResponse({"challenge": data["challenge"]})

    event = data.get("event", {})

    if event.get("type") == "app_home_opened":

        client.views_publish(
            user_id=event["user"],
            view={
                "type": "home",
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "SprintOps Assistant"},
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                "✅ SprintOps Assistant is Active\n\n"
                                "AI Powered Sprint Planning\n"
                                "Daily Standups\n"
                                "Downloadable Reports\n"
                                "Jira Automation"
                            ),
                        },
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                "*Available Commands*\n\n"
                                "• Start Standup\n"
                                "• Show Today Report\n"
                                "• Show Yesterday Update\n"
                                "• Show Weekly Report\n"
                                "• Show Monthly Report\n"
                                "• Show Yearly Report\n"
                                "• Download Today Report\n"
                                "• Download Weekly Report\n"
                                "• Download Monthly Report\n"
                                "• Download Yearly Report\n"
                                "• Show Open Blockers\n"
                                "• Launch AI Assistant"
                            ),
                        },
                    },
                ],
            },
        )

        return JSONResponse({"status": "home"})

    if event.get("type") == "message" and "bot_id" not in event:

        user_id = event["user"]
        text = event.get("text", "").strip().lower()
        channel_id = event["channel"]

        if text == "start standup":

            blocks = create_standup_block(
                user_name="Developer",
                tasks=["Sprint Activities", "Testing", "Project Work"],
            )

            client.chat_postMessage(
                channel=channel_id, text="Daily Standup", blocks=blocks
            )

            return JSONResponse({"status": "sent"})

        if text == "show today report":

            report = get_today_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id, text="No standup submitted today."
                )

                return JSONResponse({"status": "empty"})

            response = "📅 *Today's Report*\n" f"Date : {current_date()}\n\n"

            for item in report:

                response += (
                    f"Status : {item.get('status','N/A')}\n"
                    f"Work : {item.get('today_work','N/A')}\n"
                    f"Blockers : {item.get('blockers','N/A')}\n"
                    f"Support : {item.get('support','N/A')}\n\n"
                )

            client.chat_postMessage(channel=channel_id, text=response)

            return JSONResponse({"status": "today"})

        if text == "show yesterday update":

            report = get_yesterday_report(user_id)

            if not yesterday_report:

                client.chat_postMessage(
                    channel=channel_id, text="No report found for yesterday."
                )

                return JSONResponse({"status": "empty"})

            response = (
                "📋 *Yesterday's Report*\n"
                f"Date : {format_display_date(yesterday)}\n\n"
            )

            for item in yesterday_report:

                response += (
                    f"Status : {item.get('status','N/A')}\n"
                    f"Work : {item.get('today_work','N/A')}\n"
                    f"Blockers : {item.get('blockers','N/A')}\n"
                    f"Support : {item.get('support','N/A')}\n\n"
                )

            client.chat_postMessage(channel=channel_id, text=response)

            return JSONResponse({"status": "yesterday"})

        if text == "show weekly report":

            report = get_weekly_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id, text="No weekly report found."
                )

                return JSONResponse({"status": "empty"})

            start, end = weekly_range()

            response = "📊 *Weekly Report*\n" f"{start} - {end}\n\n"

            for item in report:

                response += (
                    f"📅 {format_display_date(item['date'])}\n"
                    f"Status : {item['status']}\n"
                    f"Work : {item['today_work']}\n"
                    f"Blockers : {item['blockers']}\n\n"
                )

            client.chat_postMessage(channel=channel_id, text=response)

            return JSONResponse({"status": "weekly"})

        if text == "show monthly report":

            report = get_monthly_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id, text="No monthly report found."
                )

                return JSONResponse({"status": "empty"})

            response = f"📈 *Monthly Report*\n" f"{current_month()}\n\n"

            for item in report:

                response += (
                    f"{format_display_date(item['date'])}\n"
                    f"Status : {item['status']}\n"
                    f"Work : {item['today_work']}\n\n"
                )

            client.chat_postMessage(channel=channel_id, text=response)

            return JSONResponse({"status": "monthly"})

        if text == "show yearly report":

            report = get_yearly_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id, text="No yearly report found."
                )

                return JSONResponse({"status": "empty"})

            response = f"📆 *Yearly Report*\n" f"{current_year()}\n\n"

            for item in report:

                response += (
                    f"{format_display_date(item['date'])}\n"
                    f"Status : {item.get('status','N/A')}\n"
                    f"Work : {item.get('today_work','N/A')}\n"
                    f"Blockers : {item.get('blockers','N/A')}\n\n"
                )

            client.chat_postMessage(channel=channel_id, text=response)

            return JSONResponse({"status": "yearly"})

        if "download" in text and "today" in text:

            report = get_today_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id, text="No report available for today."
                )

                return JSONResponse({"status": "empty"})

            filepath = generate_doc_report(report, "today_report")

            upload_report_to_slack(channel_id, filepath, "Today's Report")

            return JSONResponse({"status": "downloaded"})

        if text == "download weekly report":

            report = get_weekly_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id, text="No weekly report available."
                )

                return JSONResponse({"status": "empty"})

            filepath = generate_doc_report(report, "weekly_report")

            upload_report_to_slack(channel_id, filepath, "Weekly Report")

            return JSONResponse({"status": "downloaded"})

        if text == "download monthly report":

            report = get_monthly_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id, text="No monthly report available."
                )

                return JSONResponse({"status": "empty"})

            filepath = generate_doc_report(report, "monthly_report")

            upload_report_to_slack(channel_id, filepath, "Monthly Report")

            return JSONResponse({"status": "downloaded"})

        if text == "download yearly report":

            report = get_yearly_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id, text="No yearly report available."
                )

                return JSONResponse({"status": "empty"})

            filepath = generate_doc_report(report, "yearly_report")

            upload_report_to_slack(channel_id, filepath, "Yearly Report")

            return JSONResponse({"status": "downloaded"})

        if text == "show open blockers":

            blockers = get_open_blockers(user_id)

            if not blockers:

                client.chat_postMessage(channel=channel_id, text="🎉 No open blockers.")

                return JSONResponse({"status": "empty"})

            response = "🔴 *Open Blockers*\n\n"

            for item in blockers:

                response += (
                    f"📅 {format_display_date(item['date'])}\n"
                    f"Work : {item.get('today_work','N/A')}\n"
                    f"Blocker : {item.get('blockers','N/A')}\n\n"
                )

            client.chat_postMessage(channel=channel_id, text=response)

            return JSONResponse({"status": "blockers"})

        if text == "launch ai assistant":

            assistant_url = request.url_for("assistant_ui")

            client.chat_postMessage(
                channel=channel_id, text=f"🚀 Open AI Assistant\n{assistant_url}"
            )

            return JSONResponse({"status": "assistant"})

        reply = generate_followup_question(user_id=user_id, user_message=text)

        client.chat_postMessage(channel=channel_id, text=reply)

    return JSONResponse({"status": "ok"})


@app.post("/slack/interactions")
async def slack_interactions(request: Request):

    form_data = await request.form()

    payload = json.loads(form_data["payload"])

    channel_id = payload["channel"]["id"]
    user_id = payload["user"]["id"]

    action = payload["actions"][0]["action_id"]

    log_debug(f"Interaction received from {user_id} -> {action}")

    if action == "on_track_btn":

        start_session(user_id=user_id, status="on_track")

        reply = (
            "✅ Great! You're marked as *On Track*.\n\n"
            "What are you working on today?"
        )

    elif action == "blocked_btn":

        start_session(user_id=user_id, status="blocked")

        reply = "🔴 You're marked as *Blocked*.\n\n" "What are you working on today?"

    else:

        reply = "Thanks for your response."

    client.chat_postMessage(channel=channel_id, text=reply)

    return JSONResponse({"status": "ok"})
