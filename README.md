# SprintOps Assistant

SprintOps Assistant is an AI-powered Agile Sprint Planning and Daily Standup Automation platform built using FastAPI, Slack, Gemini AI, and Jira Cloud. It streamlines sprint planning, automates daily standups, generates reports, and integrates directly with Jira for seamless Agile workflow management.

---

# Features

## AI Sprint Planning

* Generate Epics
* Generate User Stories
* Generate Tasks
* Generate Acceptance Criteria
* Modify Existing Sprint Plans
* AI-powered Sprint Recommendations

---

## Jira Integration

* Automatic Epic Creation
* Automatic User Story Creation
* Automatic Task Creation
* Jira Cloud Integration
* Direct Jira Redirect after Creation

---

## Slack Integration

* Interactive Daily Standup Workflow
* On Track / Blocked Status Buttons
* AI-guided Standup Conversation
* Daily Status Tracking
* Historical Standup Records
* Open Blocker Tracking
* Slack Home Dashboard
* AI Assistant Launch Commands

---

## Standup Reports

SprintOps automatically stores every completed standup and generates reports.

Supported reports include:

* Today's Report
* Yesterday's Report
* Weekly Report
* Monthly Report
* Yearly Report
* Open Blocker Report

Each report includes:

* Report Date
* Submission Time
* Status
* Work Completed
* Blockers
* Support Required

---

## Downloadable Reports

SprintOps can generate downloadable Microsoft Word reports directly from Slack.

Supported downloads:

* Download Today Report
* Download Weekly Report
* Download Monthly Report
* Download Yearly Report

Generated reports include:

* SprintOps AI Report Header
* Report Generation Timestamp
* Daily Standup Details
* Report Summary
* Productivity Statistics

---

## AI Assistant

The built-in web assistant provides:

* Sprint Planning
* Sprint Modification
* AI Story Generation
* Jira Automation
* Project Planning Assistance

---

# Supported Slack Commands

## Standup

* start standup

---

## Reports

* show today report
* show yesterday update
* show weekly report
* show monthly report
* show yearly report
* show my history
* show open blockers

---

## Report Downloads

* download today report
* download weekly report
* download monthly report
* download yearly report

---

## Assistant

* launch ai assistant

---

# Sample AI Prompts

* Create a Digital Banking Platform
* Create a Hospital Management System
* Create a School ERP System
* Create an Airline Reservation System
* Create an Inventory Management System
* Create a Food Delivery Platform
* Create a Newspaper Publishing Platform
* Create a Cricket Stadium Management System

---

# Sample Sprint Modification Prompts

* Add Security Testing Tasks
* Add Docker Deployment Tasks
* Add Kubernetes Deployment
* Add Terraform Infrastructure
* Add AWS Deployment Tasks
* Add Monitoring and Logging
* Improve Acceptance Criteria
* Add OAuth Support

---

# Technology Stack

* FastAPI
* Python
* Slack SDK
* Google Gemini AI
* Jira Cloud API
* Microsoft Word (python-docx)
* Render
* JSON-based Local Memory Storage

---

# Project Structure

```
app/
│
├── main.py
├── bot.py
├── memory.py
├── jira.py
├── slack_blocks.py
├── reports/
│   └── report_generator.py
│
├── templates/
├── static/
└── generated_reports/
```

---

# Deployment

1. Configure Render Environment Variables
2. Configure Slack Application
3. Configure Slack Bot Token
4. Configure Jira Credentials
5. Deploy FastAPI Application
6. Install or Reinstall the Slack App
7. Start using SprintOps Assistant

---

# Environment Variables

```
GOOGLE_API_KEY

SLACK_BOT_TOKEN

JIRA_BASE_URL

JIRA_API_EMAIL

JIRA_API_TOKEN

JIRA_PROJECT_KEY
```

---

# Current Capabilities

* AI Sprint Planning
* AI Sprint Modification
* Jira Epic Creation
* Jira Story Creation
* Jira Task Creation
* Interactive Slack Standups
* Standup Session Tracking
* Daily Report Generation
* Weekly Report Generation
* Monthly Report Generation
* Yearly Report Generation
* Historical Report Tracking
* Open Blocker Reporting
* Downloadable Word Reports
* AI Assistant Dashboard

---

# Future Enhancements

* PDF Report Generation
* Team Productivity Dashboard
* AI Standup Summaries
* Email Report Delivery
* Calendar Integration
* Team Analytics
* Burndown Insights
* Automatic Blocker Notifications

---

# Status

**Production Ready**

SprintOps Assistant is a fully functional AI-powered Agile Sprint Planning and Standup Automation platform with Jira integration, Slack automation, downloadable reports, and AI-assisted sprint management.
