import os
import json

from datetime import datetime, timedelta

MEMORY_DIR = "memory"

if not os.path.exists(MEMORY_DIR):
    os.makedirs(MEMORY_DIR)

ACTIVE_SESSIONS = {}

# ---------------------------------------------------

# FILE HELPERS

# ---------------------------------------------------

def get_user_file(user_id):

    return os.path.join(
        MEMORY_DIR,
        f"{user_id}.json"
    )

# ---------------------------------------------------

# HISTORY STORAGE

# ---------------------------------------------------

def load_memory(user_id):

    file_path = get_user_file(user_id)

    if not os.path.exists(file_path):
        return []

    with open(file_path, "r") as f:

        return json.load(f)

def save_memory(user_id, memory):

    file_path = get_user_file(user_id)

    with open(file_path, "w") as f:

        json.dump(memory, f, indent=2)

def get_user_history(user_id):

    return load_memory(user_id)

def save_standup_record(
    user_id,
    status,
    today_work,
    blockers,
    support
):

    history = load_memory(user_id)

    history.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "status": status,
        "today_work": today_work,
        "blockers": blockers,
        "support": support
    })

    save_memory(user_id, history)

# ---------------------------------------------------

# REPORTS

# ---------------------------------------------------

def get_today_report(user_id):

    history = load_memory(user_id)

    today = datetime.now().strftime("%Y-%m-%d")

    return [
        item
        for item in history
        if item.get("date") == today
    ]

def get_weekly_report(user_id):

    history = load_memory(user_id)

    week_ago = datetime.now() - timedelta(days=7)

    report = []

    for item in history:

        item_date = datetime.strptime(
            item["date"],
            "%Y-%m-%d"
        )

        if item_date >= week_ago:

            report.append(item)

    return report

def get_monthly_report(user_id):

    history = load_memory(user_id)

    current_month = datetime.now().month
    current_year = datetime.now().year

    report = []

    for item in history:

        item_date = datetime.strptime(
            item["date"],
            "%Y-%m-%d"
        )

        if (
            item_date.month == current_month
            and item_date.year == current_year
        ):

            report.append(item)

    return report

def get_yearly_report(user_id):

    history = load_memory(user_id)

    current_year = datetime.now().year

    report = []

    for item in history:

        item_date = datetime.strptime(
            item["date"],
            "%Y-%m-%d"
        )

        if item_date.year == current_year:

            report.append(item)

    return report

def get_open_blockers(user_id):

    history = load_memory(user_id)

    blockers = []

    for item in history:

        if item.get("status", "").lower() == "blocked":

            blockers.append(item)

    return blockers

# ---------------------------------------------------

# SESSION MANAGEMENT

# ---------------------------------------------------

def start_session(user_id, status="on_track"):

    ACTIVE_SESSIONS[user_id] = {
        "status": status,
        "stage": 1,
        "today_work": "",
        "blockers": "",
        "support": ""
    }

def get_session(user_id):

    return ACTIVE_SESSIONS.get(user_id)

def update_session(user_id, key, value):

    if user_id not in ACTIVE_SESSIONS:
        return

    ACTIVE_SESSIONS[user_id][key] = value

def end_session(user_id):

    if user_id in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[user_id]
