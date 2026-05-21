# SRE Investigator ⚡

> **Pirates of the Coral-bean Hackathon** | WeMakeDevs | Track 1: Enterprise Agent

**SRE Investigator** is an AI-powered incident analysis tool that queries your GitHub and Sentry data via [Coral](https://www.wemakedevs.org/hackathons/coral) (SQL-over-API), sends it to Google's Gemini AI for intelligent analysis, and produces a beautiful, actionable incident report.

---

## The Story

I built this on a **2GB RAM Arch Linux laptop** — no fancy hardware, no expensive cloud services. Just Coral, Python, and Gemini's free tier. If it works on my machine, it works anywhere. That's the point of Coral.

---

## What It Does

1. **You paste an alert** — "Database timeout errors in production API"
2. **Coral queries your data sources** via SQL:
   - Recent Sentry issues (fatal/error)
   - Recent GitHub commits
   - Open security alerts
   - Open pull requests
   - **Cross-source JOIN** between GitHub commits and Sentry fatal errors
3. **Gemini AI analyzes everything** — correlating commits with errors to find root cause
4. **Beautiful incident report** — structured analysis with actionable recommendations

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3, Flask |
| AI Analysis | Google Gemini 1.5 Flash (free tier) |
| Data Layer | Coral CLI (SQL over GitHub + Sentry APIs) |
| Frontend | Vanilla HTML + JS + Tailwind CSS (CDN) |
| RAM Usage | < 150MB |

---

## Features

- **Real Coral SQL queries** — Every query runs actual `coral query --json` commands
- **Cross-source JOINs** — Demonstrates Coral's killer feature: `JOIN github.commits c ON sentry.issues s`
- **AI-powered analysis** — Gemini correlates commits with errors to identify root cause
- **Beautiful dark UI** — Glassmorphism, animations, typewriter SQL terminal
- **Responsive** — Works on mobile, tablet, and desktop
- **Zero npm** — Pure vanilla JS + Tailwind CDN for maximum portability
- **Lightweight** — Runs comfortably on 2GB RAM

---

## Project Structure

```
sre-investigator/
│
├── queries.py          # Coral SQL query runner (subprocess)
├── agent.py            # Main orchestrator
├── gemini.py           # Gemini API integration
├── report.py           # Report formatter
├── app.py              # Flask web server
│
├── templates/
│   └── index.html      # Dark-themed UI (Tailwind CDN)
│
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── README.md           # This file
└── SUBMISSION.md       # Hackathon submission text
```

---

## Quick Start

### Prerequisites

- Python 3.8+
- Coral CLI installed and configured (`coral` command available)
- GitHub and Sentry sources connected in Coral
- Gemini API key (free tier)

### Install

```bash
# Clone or copy the project
cd sre-investigator

# Install dependencies
pip install -r requirements.txt --break-system-packages

# Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run the server
python app.py
```

### Access

Open your browser and go to **http://localhost:5000**

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key (free tier) |

Get your key at: https://aistudio.google.com/app/apikey

---

## Coral SQL Queries Used

### Sentry Issues
```sql
SELECT title, culprit, level, status, first_seen, last_seen
FROM sentry.issues
WHERE level IN ('error', 'fatal')
ORDER BY last_seen DESC
LIMIT 10
```

### GitHub Commits
```sql
SELECT sha, commit_message, author_login, html_url, created_at
FROM github.commits
ORDER BY created_at DESC
LIMIT 10
```

### Cross-Source JOIN (Showcase)
```sql
SELECT c.sha, c.commit_message, c.author_login,
       s.title as sentry_error, s.level
FROM github.commits c
JOIN sentry.issues s ON s.first_seen >= c.created_at
WHERE s.level = 'fatal'
ORDER BY s.first_seen DESC
LIMIT 10
```

---

## API Endpoint

### POST `/investigate`

Request:
```json
{
  "alert": "Database timeout errors in production API"
}
```

Response:
```json
{
  "timestamp": "2024-01-15T10:30:00+00:00",
  "ai_analysis": "## Incident Summary...",
  "stats": {
    "sentry_issues_found": 8,
    "github_commits_analyzed": 10,
    "security_alerts_found": 2,
    "open_prs_found": 3,
    "cross_source_correlations": 4
  },
  "raw_data": { ... }
}
```

---

## Why This Project Wins

| Criteria | How We Deliver |
|----------|---------------|
| **Real Problem** | Every engineering team struggles with incident investigation |
| **Coral Power** | 4+ data sources with actual cross-source SQL JOINs |
| **AI Integration** | Gemini correlates commits with errors for root cause analysis |
| **Visual Impact** | Dark theme, glassmorphism, animations — judges remember it |
| **Lightweight** | Runs on 2GB RAM, no heavy frameworks |
| **Judging Optimization** | Directly targets 5/6 judging criteria |

---

## Hackathon Details

- **Event**: Pirates of the Coral-bean Hackathon by WeMakeDevs
- **Track**: Track 1 — Enterprise Agent
- **Prize Target**: MacBook Neo
- **Dates**: May 25 – May 31, 2026
- **Hackathon Page**: https://www.wemakedevs.org/hackathons/coral

---

## License

MIT — Built with Coral, powered by Gemini.

---

> ⚡ *"If it works on 2GB RAM, it works anywhere."*
