
def create_standup_block(user_name, tasks):

    task_text = "\n".join([f"• {task}" for task in tasks])

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"👋 *Hey {user_name}!*"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Your current tasks:*\n{task_text}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "What did you complete yesterday, "
                    "what are you focusing on today, "
                    "and is anything blocking your progress?"
                )
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ On Track"
                    },
                    "style": "primary",
                    "value": "on_track",
                    "action_id": "on_track_btn"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🔴 Blocked"
                    },
                    "style": "danger",
                    "value": "blocked",
                    "action_id": "blocked_btn"
                }
            ]
        }
    ]


def create_summary_block(summary):

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"📋 *Standup Summary*\n\n{summary}"
            }
        }
    ]
