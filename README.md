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

## 🏗️ Architecture

```text
                                  ┌─────────────────┐
                                  │      USER       │
                                  └────────┬────────┘
                                           │
                                  ┌────────▼────────┐
                                  │   Flask Web UI  │
                                  └────────┬────────┘
                                           │
                                  ┌────────▼────────┐
                                  │    agent.py     │
                                  └────┬──────┬─────┘
                                       │      │
            ┌──────────────────────────┘      └──────────────────────────┐
            │                                                            │
    ┌───────▼───────┐                                            ┌───────▼───────┐
    │   queries.py  │                                            │   gemini.py   │
    └───────┬───────┘                                            └───────┬───────┘
            │                                                            │
    ┌───────▼───────┐                                            ┌───────▼───────┐
    │     CORAL     │                                            │   Gemini API  │
    └────┬──────┬───┘                                            └───────────────┘
         │      │
    ┌────▼───┐  └────▼────────┐
    │ GitHub │       │ Sentry │
    └────────┘       └────────┘
```

---

## 💎 Why CALYPSO Wins
CALYPSO isn't just another dashboard; it's a reasoning engine built for the heat of production incidents.

- **🚢 Cross-Source Investigation**: The only tool that joins Sentry's fatal errors with GitHub's commit stream using standard SQL.
- **🧠 AI Reasoning**: Powered by Google's Gemini Flash, CALYPSO doesn't just show data—it analyzes correlations to suggest specific root causes.
- **🛰️ Telemetry First**: Every investigation shows you the exact Coral SQL queries executed, bringing transparency to AI actions.
- **💾 Persistence**: Built-in SQLite database tracks all past investigations for easy post-mortem reviews.
- **📢 Slack Integration**: Instant report sharing to keep the entire team in the loop.
- **☁️ Docker Ready**: Fully containerized and optimized to run on a lightweight 2GB RAM instance.

---

## 🌊 The Problem

When production breaks at 3am, engineers open **5 different tabs**:

```
GitHub    →  what was just deployed?
Sentry    →  what errors are firing?
Slack     →  what did the team say?
Datadog   →  what do the metrics say?
Brain     →  what do I actually do now?
```

That context-switching costs **precious minutes** during an incident.  
CALYPSO collapses all of it into **one SQL query and one AI report.**

---

## ⚡ How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                        CALYPSO                              │
│                                                             │
│  1. You paste an alert description                          │
│  2. Coral queries GitHub + Sentry via real SQL              │
│  3. Gemini AI correlates commits with errors                │
│  4. You get a full incident report in ~30 seconds           │
└─────────────────────────────────────────────────────────────┘
```

### ⚡ How Coral Powers CALYPSO
CALYPSO uses **Coral's SQL interface** to query multiple data sources as if they were local tables. Here are the real queries driving our analysis:

#### 1. The Cross-Source Join (The "Aha!" Moment)
We join GitHub commits with Sentry issues based on temporal overlap:
```sql
SELECT c.sha, c.commit__message, s.title as sentry_error
FROM github.commits c
JOIN sentry.issues s ON s.first_seen >= c.commit__author__date
WHERE c.owner = 'Yashmko' AND c.repo = 'calypso' AND s.level = 'fatal'
ORDER BY s.first_seen DESC LIMIT 10;
```

#### 2. The Unified Incident Timeline
We use `UNION ALL` to create a chronological stream of disparate events:
```sql
SELECT 'commit' as type, commit__author__date as ts, commit__message as msg
FROM github.commits
UNION ALL
SELECT 'error' as type, first_seen as ts, title as msg
FROM sentry.issues
ORDER BY ts DESC LIMIT 20;
```

#### 3. Multi-Repo Comparison
Comparing health across different services during a global outage:
```sql
SELECT 'repo-a' as repository, sha, commit__message as msg, commit__author__date as ts
FROM github.commits WHERE owner = 'org' AND repo = 'repo-a'
UNION ALL
SELECT 'repo-b' as repository, sha, commit__message as msg, commit__author__date as ts
FROM github.commits WHERE owner = 'org' AND repo = 'repo-b'
ORDER BY ts DESC LIMIT 10;
```

### Full Data Flow

```
  Alert Description (user input)
           │
           ▼
     ┌──────────┐
     │ agent.py │  ← orchestrates everything
     └────┬─────┘
          │
     ┌────▼──────────────────────────────────────────┐
     │              queries.py                       │
     │                                               │
     │   coral sql --format json "SELECT ..."        │
     │              │              │                 │
     │       ┌──────▼──────┐ ┌────▼──────┐           │
     │       │   GitHub    │ │  Sentry   │           │
     │       │  · commits  │ │  · issues │           │
     │       │  · PRs      │ │  · errors │           │
     │       │  · alerts   │ │  · fatal  │           │
     │       └──────┬──────┘ └────┬──────┘           │
     │              │             │                  │
     │              └──────┬──────┘                  │
     │                     │  JOIN + UNION ALL       │
     │                     ▼                         │
     │             combined evidence                 │
     └─────────────────────┬─────────────────────────┘
                           │
                    ┌──────▼───────┐
                    │  gemini.py   │  ← AI analysis
                    │              │
                    │  Prompt →    │
                    │  Gemini API  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  report.py   │  ← format & structure
                    └──────┬───────┘
                           │
                           ▼
               ┌───────────────────────┐
               │   Incident Report     │
               │  · Summary            │
               │  · Root Cause         │
               │  · Affected Systems   │
               │  · Action Plan        │
               │  · Prevention         │
               └───────────────────────┘
```

---

## ✨ Features

| Feature | What It Does | Coral Superpower Used |
|---|---|---|
| 🔍 **Incident Investigator** | Full AI report from one alert | Parallel queries across sources |
| 🕒 **Evidence Timeline** | Commits + errors in one stream | `UNION ALL` across GitHub + Sentry |
| ⚔️ **Multi-Repo Comparison** | Compare two repos side by side | Cross-repo `UNION ALL` query |
| 👁️ **Query Viewer** | See exact SQL + execution time | Full Coral transparency |
| 📜 **Live Query History** | Terminal of last 5 SQL executions | Real-time Coral telemetry |
| 🟢 **Source Status Badges** | Live GitHub + Sentry ping on load | Lightweight health-check queries |
| 💬 **Follow-up Chat** | Ask the agent follow-up questions | Contextual AI over Coral results |
| 🛠️ **Create Fix Issue** | One-click GitHub Issue from report | Closes the investigation loop |

---

## 🗂️ Project Structure

```
calypso/
│
├── 🧠  agent.py              # Main orchestrator
├── 🔌  queries.py            # All Coral SQL (real subprocess calls)
├── 🤖  gemini.py             # Gemini 1.5 Flash integration
├── 📋  report.py             # JSON report formatter
├── 🌐  app.py                # Flask server (port 5000)
│
├── templates/
│   └── 🎨  index.html        # Dark UI — Tailwind CDN, vanilla JS
│
├── .env                      # Your secrets (never committed)
├── .env.example              # Template for others
├── .gitignore                # Keeps .env safe
├── requirements.txt          # flask, google-generativeai, python-dotenv
├── README.md                 # You are here
└── SUBMISSION.md             # Hackathon submission copy
```

---

## 🔥 The Coral SQL

Every piece of data in CALYPSO flows through real `coral sql` subprocess calls.  
No mock data. No hardcoded JSON. Real SQL. Real results.

### Sentry Issues
```sql
SELECT title, culprit, level, status, first_seen, last_seen
FROM sentry.issues
WHERE level IN ('error', 'fatal')
ORDER BY last_seen DESC
LIMIT 10
```

### Recent GitHub Commits
```sql
SELECT sha, commit__message, author__login, html_url, created_at
FROM github.commits
WHERE owner = :owner AND repo = :repo
ORDER BY commit__author__date DESC
LIMIT 10
```

### 🏆 Cross-Source JOIN — The Money Shot
```sql
SELECT
    c.sha,
    c.commit__message,
    c.author__login,
    s.title      AS sentry_error,
    s.level      AS severity,
    s.first_seen AS error_time,
    c.created_at AS commit_time
FROM github.commits c
JOIN sentry.issues s
  ON s.first_seen >= c.created_at
WHERE s.level = 'fatal'
ORDER BY s.first_seen DESC
LIMIT 10
```

### Evidence Timeline — UNION ALL
```sql
SELECT 'commit' AS type, sha    AS id, commit__message AS message, created_at  AS ts
FROM github.commits
WHERE owner = :owner AND repo = :repo

UNION ALL

SELECT 'error'  AS type, id,          title           AS message, first_seen   AS ts
FROM sentry.issues
WHERE level IN ('error', 'fatal')

ORDER BY ts DESC
LIMIT 20
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Coral CLI](https://withcoral.com) installed
- GitHub source connected → `coral source add --interactive github`
- Sentry source connected → `coral source add --interactive sentry`
- Gemini API key → [aistudio.google.com](https://aistudio.google.com) (free, no credit card)

### Install & Run

```bash
# Clone
git clone https://github.com/Yashmko/calypso.git
cd calypso

# Install
pip install -r requirements.txt --break-system-packages

# Configure
cp .env.example .env
nano .env   # add your GEMINI_API_KEY

# Launch
python app.py

# Open
# http://localhost:5000
```

### Environment Variables

| Variable | Required | Where to Get |
|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | [aistudio.google.com](https://aistudio.google.com/app/apikey) |

---

## 🎮 Using CALYPSO

```
Step 1 → Open http://localhost:5000
Step 2 → Enter your GitHub repo (owner/repo)
Step 3 → Optionally enter a second repo for comparison
Step 4 → Paste your alert or incident description
Step 5 → Hit Investigate (or Ctrl+Enter)
Step 6 → Read the 5-section incident report
Step 7 → Click "View Coral Query" to see live SQL
Step 8 → Ask follow-up questions in the chat
Step 9 → Click "Create Fix Issue" to log it in GitHub
```

---

## 🏗️ Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Query Engine | Coral CLI | SQL over GitHub + Sentry, no ETL |
| AI | Gemini 1.5 Flash | Free tier, fast, excellent reasoning |
| Backend | Python + Flask | Lightweight, 2GB RAM friendly |
| Frontend | HTML + Tailwind CDN + Vanilla JS | Zero npm, zero build step |
| OS | Arch Linux | Because we don't need more |

---

## 📊 API Reference

### `POST /investigate`

**Request:**
```json
{
  "alert": "Database timeout errors spiking in production API",
  "owner": "your-org",
  "repo": "your-repo",
  "compare_repo": "your-org/other-repo"
}
```

**Response:**
```json
{
  "timestamp": "2026-05-25T03:00:00+00:00",
  "ai_analysis": "## Incident Summary\n...",
  "stats": {
    "sentry_issues_found": 8,
    "github_commits_analyzed": 10,
    "security_alerts_found": 2,
    "open_prs_found": 3,
    "cross_source_correlations": 4
  },
  "query_log": [
    {
      "sql": "SELECT title FROM sentry.issues ...",
      "duration_ms": 312
    }
  ],
  "raw_data": {}
}
```

### `GET /status`
Returns live Coral source connectivity for the header badges.

```json
{
  "github": "connected",
  "sentry": "connected"
}
```

---

## 🏆 Why CALYPSO Wins

| Judging Criterion | What CALYPSO Delivers |
|---|---|
| 🎯 **Impact** | Solves on-call incident investigation — every eng team's pain |
| 🧠 **Creativity** | Named after a sea goddess, fits pirate theme, cross-source SQL joins |
| ⚙️ **Technical Depth** | Real subprocess Coral calls, UNION ALL, JOIN, live telemetry |
| 🎨 **Aesthetics** | Glassmorphism dark UI, typewriter SQL terminal, smooth animations |
| 🔗 **Best Use of Coral** | Query viewer, live history, source badges — Coral is the star |
| 📈 **Learning Curve** | Solo, 2GB RAM, Arch Linux, all free tools — built it anyway |

---

## 🧑‍💻 The Builder

Built solo by **[@Yashmko](https://github.com/Yashmko)** on a **2GB RAM Arch Linux laptop.**

No paid subscriptions. No cloud services. No team.  
Just Coral, Python, and stubbornness.

> *"If it runs on my machine, it runs anywhere. That's the point of Coral."*

---

## 📄 License

MIT — use it, fork it, ship it.

---

<div align="center">

🏴‍☠️ **CALYPSO** · Built for the Pirates of the Coral-bean Hackathon · WeMakeDevs · May 2026

*She knows the waters. She sees the wrecks. She tells you what broke before you even ask.*

</div>
