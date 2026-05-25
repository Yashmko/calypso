# Hackathon Submission — CALYPSO

## Project Name
**CALYPSO**

> *"She knows the waters. She sees the wrecks. She tells you what broke before you even ask."*

## Track
**Track 1 — Enterprise Agent**

## Prize Target
MacBook Neo

---

## Elevator Pitch

CALYPSO is an AI-powered incident analysis tool that uses Coral's SQL-over-API to query GitHub and Sentry data, then sends it to Gemini AI for intelligent root cause analysis — producing a beautiful, actionable incident report in seconds.

She knows the waters. She sees the wrecks. She tells you what broke before you even ask.

---

## Problem Statement

Every engineering team faces the same painful scenario: an alert fires at 2 AM, and you're scrambling across GitHub commits, Sentry errors, and PRs trying to figure out what broke and why. CALYPSO automates this entire investigation pipeline using Coral's cross-source SQL queries and Gemini AI analysis.

---

## What I Built

A lightweight Flask web app with a stunning dark UI that:

1. Accepts an incident/alert description
2. Queries **4 data sources** via Coral SQL:
   - Sentry issues (fatal/error levels)
   - GitHub commits
   - GitHub security alerts
   - Open pull requests
3. Executes a **cross-source SQL JOIN** between GitHub commits and Sentry fatal errors — Coral's most powerful feature
4. Generates a **Unified Incident Timeline** using `UNION ALL` to show exactly when things broke relative to deployments
5. Calculates an **Evidence Confidence Score (0-100)** based on source variety and correlation strength
6. Sends all data to **Gemini 1.5 Flash** for strictly structured AI-powered root cause analysis
7. Displays a **beautiful incident report** with summary, root cause, affected components, recommended actions, and prevention strategies
8. Includes **interactive follow-up chat** to query the investigation data further

**Key Technical Achievement**: The cross-source JOIN query correlates recent GitHub commits with Sentry fatal errors by temporal overlap, enabling AI to pinpoint which commit likely introduced the bug.

---

## Tech Stack

- **Python + Flask** — Backend server
- **Coral CLI** — SQL queries over GitHub and Sentry APIs
- **Google Gemini 1.5 Flash** — AI incident analysis
- **HTML + Tailwind CSS** — Dark-themed responsive UI
- **Zero npm, Zero React** — Pure vanilla JS for maximum portability

---

## Why It Wins

1. **Solves a REAL problem** — Incident investigation is universal pain
2. **Showcases Coral's strength** — Cross-source SQL JOINs are the killer feature
3. **AI + SQL together** — Unique combination of structured data querying + unstructured AI analysis
4. **Visually impressive** — Dark glassmorphism UI with animations
5. **Lightweight** — Runs on 2GB RAM Arch Linux, no heavy frameworks
6. **Actually works** — Real Coral queries, real Gemini API calls, real data

---

## Setup & Run

```bash
pip install -r requirements.txt --break-system-packages
echo "GEMINI_API_KEY=my_key_here" > .env
python app.py
# Visit http://localhost:5000
```

---

## Repository

[Your repo URL here]

---

## Demo Video

[Your demo video URL here]

---

## My Story

> I built this on a 2GB RAM Arch Linux laptop — no fancy hardware, no expensive cloud services. Just Coral, Python, and Gemini's free tier. If it works on my machine, it works anywhere. That's the point of Coral.

---

*Submitted for Pirates of the Coral-bean Hackathon by WeMakeDevs*
