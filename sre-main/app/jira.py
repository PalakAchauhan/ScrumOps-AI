import os
import requests
from requests.auth import HTTPBasicAuth

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_API_EMAIL = os.getenv("JIRA_API_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")
JIRA_ISSUE_TYPE = os.getenv("JIRA_ISSUE_TYPE", "Task")


def jira_is_configured():
    return all([
        JIRA_BASE_URL,
        JIRA_API_EMAIL,
        JIRA_API_TOKEN,
        JIRA_PROJECT_KEY
    ])


def build_adf_description(text):
    lines = [line for line in text.split("\n") if line.strip()]
    if not lines:
        lines = [""]

    content = []
    for line in lines:
        content.append({
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": line
                }
            ]
        })

    return {
        "type": "doc",
        "version": 1,
        "content": content
    }


def get_issue_metadata(project_key, issue_type_name):
    url = f"{JIRA_BASE_URL.rstrip('/')}/rest/api/3/issue/createmeta?projectKeys={project_key}&issuetypeNames={issue_type_name}&expand=projects.issuetypes.fields"
    auth = HTTPBasicAuth(JIRA_API_EMAIL, JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json"
    }

    response = requests.get(url, auth=auth, headers=headers, timeout=20)
    if response.ok:
        return response.json()

    return None


def find_field_key(metadata, field_name):
    if not metadata:
        return None

    for project in metadata.get("projects", []):
        for issue_type in project.get("issuetypes", []):
            for field_key, field in issue_type.get("fields", {}).items():
                if field.get("name") == field_name:
                    return field_key

    return None


def create_jira_issue(summary, description, issue_type=None, extra_fields=None):
    if not jira_is_configured():
        return {
            "success": False,
            "error": "Jira not configured. Set JIRA_BASE_URL, JIRA_API_EMAIL, JIRA_API_TOKEN, and JIRA_PROJECT_KEY."
        }

    issue_type = issue_type or JIRA_ISSUE_TYPE
    fields = {
        "project": {
            "key": JIRA_PROJECT_KEY
        },
        "summary": summary,
        "description": build_adf_description(description),
        "issuetype": {
            "name": issue_type
        }
    }

    if extra_fields:
        fields.update(extra_fields)

    payload = {"fields": fields}
    url = f"{JIRA_BASE_URL.rstrip('/')}/rest/api/3/issue"
    auth = HTTPBasicAuth(JIRA_API_EMAIL, JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, auth=auth, headers=headers, timeout=20)

    if response.ok:
        issue_key = response.json().get("key")
        issue_url = f"{JIRA_BASE_URL.rstrip('/')}/browse/{issue_key}"
        return {
            "success": True,
            "issue_key": issue_key,
            "issue_url": issue_url,
            "data": response.json()
        }

    result = {
        "success": False,
        "error": response.text,
        "status_code": response.status_code
    }
    try:
        result["data"] = response.json()
    except Exception:
        pass

    return result


def format_story_description(story):
    lines = []
    description = story.get("description", "")
    if description:
        lines.append(description)

    tasks = story.get("tasks") or []
    if tasks:
        lines.append("")
        lines.append("Tasks:")
        for task in tasks:
            lines.append(f"- {task}")

    acceptance = story.get("acceptance_criteria") or []
    if acceptance:
        lines.append("")
        lines.append("Acceptance Criteria:")
        for ac in acceptance:
            lines.append(f"- {ac}")

    return "\n".join(lines).strip() or "No description provided."


def create_jira_issues_from_structure(structure):
    if not jira_is_configured():
        return {
            "success": False,
            "error": "Jira is not configured. Set JIRA_BASE_URL, JIRA_API_EMAIL, JIRA_API_TOKEN, and JIRA_PROJECT_KEY."
        }

    created = []
    epic_key = None
    epic_link_field = None

    epic_name = structure.get("epic")
    if epic_name:
        epic_meta = get_issue_metadata(JIRA_PROJECT_KEY, "Epic")
        epic_name_field = find_field_key(epic_meta, "Epic Name")
        epic_fields = {}
        if epic_name_field:
            epic_fields[epic_name_field] = epic_name

        epic_description = format_story_description({
            "description": f"Epic created from AI sprint: {epic_name}."
        })
        epic_result = create_jira_issue(epic_name, epic_description, issue_type="Epic", extra_fields=epic_fields)
        created.append(epic_result)
        if epic_result.get("success"):
            epic_key = epic_result["issue_key"]

    story_meta = get_issue_metadata(JIRA_PROJECT_KEY, "Story")
    epic_link_field = find_field_key(story_meta, "Epic Link")

    for story in structure.get("stories", []):
        story_title = story.get("title") or "Untitled Story"
        story_description = format_story_description(story)
        extra_fields = {}
        if epic_key and epic_link_field:
            extra_fields[epic_link_field] = epic_key

        story_result = create_jira_issue(story_title, story_description, issue_type="Story", extra_fields=extra_fields)
        created.append(story_result)

    successful = [item for item in created if item.get("success")]
    failed = [item for item in created if not item.get("success")]

    if successful and not failed:
        first_url = successful[0].get("issue_url")
        issue_keys = [item.get("issue_key") for item in successful]
        return {
            "success": True,
            "issue_key": issue_keys[0] if issue_keys else None,
            "issue_url": first_url,
            "issue_keys": issue_keys,
            "issues": successful,
            "message": f"Created {len(successful)} Jira issue(s)."
        }

    return {
        "success": False,
        "error": "Some Jira issues failed to create.",
        "issues": created,
        "message": "; ".join([item.get("error", "Unknown error") for item in failed])
    }