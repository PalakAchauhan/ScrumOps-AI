# Installation Guide

## Prerequisites

Make sure the following are installed before running the project:

* Python 3.10 or above
* Git
* Slack Workspace
* Slack App
* Jira Cloud Account
* Google Gemini API Key

---

## Clone the Repository

```bash
git clone https://github.com/<your-username>/SprintOps-Assistant.git
cd SprintOps-Assistant
```

---

## Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the project root and add the following:

```env
GOOGLE_API_KEY=your_gemini_api_key

SLACK_BOT_TOKEN=xoxb-your-slack-bot-token

JIRA_BASE_URL=https://your-domain.atlassian.net

JIRA_API_EMAIL=your_email@example.com

JIRA_API_TOKEN=your_jira_api_token

JIRA_PROJECT_KEY=PROJECTKEY
```

---

## Configure Slack App

1. Create a Slack App.
2. Enable Event Subscriptions.
3. Enable Interactivity.
4. Add the required Bot Token Scopes:

   * chat:write
   * chat:write.public
   * files:read
   * files:write
   * channels:history
   * channels:read
   * groups:history
   * groups:read
   * im:history
   * im:read
   * mpim:read
   * users:read
5. Install or Reinstall the app to your workspace.

---

## Configure Jira

Create an API Token from Atlassian and configure:

* Jira Base URL
* API Email
* API Token
* Project Key

---

## Run the Application

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```
http://127.0.0.1:8000
```

---

## Deploy to Render

1. Push the project to GitHub.
2. Create a new Web Service in Render.
3. Connect your GitHub repository.
4. Set the Build Command:

```bash
pip install -r requirements.txt
```

5. Set the Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

6. Add all required environment variables in Render.
7. Deploy the application.

---

## Verify the Deployment

Once deployed, test the following commands in Slack:

* start standup
* show today report
* show weekly report
* show monthly report
* show yearly report
* download today report
* download weekly report
* launch ai assistant

If all commands execute successfully, SprintOps Assistant is ready to use.
