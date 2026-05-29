import os
import json
import google.generativeai as genai

from dotenv import load_dotenv

from app.memory import (
    start_session,
    get_session,
    update_session,
    end_session,
    save_standup_record
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


# ---------------------------------------------------
# SCRUM FOLLOWUP FLOW
# ---------------------------------------------------

def generate_followup_question(user_id, user_message):

    session = get_session(user_id)

    if not session:

        return (
            "Please start a standup first by typing "
            "'start standup'"
        )

    stage = session["stage"]

    # Question 1 answered
    if stage == 1:

        update_session(
            user_id,
            "today_work",
            user_message
        )

        session["stage"] = 2

        return (
            "Do you have any blockers today?"
        )

    # Question 2 answered
    elif stage == 2:

        update_session(
            user_id,
            "blockers",
            user_message
        )

        session["stage"] = 3

        return (
            "Do you need any support from the team?"
        )

    # Question 3 answered
    elif stage == 3:

        update_session(
            user_id,
            "support",
            user_message
        )

        save_standup_record(
            user_id,
            session["today_work"],
            session["blockers"],
            user_message
        )

        end_session(user_id)

        return (
            "✅ Thanks for the update.\n\n"
            "Standup completed successfully.\n\n"
            "Summary:\n"
            f"• Work: {session['today_work']}\n"
            f"• Blockers: {session['blockers']}\n"
            f"• Support: {user_message}\n\n"
            "Have a productive day!"
        )

    return "Standup completed."


# ---------------------------------------------------
# JIRA SPRINT STRUCTURE GENERATOR
# ---------------------------------------------------

def generate_jira_structure(user_prompt):

    prompt = f'''
You are an expert Agile Scrum Master.

Convert the following requirement into:

1. Epic
2. User Stories
3. Tasks

Return STRICT JSON format only.

Format:

{{
  "epic": {{
    "title": "",
    "description": ""
  }},
  "stories": [
    {{
      "title": "",
      "description": "",
      "tasks": [
        ""
      ]
    }}
  ]
}}

Requirement:
{user_prompt}
'''

    response = model.generate_content(prompt)

    text = response.text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")

    try:

        return json.loads(text)

    except Exception as e:

        return {
            "error": str(e),
            "raw_response": text
        }


# ---------------------------------------------------
# MODIFY EXISTING SPRINT
# ---------------------------------------------------

def modify_sprint(original_prompt, modification_prompt):

    prompt = f'''
You are an Agile Scrum AI Assistant.

Original Sprint Requirement:
{original_prompt}

Modification Request:
{modification_prompt}

Update the sprint structure accordingly.

Return proper readable response.
'''

    response = model.generate_content(prompt)

    return response.text.strip()
