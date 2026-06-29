# Project Architecture

                               +----------------------+
                               |      Slack User      |
                               +----------+-----------+
                                          |
                                          |
                             Slack Events / Commands
                                          |
                                          v
                          +-------------------------------+
                          |       SprintOps Assistant      |
                          |        FastAPI (main.py)       |
                          +---------------+----------------+
                                          |
            -----------------------------------------------------------------
            |                       |                       |                |
            |                       |                       |                |
            v                       v                       v                v
+--------------------+   +--------------------+   +----------------+  +------------------+
|    memory.py       |   |      bot.py        |   | slack_blocks.py|  |     jira.py      |
| Session & Reports  |   | Gemini AI Engine   |   | Slack UI Blocks|  | Jira Integration |
+---------+----------+   +---------+----------+   +-------+--------+  +--------+---------+
          |                          |                      |                    |
          |                          |                      |                    |
          |                          |                      |                    |
          |                          |                      |                    |
          v                          |                      |                    |
+----------------------+             |                      |                    |
| Local JSON Storage   |             |                      |                    |
| Daily Standups       |             |                      |                    |
| Report History       |             |                      |                    |
+----------+-----------+             |                      |                    |
           |                         |                      |                    |
           |                         |                      |                    |
           v                         v                      |                    |
+---------------------------+   +----------------------+    |                    |
| report_generator.py       |   | AI Sprint Planner    |    |                    |
| DOCX Report Generation    |   | (Gemini AI)          |    |                    |
+------------+--------------+   +----------+-----------+    |                    |
             |                             |                |                    |
             |                             |                |                    |
             v                             v                |                    |
+---------------------------+    +----------------------+    |                    |
| Downloadable DOCX Reports |    | Sprint Structure    |    |                    |
+------------+--------------+    | (Epics, Stories,    |    |                    |
             |                   | Tasks, Acceptance)  |    |                    |
             |                   +----------+-----------+    |                    |
             |                              |                |                    |
             |                              |                |                    |
             +------------------------------+----------------+                    |
                                            |                                     |
                                            v                                     |
                                   +----------------------+                       |
                                   |    Jira Cloud API    |<----------------------+
                                   +----------+-----------+
                                              |
                                              |
                                              v
                                  +---------------------------+
                                  | Epic / Story / Task       |
                                  | Created in Jira           |
                                  +---------------------------+
```

## Architecture Flow

### Standup & Reporting Workflow

1. User starts a standup from Slack.
2. FastAPI receives the Slack event.
3. Interactive standup questions are displayed.
4. User responses are stored in `memory.py`.
5. Standup history is saved in local JSON storage.
6. Reports (Today, Weekly, Monthly, Yearly) are generated.
7. `report_generator.py` creates downloadable DOCX reports.
8. Reports are uploaded back to Slack.

### AI Sprint Planning Workflow

1. User opens the AI Assistant.
2. Sprint requirements are entered.
3. `bot.py` uses Gemini AI to generate:

   * Epics
   * User Stories
   * Tasks
   * Acceptance Criteria
4. The generated sprint structure is sent to `jira.py`.
5. Jira Cloud APIs create Epics, Stories, and Tasks automatically.
6. Users are redirected to the newly created Jira project for further management.
