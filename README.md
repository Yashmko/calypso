<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:000000,100:1a1a1a&height=120&section=header&text=CALYPSO&fontSize=52&fontColor=ffffff&fontAlignY=65&animation=fadeIn&desc=She%20knows%20the%20waters.%20She%20sees%20the%20wrecks.&descAlignY=85&descSize=14&descColor=888888"/>

<br/>

**The incident is already over by the time most teams open their first tab.**  
**CALYPSO opened all of them before you even typed the alert.**

<br/>

[![Python](https://img.shields.io/badge/Python_3.10+-black?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-black?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Coral](https://img.shields.io/badge/Powered_by_Coral_SQL-black?style=flat-square)](https://withcoral.com)
[![Gemini](https://img.shields.io/badge/Gemini_1.5_Flash-black?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com)
[![Track](https://img.shields.io/badge/Track_1_Enterprise_Agent-black?style=flat-square)](https://wemakedevs.org/hackathons/coral)
[![Live](https://img.shields.io/badge/Live_Demo-online-black?style=flat-square)](https://calypso-bre2.onrender.com)

<br/>

### [→ Live Demo](https://calypso-bre2.onrender.com) &nbsp;·&nbsp; [→ GitHub](https://github.com/Yashmko/calypso) &nbsp;·&nbsp; [→ Hackathon](https://wemakedevs.org/hackathons/coral)

<br/>

</div>

---

## The problem nobody talks about

Every post-mortem says the same thing.

> *"We spent 40 minutes figuring out what happened before we could even start fixing it."*

GitHub. Sentry. Slack. Logs. Dashboards. Five tabs. One incident. Zero correlation.

The tools exist. The data exists. The connection between them doesn't — until someone manually builds it at 3am while the alerts are still firing.

**CALYPSO builds that connection automatically.**

One alert in. Full incident report out. In under 30 seconds.

---

## What CALYPSO actually does

You paste an alert. CALYPSO:

1. Queries your **GitHub** — what changed, who pushed, which PRs merged
2. Queries your **Sentry** — what errors fired, when, how severe
3. **JOINs them with Coral SQL** — correlates commits to errors by timestamp
4. Builds an **evidence timeline** — one chronological view of what happened
5. Sends everything to **Gemini AI** — structured root cause analysis
6. Returns a **complete investigation report** — summary, root cause, actions, prevention

What used to take 40 minutes now takes 30 seconds.

---

## Built on a 2GB RAM Arch Linux laptop

No cloud credits. No expensive hardware. No team.

Just Coral, Python, a free Gemini API key, and a machine most people would retire.

> *If it runs here, it runs anywhere. That's the whole point of Coral.*

This is not a disclaimer. This is the point.  
The constraint proved the concept.  
Lightweight by necessity. Powerful by design.

---

## The Coral SQL layer — this is the real story

Most agent projects call APIs one at a time, stitch results manually, and call it "multi-source."

CALYPSO uses **Coral as a unified SQL retrieval engine** — single queries across multiple live systems.

### The query that matters most

```sql
-- One query. Two systems. Zero glue code.
SELECT
    c.sha,
    c.commit__message,
    c.author__login,
    s.title           AS sentry_error,
    s.level           AS severity,
    s.first_seen      AS error_time,
    c.commit__author__date AS commit_time
FROM github.commits c
JOIN sentry.issues s
  ON s.first_seen >= c.commit__author__date
WHERE s.level = 'fatal'
ORDER BY s.first_seen DESC
LIMIT 10;
```

This single query replaces:
- A GitHub API call
- A Sentry API call  
- Manual pagination handling
- Custom response merging logic
- Timestamp normalization code

**Coral does all of it. CALYPSO just asks the question.**

### Unified evidence timeline

```sql
SELECT 'commit' AS type, commit__author__date AS ts, commit__message AS message
FROM github.commits WHERE owner = :owner AND repo = :repo

UNION ALL

SELECT 'error' AS type, first_seen AS ts, title AS message
FROM sentry.issues WHERE level IN ('error', 'fatal')

ORDER BY ts DESC LIMIT 20;
```

### Multi-repo comparison

```sql
SELECT 'repo-a' AS repository, sha, commit__message, commit__author__date AS ts
FROM github.commits WHERE owner = :org AND repo = 'service-a'

UNION ALL

SELECT 'repo-b' AS repository, sha, commit__message, commit__author__date AS ts
FROM github.commits WHERE owner = :org AND repo = 'service-b'

ORDER BY ts DESC LIMIT 10;
```

Every query is visible in the **Coral Telemetry** tab — execution time included.  
Nothing is mocked. Nothing is hardcoded. Everything runs live.

---

## Features

| Feature | What it does |
|---|---|
| **AI Root Cause Analysis** | Structured 5-section incident report from a single alert |
| **Evidence Timeline** | GitHub commits + Sentry errors in one chronological stream |
| **Cross-Source SQL JOIN** | Coral-powered correlation between two live systems |
| **Multi-Repo Comparison** | UNION ALL across two GitHub repos simultaneously |
| **Confidence Scoring** | Evidence-based certainty rating with MTTR estimate |
| **Coral SQL Telemetry** | Every query shown with execution time in milliseconds |
| **Investigation History** | SQLite-persisted cases, reloadable across sessions |
| **Follow-up AI Chat** | Ask questions about the current investigation context |
| **Slack Broadcast** | One-click incident report to team channel |
| **Create GitHub Issue** | Pre-fills issue with AI summary and action plan |
| **Live Source Badges** | Real-time GitHub and Sentry connectivity status |
| **Sample Incidents** | One-click demo scenarios for immediate testing |

---

## Architecture

```
Alert Description (user input)
           │
           ▼
     ┌──────────┐
     │  app.py  │  Flask · port 5000
     └────┬─────┘
          │
     ┌────▼──────────────────────────────────┐
     │              agent.py                 │
     │         Investigation Engine          │
     └──────┬─────────────────┬──────────────┘
            │                 │
     ┌──────▼──────┐   ┌──────▼───────┐
     │  queries.py │   │  gemini.py   │
     │             │   │              │
     │  coral sql  │   │  Gemini API  │
     │  subprocess │   │  1.5 Flash   │
     └──────┬──────┘   └──────┬───────┘
            │                 │
     ┌──────▼──────┐          │
     │    Coral    │          │
     │  SQL layer  │          │
     └──────┬──────┘          │
            │                 │
     ┌──────▼──────┐          │
     │  GitHub +   │          │
     │   Sentry    │          │
     └──────┬──────┘          │
            │                 │
            └────────┬────────┘
                     │
              ┌──────▼──────┐
              │  report.py  │
              │   db.py     │
              └──────┬──────┘
                     │
                     ▼
           Investigation Report
      { ai_analysis · timeline · stats
        query_log · confidence · raw_data }
```

---

## Project structure

```
calypso/
│
├── agent.py              # Investigation orchestrator
├── queries.py            # Coral SQL execution layer
├── gemini.py             # Gemini AI integration
├── report.py             # Report formatter + Slack sender
├── db.py                 # SQLite persistence
├── app.py                # Flask web server
│
├── templates/
│   └── index.html        # Minimal editorial UI
│
├── sample_incidents.json # Demo scenarios
├── requirements.txt      # Dependencies
├── .env.example          # Environment template
├── Dockerfile            # Container support
├── docker-compose.yml    # One-command startup
└── .gitignore            # Secret protection
```

---

## Quick start

```bash
# Clone
git clone https://github.com/Yashmko/calypso.git
cd calypso

# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add GEMINI_API_KEY to .env

# Connect Coral sources
coral source add --interactive github
coral source add --interactive sentry

# Run
python app.py
# → http://localhost:5000
```

### Or with Docker

```bash
docker-compose up
# → http://localhost:5000
```

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Google Gemini API key (free at aistudio.google.com) |
| `SLACK_WEBHOOK_URL` | Optional | Slack incoming webhook for broadcasts |
| `FLASK_SECRET_KEY` | ✅ | Flask session security key |

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Query engine | Coral CLI | SQL over GitHub + Sentry, no ETL, no glue |
| AI | Gemini 1.5 Flash | Fast, free tier, excellent structured reasoning |
| Backend | Python + Flask | Lightweight, 2GB RAM friendly |
| Frontend | HTML + Tailwind CDN + Vanilla JS | Zero build step, zero npm |
| Persistence | SQLite | Simple, local, reliable |
| Deployment | Render | Clean production deployment |
| Dev machine | 2GB RAM Arch Linux | Proof that constraints don't stop shipping |

---

## Why this wins

Other submissions in this hackathon likely built dashboards that call APIs and display results.

CALYPSO built something different.

**It doesn't call APIs. It asks questions.**

```sql
-- Not this:
GET /repos/owner/repo/commits
GET /organizations/org/issues

-- This:
SELECT commits, errors, correlation
FROM github JOIN sentry
WHERE the_incident_happened
```

That distinction is what Coral was built for.  
CALYPSO is proof of exactly that.

---

## Live deployment

**[https://calypso-bre2.onrender.com](https://calypso-bre2.onrender.com)**

Deployed on Render. Connected to live GitHub and Sentry sources.  
Open it. Type any alert. See it work.

---

<div align="center">

**Built solo · 2GB RAM · Arch Linux · All free tools**

*Pirates of the Coral-bean Hackathon · WeMakeDevs · May 2026*

<br/>

*She knows the waters. She sees the wrecks.*  
*She tells you what broke before you even ask.*

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1a1a,100:000000&height=80&section=footer"/>

</div>
