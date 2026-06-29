import json
import os
from datetime import datetime, timedelta

MEMORY_DIR = "memory"

os.makedirs(MEMORY_DIR, exist_ok=True)

ACTIVE_SESSIONS = {}


def get_user_file(user_id):

    return os.path.join(MEMORY_DIR, f"{user_id}.json")


def load_memory(user_id):

    file_path = get_user_file(user_id)

    if not os.path.exists(file_path):
        return []

    try:

        with open(file_path, "r", encoding="utf-8") as f:

            history = json.load(f)

    except Exception:

        history = []

    for item in history:

        item.setdefault("time", "Unknown")

        item.setdefault("status", "N/A")

        item.setdefault("today_work", "N/A")

        item.setdefault("blockers", "None")

        item.setdefault("support", "No")

    return history


def save_memory(user_id, memory):

    file_path = get_user_file(user_id)

    with open(file_path, "w", encoding="utf-8") as f:

        json.dump(memory, f, indent=4)


def get_user_history(user_id):

    history = load_memory(user_id)

    history.sort(key=lambda x: (x.get("date", ""), x.get("time", "")), reverse=True)

    return history


def save_standup_record(user_id, status, today_work, blockers, support):

    history = load_memory(user_id)

    now = datetime.now()

    history.append(
        {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%I:%M %p"),
            "status": status,
            "today_work": today_work,
            "blockers": blockers,
            "support": support,
        }
    )

    save_memory(user_id, history)


def get_today_report(user_id):

    today = datetime.now().strftime("%Y-%m-%d")

    history = load_memory(user_id)

    report = [item for item in history if item.get("date") == today]

    return sorted(report, key=lambda x: x.get("time", ""), reverse=True)


def get_yesterday_report(user_id):

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    history = load_memory(user_id)

    report = [item for item in history if item.get("date") == yesterday]

    return sorted(report, key=lambda x: x.get("time", ""), reverse=True)


def get_weekly_report(user_id):

    history = load_memory(user_id)

    week_ago = datetime.now() - timedelta(days=7)

    report = []

    for item in history:

        try:

            item_date = datetime.strptime(item["date"], "%Y-%m-%d")

            if item_date >= week_ago:

                report.append(item)

        except Exception:

            pass

    return sorted(report, key=lambda x: x.get("date", ""), reverse=True)


def get_monthly_report(user_id):

    history = load_memory(user_id)

    now = datetime.now()

    report = []

    for item in history:

        try:

            d = datetime.strptime(item["date"], "%Y-%m-%d")

            if d.month == now.month and d.year == now.year:

                report.append(item)

        except Exception:

            pass

    return sorted(report, key=lambda x: x.get("date", ""), reverse=True)


def get_yearly_report(user_id):

    history = load_memory(user_id)

    year = datetime.now().year

    report = []

    for item in history:

        try:

            d = datetime.strptime(item["date"], "%Y-%m-%d")

            if d.year == year:

                report.append(item)

        except Exception:

            pass

    return sorted(report, key=lambda x: x.get("date", ""), reverse=True)


def get_open_blockers(user_id):

    history = load_memory(user_id)

    blockers = []

    for item in history:

        status = item.get("status", "").lower()

        if status == "blocked":

            blockers.append(item)

    return blockers


def start_session(user_id, status="on_track"):
    """
    Starts a fresh standup session for the user.
    """

    ACTIVE_SESSIONS[user_id] = {
        "status": status,
        "stage": 1,
        "today_work": "",
        "blockers": "",
        "support": "",
        "started_at": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
    }


def get_session(user_id):
    """
    Returns the current active session.
    """

    return ACTIVE_SESSIONS.get(user_id)


def update_session(user_id, key, value):
    """
    Updates one field of the current session.
    """

    if user_id not in ACTIVE_SESSIONS:
        return

    ACTIVE_SESSIONS[user_id][key] = value


def session_exists(user_id):
    """
    Returns True if a standup session is currently active.
    """

    return user_id in ACTIVE_SESSIONS


def reset_session(user_id):
    """
    Clears all answers while keeping the user in session.
    Useful if the user wants to restart the standup.
    """

    if user_id not in ACTIVE_SESSIONS:
        return

    ACTIVE_SESSIONS[user_id].update(
        {"stage": 1, "today_work": "", "blockers": "", "support": ""}
    )


def end_session(user_id):
    """
    Ends the active session.
    """

    ACTIVE_SESSIONS.pop(user_id, None)


def get_latest_report(user_id):
    """
    Returns the latest report submitted by the user.
    """

    history = get_user_history(user_id)

    if history:
        return history[0]

    return None


def get_report_by_date(user_id, date):
    """
    Returns all reports for a specific date.
    Date format:
        YYYY-MM-DD
    """

    history = load_memory(user_id)

    return [item for item in history if item.get("date") == date]


def get_report_statistics(user_id):
    """
    Returns basic statistics for dashboard/reporting.
    """

    history = load_memory(user_id)

    stats = {"total_reports": len(history), "blocked_days": 0, "on_track_days": 0}

    for item in history:

        status = item.get("status", "").lower()

        if status == "blocked":
            stats["blocked_days"] += 1

        elif status == "on_track":
            stats["on_track_days"] += 1

    return stats
