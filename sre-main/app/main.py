import os
import sys
import json

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from slack_sdk import WebClient

from app.memory import (
    get_user_history,
    start_session,
    get_today_report,
    get_open_blockers,
    get_weekly_report,
    get_monthly_report,
    get_yearly_report
)

from app.slack_blocks import create_standup_block

from app.bot import (
    generate_followup_question,
    generate_jira_structure,
    modify_sprint
)

from app.jira import (
    create_jira_issues_from_structure,
    jira_is_configured
)

load_dotenv()

def log_debug(*messages):
    sys.stderr.write("[APP DEBUG] " + " ".join(str(m) for m in messages) + "\n")
    sys.stderr.flush()

log_debug("App starting up...")

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")

client = WebClient(token=SLACK_BOT_TOKEN)

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)


@app.get("/")
async def home():

    return RedirectResponse(
        url="https://app.slack.com/client/T0B9BN3GCDC/C0B9HCWP5LL",
        status_code=302
    )


# -----------------------------
# AI ASSISTANT UI
# -----------------------------

@app.get("/assistant", response_class=HTMLResponse)
async def assistant_ui(request: Request):

    return templates.TemplateResponse(
        "assistant.html",
        {"request": request}
    )


@app.post("/generate")
async def generate(prompt: str = Form(...)):

    log_debug(f"POST /generate called with prompt: {repr(prompt[:100])}")

    structure = generate_jira_structure(prompt)

    log_debug(f"Generated structure: {structure}")

    jira_response = None

    if jira_is_configured():

        log_debug("Jira is configured, attempting to create issues...")

        jira_response = create_jira_issues_from_structure(
            structure
        )

        log_debug(f"Jira response: {jira_response}")

    else:

        log_debug("Jira is NOT configured, skipping issue creation")

    return JSONResponse({
        "success": True,
        "structure": structure,
        "jira": jira_response
    })


@app.post("/modify")
async def modify(
    original_prompt: str = Form(...),
    modification_prompt: str = Form(...)
):

    updated = modify_sprint(
        original_prompt,
        modification_prompt
    )

    return JSONResponse({
        "success": True,
        "updated": updated
    })


# -----------------------------
# SLACK EVENTS
# -----------------------------

@app.post("/slack/events")
async def slack_events(request: Request):

    data = await request.json()

    log_debug(f"Slack event received: {data.get('type', 'unknown')}")

    if "challenge" in data:

        return JSONResponse({
            "challenge": data["challenge"]
        })

    event = data.get("event", {})

    if (
        event.get("type") == "message"
        and "bot_id" not in event
    ):

        user_id = event.get("user")
        text = event.get("text", "")
        channel_id = event.get("channel")

        log_debug(f"Message from {user_id}: {repr(text[:100])}")

        # -------------------------
        # START STANDUP
        # -------------------------

        if text.lower() == "start standup":

            blocks = create_standup_block(
                user_name="Developer",
                tasks=[
                    "Sprint Activities",
                    "Testing",
                    "Project Work"
                ]
            )

            client.chat_postMessage(
                channel=channel_id,
                text="Daily Standup",
                blocks=blocks
            )

            return JSONResponse({"status": "sent"})

        # -------------------------
        # SHOW YESTERDAY
        # -------------------------

        if text.lower() == "show yesterday update":

            history = get_user_history(user_id)

            if history:

                latest = history[-1]

                client.chat_postMessage(
                    channel=channel_id,
                    text=(
                        f"📋 Yesterday Update\n\n"
                        f"Work: {latest.get('today_work', 'N/A')}\n"
                        f"Blockers: {latest.get('blockers', 'N/A')}\n"
                        f"Support: {latest.get('support', 'N/A')}"
                    )
                )

            else:

                client.chat_postMessage(
                    channel=channel_id,
                    text="No previous standup records found."
                )

            return JSONResponse({"status": "history_sent"})

        # -------------------------
        # SHOW HISTORY
        # -------------------------

        if text.lower() == "show my history":

            history = get_user_history(user_id)

            if not history:

                client.chat_postMessage(
                    channel=channel_id,
                    text="No standup history found."
                )

                return JSONResponse({"status": "history_empty"})

            response = "📊 Last Standups\n\n"

            for item in history[-5:]:

                response += (
                    f"{item.get('date', 'Unknown Date')}\n"
                    f"Work: {item.get('today_work', 'N/A')}\n"
                    f"Blockers: {item.get('blockers', 'N/A')}\n"
                    f"Support: {item.get('support', 'N/A')}\n\n"
                )

            client.chat_postMessage(
                channel=channel_id,
                text=response
            )

            return JSONResponse({"status": "history_sent"})

        # -------------------------
        # SHOW TODAY REPORT
        # -------------------------

        if text.lower() == "show today report":

            report = get_today_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id,
                    text="No updates found for today."
                )

                return JSONResponse({"status": "empty"})

            response = "📅 Today's Report\n\n"

            for item in report:

                response += (
                    f"Status: {item['status']}\n"
                    f"Work: {item['today_work']}\n"
                    f"Blockers: {item['blockers']}\n"
                    f"Support: {item['support']}\n\n"
                )

            client.chat_postMessage(
                channel=channel_id,
                text=response
            )

            return JSONResponse({"status": "sent"})

        # -------------------------
        # SHOW WEEKLY REPORT
        # -------------------------

        if text.lower() == "show weekly report":

            report = get_weekly_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id,
                    text="No weekly data found."
                )

                return JSONResponse({"status": "empty"})

            response = "📊 Weekly Report\n\n"

            for item in report:

                response += (
                    f"{item['date']}\n"
                    f"Status: {item['status']}\n"
                    f"Work: {item['today_work']}\n\n"
                )

            client.chat_postMessage(
                channel=channel_id,
                text=response
            )

            return JSONResponse({"status": "sent"})

        # -------------------------
        # SHOW MONTHLY REPORT
        # -------------------------

        if text.lower() == "show monthly report":

            report = get_monthly_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id,
                    text="No monthly data found."
                )

                return JSONResponse({"status": "empty"})

            response = "📈 Monthly Report\n\n"

            for item in report:

                response += (
                    f"{item['date']}\n"
                    f"Status: {item['status']}\n"
                    f"Work: {item['today_work']}\n\n"
                )

            client.chat_postMessage(
                channel=channel_id,
                text=response
            )

            return JSONResponse({"status": "sent"})

        # -------------------------
        # SHOW YEARLY REPORT
        # -------------------------

        if text.lower() == "show yearly report":

            report = get_yearly_report(user_id)

            if not report:

                client.chat_postMessage(
                    channel=channel_id,
                    text="No yearly data found."
                )

                return JSONResponse({"status": "empty"})

            response = "📆 Yearly Report\n\n"

            for item in report:

                response += (
                    f"{item['date']}\n"
                    f"Status: {item['status']}\n"
                    f"Work: {item['today_work']}\n\n"
                )

            client.chat_postMessage(
                channel=channel_id,
                text=response
            )

            return JSONResponse({"status": "sent"})

        # -------------------------
        # SHOW OPEN BLOCKERS
        # -------------------------

        if text.lower() == "show open blockers":

            blockers = get_open_blockers(user_id)

            if not blockers:

                client.chat_postMessage(
                    channel=channel_id,
                    text="No blockers found."
                )

                return JSONResponse({"status": "empty"})

            response = "🔴 Open Blockers\n\n"

            for item in blockers:

                response += (
                    f"{item['date']}\n"
                    f"Work: {item['today_work']}\n"
                    f"Blocker: {item['blockers']}\n\n"
                )

            client.chat_postMessage(
                channel=channel_id,
                text=response
            )

            return JSONResponse({"status": "sent"})

        # -------------------------
        # LAUNCH AI ASSISTANT
        # -------------------------

        if text.lower() == "launch ai assistant":

            assistant_url = request.url_for("assistant_ui")
            log_debug(f"Launching assistant URL: {assistant_url}")

            client.chat_postMessage(
                channel=channel_id,
                text=f"Open AI Assistant: {assistant_url}"
            )

            return JSONResponse({"status": "assistant_sent"})

        # -------------------------
        # STANDUP CONVERSATION
        # -------------------------

        reply = generate_followup_question(
            user_id=user_id,
            user_message=text
        )

        client.chat_postMessage(
            channel=channel_id,
            text=reply
        )

    return JSONResponse({"status": "ok"})


# -----------------------------
# SLACK INTERACTIONS
# -----------------------------

@app.post("/slack/interactions")
async def slack_interactions(request: Request):

    form_data = await request.form()

    payload = json.loads(
        form_data["payload"]
    )

    channel_id = payload["channel"]["id"]

    action = payload["actions"][0]["action_id"]

    user_id = payload["user"]["id"]

    if action == "on_track_btn":

        start_session(
            user_id,
            status="on_track"
        )

        reply = (
            "✅ Great to hear.\n\n"
            "What are you working on today?"
        )

    elif action == "blocked_btn":

        start_session(
            user_id,
            status="blocked"
        )

        reply = (
            "🔴 Understood.\n\n"
            "What are you working on today?"
        )

    else:

        reply = "Thanks for the update."

    client.chat_postMessage(
        channel=channel_id,
        text=reply
    )

    return JSONResponse({"status": "ok"})


