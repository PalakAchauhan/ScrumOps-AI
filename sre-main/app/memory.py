import os
import json
from datetime import datetime

MEMORY_DIR = "memory"

if not os.path.exists(MEMORY_DIR):
    os.makedirs(MEMORY_DIR)

# Active standup sessions
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
    today_work,
    blockers,
    support
):

    history = load_memory(user_id)

    history.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "today_work": today_work,
        "blockers": blockers,
        "support": support
    })

    save_memory(user_id, history)


# ---------------------------------------------------
# SESSION MANAGEMENT
# ---------------------------------------------------

def start_session(user_id):

    ACTIVE_SESSIONS[user_id] = {
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
