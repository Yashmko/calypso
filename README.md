<div align="center">

```
 ██████╗ █████╗ ██╗  ██╗   ██╗██████╗ ███████╗ ██████╗ 
██╔════╝██╔══██╗██║  ╚██╗ ██╔╝██╔══██╗██╔════╝██╔═══██╗
██║     ███████║██║   ╚████╔╝ ██████╔╝███████╗██║   ██║
██║     ██╔══██║██║    ╚██╔╝  ██╔═══╝ ╚════██║██║   ██║
╚██████╗██║  ██║███████╗██║   ██║     ███████║╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝     ╚══════╝ ╚═════╝ 
```

*She knows the waters. She sees the wrecks.*  
*She tells you what broke before you even ask.*

<br/>

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![Coral](https://img.shields.io/badge/Powered_by-Coral_SQL-FF6B4A?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Gemini-1.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![Track](https://img.shields.io/badge/Track_1-Enterprise_Agent_🏴‍☠️-gold?style=for-the-badge)
![RAM](https://img.shields.io/badge/Runs_on-2GB_RAM-success?style=for-the-badge)

<br/>

> **Built for the [Pirates of the Coral-bean Hackathon](https://www.wemakedevs.org/hackathons/coral) by WeMakeDevs**  
> Track 1 · Enterprise Agent · MacBook Neo Target 🎯

</div>


---

# 🚀 CALYPSO

**AI-Powered Enterprise Incident Investigation Engine**

She knows the waters. She sees the wrecks.  
She tells you what broke before you even ask.

<br/>

**🌐 Live Demo:** https://calypso-bre2.onrender.com/  
**📦 GitHub Repository:** https://github.com/Yashmko/calypso  
**🏴‍☠️ Track:** Pirates of the Coral-bean Hackathon · WeMakeDevs · Enterprise Agent

</div>

---

## ⚡ What is CALYPSO?

CALYPSO is an AI-powered incident investigation platform built to help engineering teams reduce Mean Time To Resolution (MTTR).

Instead of manually jumping between GitHub, Sentry, logs, deployment history, and telemetry dashboards, CALYPSO correlates the evidence for you and generates a structured investigation report.

It helps teams answer the questions that matter most during an incident:

- What changed?
- What broke?
- Which commit likely caused it?
- What evidence supports that conclusion?
- What should we do next?

CALYPSO transforms fragmented operational data into a single investigation workflow.

---

## 🚨 The Problem

When production breaks, engineers waste time switching between tools.

GitHub tells you what changed.  
Sentry tells you what failed.  
Slack tells you what people said.  
Logs tell you fragments.  
Your brain tries to connect the rest.

That context switching costs precious minutes during a real incident.

CALYPSO collapses those signals into one AI-assisted incident investigation flow.

---

## 🌊 Why CALYPSO Matters

Most tools show data.

CALYPSO investigates.

It combines Coral-powered retrieval, Gemini reasoning, and a clean investigation interface to produce:

- Root Cause Analysis
- Incident Timelines
- Confidence Scoring
- Affected Components
- Recommended Actions
- Prevention Plans
- Investigation History
- Follow-up AI Chat

It is designed for real engineering workflows, not just pretty dashboards.

---

## 🌐 Live Production Deployment

CALYPSO is publicly deployed and accessible here:

**https://calypso-bre2.onrender.com/**

This live deployment demonstrates:

- End-to-end incident investigation
- AI-generated root cause analysis
- Cross-source evidence correlation
- Timeline reconstruction
- Investigation history
- Follow-up chat
- Enterprise-style reporting

---

## 🧠 How CALYPSO Works

```text
Alert / Incident Description
          ↓
       Flask UI
          ↓
       agent.py
      /        \
queries.py    gemini.py
     ↓            ↓
   Coral        Gemini API
     ↓
 GitHub + Sentry data
          ↓
   report.py formats output
          ↓
   Investigation report in UI
```

### High-Level Flow

1. The user enters an alert or incident description.
2. `agent.py` coordinates the investigation.
3. `queries.py` runs Coral SQL queries against connected sources.
4. Coral retrieves evidence from GitHub and Sentry.
5. `gemini.py` analyzes the evidence and generates reasoning.
6. `report.py` formats the output into a structured incident report.
7. The frontend displays the analysis, timeline, query logs, and history.

## 🔥 How Coral Powers CALYPSO

Coral is the investigation data layer of CALYPSO.

It lets the platform query engineering sources as if they were local tables, which means CALYPSO can correlate commits, errors, timelines, and service signals without manual digging.

### Coral is used for:

* Cross-source joins between GitHub and Sentry
* Unified incident timelines
* Source status checks
* Transparent query execution
* Investigation telemetry
* Live evidence retrieval

### Example Coral Queries

#### 1. Cross-Source Join

```sql
SELECT c.sha, c.commit__message, s.title as sentry_error
FROM github.commits c
JOIN sentry.issues s ON s.first_seen >= c.commit__author__date
WHERE c.owner = 'Yashmko' AND c.repo = 'calypso' AND s.level = 'fatal'
ORDER BY s.first_seen DESC
LIMIT 10;
```

#### 2. Unified Incident Timeline

```sql
SELECT 'commit' as type, commit__author__date as ts, commit__message as msg
FROM github.commits

UNION ALL

SELECT 'error' as type, first_seen as ts, title as msg
FROM sentry.issues

ORDER BY ts DESC
LIMIT 20;
```

#### 3. Multi-Repo Comparison

```sql
SELECT 'repo-a' as repository, sha, commit__message as msg, commit__author__date as ts
FROM github.commits
WHERE owner = 'org' AND repo = 'repo-a'

UNION ALL

SELECT 'repo-b' as repository, sha, commit__message as msg, commit__author__date as ts
FROM github.commits
WHERE owner = 'org' AND repo = 'repo-b'

ORDER BY ts DESC
LIMIT 10;
```

Coral provides the evidence.

Gemini provides the reasoning.

CALYPSO turns both into a usable investigation workflow.

---

## ✨ Key Features

### 🤖 AI Root Cause Analysis

Generates structured incident reports from a single alert.

### 🕒 Evidence Timeline

Combines commits and errors into one chronological view.

### 📊 Confidence Scoring

Scores the strength of the evidence and reasoning.

### 🔍 GitHub Correlation

Detects relevant commits and recent code changes.

### 👁️ Live Coral SQL Telemetry

Lets you inspect the exact queries used during an investigation.

### 💾 Investigation History

Stores and reloads previous investigations.

### 💬 Follow-up AI Chat

Ask questions after the initial report is generated.

### 📢 Slack Integration

Broadcasts reports to the team when needed.

### 🌐 Public Deployment

Available online through Render.

## 🧩 Project Structure

```text id="j95kzv"
calypso/
├── agent.py              # Main investigation orchestrator
├── queries.py            # Coral SQL execution and source queries
├── gemini.py             # Gemini integration and fallback logic
├── report.py             # Report formatting and Slack formatting
├── db.py                 # SQLite persistence layer
├── app.py                # Flask web server
├── templates/
│   └── index.html        # Frontend UI
├── sample_incidents.json # Demo incident scenarios
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore            # Secret protection
└── README.md             # You are here
```

## 🛠️ Tech Stack

| Layer        | Choice                           | Why                                     |
| ------------ | -------------------------------- | --------------------------------------- |
| Query Engine | Coral CLI                        | SQL over GitHub + Sentry, no ETL        |
| AI           | Gemini API                       | Fast reasoning and report generation    |
| Backend      | Python + Flask                   | Lightweight and hackathon-friendly      |
| Frontend     | HTML + Tailwind CDN + Vanilla JS | Zero build step, fast iteration         |
| Persistence  | SQLite                           | Simple local storage for investigations |
| Deployment   | Render                           | Clean production deployment             |
| OS           | Arch Linux                       | Because chaos builds character          |

## 🚀 Quick Start

### Prerequisites

* Python 3.8+
* Coral CLI installed and connected
* GitHub source connected
* Sentry source connected
* Gemini API key

### Install

```bash id="k7vfhs"
git clone https://github.com/Yashmko/calypso.git
cd calypso
pip install -r requirements.txt
```

### Configure

```bash id="v1hkjw"
cp .env.example .env
nano .env
```

Add:

```env id="5rxb52"
GEMINI_API_KEY=your_gemini_api_key
SLACK_WEBHOOK_URL=your_slack_webhook_url
FLASK_SECRET_KEY=your_random_secret
```

### Run

```bash id="y6s94x"
python app.py
```

Open:

```text id="8l6g89"
http://localhost:5000
```

## 🔐 Environment Variables

| Variable          | Required | Description                   |
| ----------------- | -------- | ----------------------------- |
| GEMINI_API_KEY    | ✅ Yes    | Gemini API key                |
| GOOGLE_API_KEY    | Optional | Alternate Gemini key name     |
| SLACK_WEBHOOK_URL | Optional | Sends reports to Slack        |
| FLASK_SECRET_KEY  | ✅ Yes    | Flask session/security secret |
| SENTRY_DSN        | Optional | Sentry integration            |

## 🎮 Using CALYPSO

1. Open the app.
2. Enter your GitHub repo in `owner/repo` format.
3. Optionally enter a second repo for comparison.
4. Paste your alert or incident description.
5. Hit **Analyze Incident** or press **Ctrl + Enter**.
6. Read the investigation report.
7. Inspect the timeline and Coral SQL telemetry.
8. Ask follow-up questions in the chat tab.
9. Share or export the report as needed.

## 📊 API Reference

### POST `/investigate`

#### Request

```json id="7zb1tp"
{
  "alert": "Database timeout errors spiking in production API",
  "repo": "your-org/your-repo",
  "compare_repo": "your-org/other-repo"
}
```

#### Response

```json id="g9a4cf"
{
  "timestamp": "2026-05-25T03:00:00+00:00",
  "evidence_score": 85
}
```

### GET `/status`

```json id="ov9p1y"
{
  "github": "connected",
  "sentry": "connected"
}
```

## 🏆 Why CALYPSO Stands Out

| Judging Criterion    | What CALYPSO Delivers                       |
| -------------------- | ------------------------------------------- |
| 🎯 Impact            | Reduces incident investigation time         |
| 🧠 Creativity        | Sea-themed AI investigation engine          |
| ⚙️ Technical Depth   | Real Coral SQL, joins, timelines, telemetry |
| 🎨 Aesthetics        | Modern investigation dashboard              |
| 🔗 Best Use of Coral | Coral is the center of the workflow         |
| 📈 Practical Value   | Useful for real engineering teams           |

## 📸 Screenshots

> Add screenshots before final submission.

```markdown id="0w6jxl"
![Dashboard](screenshots/dashboard.png)
![Report](screenshots/report.png)
![Timeline](screenshots/timeline.png)
![SQL](screenshots/sql.png)
```

## 👨‍💻 Builder

Built solo by **@Yashmko**.

No giant team.
No expensive infrastructure.
Just Coral, Python, Flask, Gemini, and persistence.

## 📄 License

MIT License.

## 🏴‍☠️ Final Note

CALYPSO is an AI-powered incident investigation engine that transforms fragmented operational data into actionable reasoning.

*She knows the waters. She sees the wrecks. She tells you what broke before you even ask.*
you even ask.*

</div>
