# UPDATED `README.md`

````md
# AI Sprint Planning Assistant

AI-powered Agile Sprint Planning Assistant integrated with:

- Slack
- Jira
- Gemini/OpenAI
- FastAPI
- Render Deployment

The application allows users to:

- Generate Epics
- Generate User Stories
- Generate Tasks
- Generate Acceptance Criteria
- Automatically create real Jira tickets
- Launch AI Assistant directly from Slack
- Redirect directly to created Jira issues

---

# Architecture

```text
Slack App
   ↓
Launch AI Assistant
   ↓
AI Prompt UI
   ↓
Gemini/OpenAI Sprint Generation
   ↓
Automatic Jira Ticket Creation
   ↓
Redirect to Real Jira Issue
````

---

# Features

## Slack Integration

* Slack Home Tab
* AI Assistant Launch Button
* Slack Slash Command Support
* Slack Bot Messages

## Jira Integration

* Real Jira Ticket Creation
* Epic Creation
* Story Creation
* Auto Redirect to Jira Issue

## AI Features

* Sprint Planning
* Epic Generation
* Story Generation
* Acceptance Criteria Generation
* Story Points Estimation
* AI Sprint Modification

---

# Tech Stack

* FastAPI
* Jinja2
* Slack SDK
* Jira REST API
* Gemini / OpenAI
* Render

---

# Local Setup

## Clone Repository

```bash
git clone <YOUR_REPO_URL>
cd sre-main
```

---

# Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Create `.env`

```env
GOOGLE_API_KEY=your_google_api_key

JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_jira_email
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=SJA

SLACK_BOT_TOKEN=xoxb-xxxxxxxx
SLACK_SIGNING_SECRET=xxxxxxxx

BASE_URL=https://your-render-app.onrender.com
```

---

# Run Locally

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

---

# Render Deployment

## Step 1 — Push Code To GitHub

```bash
git add .
git commit -m "production deployment"
git push origin main
```

---

## Step 2 — Create Render Account

Open:

```text
https://render.com
```

Login using GitHub.

---

## Step 3 — Create Web Service

Click:

```text
New +
```

Then:

```text
Web Service
```

Select your GitHub repo.

---

## Step 4 — Configure Render

### Name

```text
ai-sprint-planner
```

### Environment

```text
Python 3
```

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

---

# Step 5 — Add Environment Variables

Inside Render Dashboard:

```text
Environment
```

Add:

```env
GOOGLE_API_KEY=your_google_api_key

JIRA_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_jira_email
JIRA_API_TOKEN=your_jira_api_token
JIRA_PROJECT_KEY=SJA

SLACK_BOT_TOKEN=xoxb-xxxxxxxx
SLACK_SIGNING_SECRET=xxxxxxxx

BASE_URL=https://your-render-app.onrender.com
```

---

# Step 6 — Deploy

Click:

```text
Create Web Service
```

Wait until deployment completes.

You will get:

```text
https://your-render-app.onrender.com
```

---

# Slack Configuration

Open:

```text
https://api.slack.com/apps
```

Select your app.

---

# Event Subscriptions

Enable Events.

Request URL:

```text
https://your-render-app.onrender.com/slack/events
```

Add Bot Event:

```text
app_home_opened
```

---

# OAuth & Permissions

Add Bot Scopes:

```text
app_home:read
app_home:write
chat:write
commands
im:history
im:read
im:write
```

Then:

```text
Reinstall to Workspace
```

---

# App Home

Enable:

* Home Tab
* Messages Tab

---

# Final Production Flow

```text
Slack-Int Home
    ↓
Launch AI Assistant
    ↓
Enter Prompt
    ↓
AI Generates Sprint
    ↓
Real Jira Issues Created
    ↓
Automatic Redirect To Jira Ticket
```

---

# Example Prompt

```text
Create user stories for weather forecasting application
```


# DEPLOYMENT GUIDE FROM SCRATCH

## 1. Push Latest Code

Run:

```bash
git add .
git commit -m "final production deployment"
git push origin main
````

---

## 2. Create `requirements.txt`

If missing:

```bash
pip freeze > requirements.txt
```

Make sure these exist:

```text
fastapi
uvicorn
jinja2
python-dotenv
slack-sdk
google-generativeai
requests
python-multipart
```

---

## 3. Render Deployment

Open:

```text
https://render.com
```

### Click:

```text
New + → Web Service
```

### Connect GitHub repo.

---

## 4. Render Settings

### Runtime

```text
Python 3
```

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

---

## 5. Add ENV Variables

Render Dashboard → Environment:

```env
GOOGLE_API_KEY=
JIRA_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=
JIRA_PROJECT_KEY=
SLACK_BOT_TOKEN=
SLACK_SIGNING_SECRET=
BASE_URL=https://your-render-app.onrender.com
```

---

## 6. Deploy

Click:

```text
Create Web Service
```

Wait for:

```text
Live
```

status.

---

## 7. Configure Slack

Open:

```text
https://api.slack.com/apps
```

### Event Subscription URL

```text
https://your-render-app.onrender.com/slack/events
```

### Add Event

```text
app_home_opened
```

### Reinstall App

```text
OAuth & Permissions → Reinstall
```

---

# FINAL RESULT

Production App Flow:

```text
Slack App
↓
Launch AI Assistant
↓
Prompt
↓
AI Generates Sprint
↓
Real Jira Ticket Created
↓
Redirect To Jira Issue
```
