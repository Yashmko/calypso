"""
Gemini AI Integration
Uses Google's Gemini API to analyze incident data and generate intelligent reports.
"""

import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Use gemini-flash-latest for fast, free-tier responses
MODEL = genai.GenerativeModel("gemini-flash-latest")


def generate_incident_report(alert_description: str, github_data: dict, sentry_data: dict) -> str:
    """
    Generate an AI-powered incident report using Gemini.
    
    Args:
        alert_description: The user's alert/incident description
        github_data: Dict containing github commits, PRs, and security alerts
        sentry_data: Dict containing sentry issues and cross-source join data
        
    Returns:
        Formatted incident report as markdown string
    """
    try:
        # Build the context from our data
        context = _build_context(github_data, sentry_data)
        
        prompt = f"""You are CALYPSO, an expert AI Site Reliability Engineer.
"She knows the waters. She sees the wrecks. She tells you what broke before you even ask."

Analyze the following alert and system data to produce a comprehensive incident report.

## ALERT DESCRIPTION
{alert_description}

## SYSTEM DATA
{context}

## YOUR TASK
Generate a detailed incident report with the following EXACT sections. Use markdown headers (##).

## Incident Summary
Provide a concise 2-3 sentence summary of what happened and its potential impact.

## Root Cause
Based on the correlation between recent commits and errors, identify the most probable root cause.
Be specific about which commit or change likely introduced the issue.

## Affected Components
List the specific services, endpoints, or components that are affected.

## Recommended Actions
Provide a numbered, step-by-step action plan to resolve the incident.
Include immediate mitigation steps and longer-term fixes.

## Prevention Plan
Suggest concrete measures to prevent this type of incident in the future.
Consider code review practices, testing, monitoring, and deployment strategies.

## Confidence Score
Assign a confidence score: [Low / Medium / High]
Provide a short (1 sentence) explanation for why this score was chosen based on the evidence available.

Format your response in clean markdown. Be thorough but concise. Focus on actionable insights.
"""

        response = MODEL.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            logger.error("Gemini returned empty response")
            return _generate_fallback_report(alert_description)
            
    except Exception as e:
        logger.error(f"Error generating incident report with Gemini: {e}")
        return _generate_fallback_report(alert_description)


def _build_context(github_data: dict, sentry_data: dict) -> str:
    """Build a structured context string from the collected data."""
    context_parts = []
    
    # Sentry issues
    sentry_issues = sentry_data.get("sentry_issues", [])
    if sentry_issues:
        context_parts.append(f"### Recent Sentry Errors ({len(sentry_issues)} found)")
        for issue in sentry_issues[:5]:
            context_parts.append(
                f"- [{issue.get('level', 'unknown').upper()}] {issue.get('title', 'N/A')}"
                f"  (Culprit: {issue.get('culprit', 'unknown')}, "
                f"First seen: {issue.get('first_seen', 'unknown')})"
            )
    else:
        context_parts.append("### Recent Sentry Errors\nNo sentry issues found.")
    
    # GitHub commits
    github_commits = github_data.get("github_commits", [])
    if github_commits:
        context_parts.append(f"\n### Recent GitHub Commits ({len(github_commits)} found)")
        for commit in github_commits[:5]:
            context_parts.append(
                f"- [{commit.get('sha', 'unknown')[:7]}] {commit.get('commit_message', 'N/A')[:60]}"
                f"  (by {commit.get('author_login', 'unknown')})"
            )
    else:
        context_parts.append("\n### Recent GitHub Commits\nNo commits found.")
    
    # Related Commits (Keyword-based)
    related_commits = github_data.get("related_commits", [])
    if related_commits:
        context_parts.append(f"\n### Highly Relevant Historical Changes ({len(related_commits)} found matching keywords)")
        for commit in related_commits:
            context_parts.append(
                f"- [{commit.get('sha', 'unknown')[:7]}] {commit.get('commit_message', 'N/A')[:100]}"
                f"  (Date: {commit.get('created_at', 'unknown')}, by {commit.get('author_login', 'unknown')})"
            )
    
    # Security alerts
    security_alerts = github_data.get("security_alerts", [])
    if security_alerts:
        context_parts.append(f"\n### Open Security Alerts ({len(security_alerts)} found)")
        for alert in security_alerts[:3]:
            context_parts.append(
                f"- [{alert.get('severity', 'unknown')}] {alert.get('title', 'N/A')}"
            )
    
    # Open PRs
    open_prs = github_data.get("open_prs", [])
    if open_prs:
        context_parts.append(f"\n### Open Pull Requests ({len(open_prs)} found)")
        for pr in open_prs[:3]:
            context_parts.append(
                f"- #{pr.get('number', '?')}: {pr.get('title', 'N/A')}"
            )
    
    # Cross-source joins
    cross_joins = sentry_data.get("cross_source_joins", [])
    if cross_joins:
        context_parts.append(f"\n### Correlated Commits + Fatal Errors ({len(cross_joins)} correlations)")
        for join in cross_joins[:5]:
            context_parts.append(
                f"- Commit [{join.get('sha', 'unknown')[:7]}] by {join.get('author_login', '?')}: "
                f"'{join.get('commit_message', 'N/A')[:40]}' "
                f"-> Linked to fatal error: {join.get('sentry_error', 'unknown')[:50]}"
            )
    
    return "\n".join(context_parts)


def _generate_fallback_report(alert_description: str) -> str:
    """Generate a basic fallback report when Gemini API fails."""
    return f"""## Incident Summary
Investigating alert: "{alert_description}". The system detected an anomaly that requires immediate attention.

## Root Cause
**[AI Analysis Failed]** Unable to determine root cause due to Gemini AI service unavailability. Please review the RAW EVIDENCE tab and logs manually.

## Affected Components
- Primary service (investigating)

## Recommended Actions
1. Check service health dashboards
2. Review recent deployment logs
3. Verify database connectivity
4. Check downstream service dependencies
5. Escalate to on-call engineer if unresolved

## Prevention Plan
- Implement proper error handling
- Add health check endpoints
- Review deployment procedures

## Confidence Score
Low
AI service is currently unavailable.
"""


def answer_followup_question(question: str, context_data: dict, alert: str) -> str:
    """
    Answer a follow-up question based on investigation context.
    """
    try:
        # Build a context string from the raw data
        # We'll use a simplified version of _build_context but for the full data
        github_data = {
            "github_commits": context_data.get("github_commits", []),
            "security_alerts": context_data.get("security_alerts", []),
            "open_prs": context_data.get("open_prs", [])
        }
        sentry_data = {
            "sentry_issues": context_data.get("sentry_issues", []),
            "cross_source_joins": context_data.get("cross_source_joins", []),
            "timeline": context_data.get("timeline", [])
        }
        
        context = _build_context(github_data, sentry_data)
        
        prompt = f"""You are CALYPSO, an SRE assistant helping an engineer investigate an incident.
"She knows the waters. She sees the wrecks. She tells you what broke before you even ask."

You already provided an initial report for the alert: "{alert}".

The following is the system data you have access to:
{context}

USER QUESTION: {question}

Please answer the question accurately based ONLY on the provided system data. 
If the data doesn't contain the answer, say so.
Be helpful, concise, and technical. Use markdown for lists or code.
"""

        response = MODEL.generate_content(prompt)
        return response.text if response and response.text else "I'm sorry, I couldn't generate an answer."
        
    except Exception as e:
        logger.error(f"Error answering follow-up: {e}")
        return f"Error: {str(e)}"
    # Quick test
    test_github = {
        "github_commits": [
            {"sha": "abc1234", "commit_message": "Fix auth middleware", "author_login": "dev1"}
        ],
        "security_alerts": [],
        "open_prs": []
    }
    test_sentry = {
        "sentry_issues": [
            {"title": "Database timeout", "level": "fatal", "culprit": "api.endpoint", "first_seen": "2024-01-01"}
        ],
        "cross_source_joins": []
    }
    
    report = generate_incident_report("Database timeout in production", test_github, test_sentry)
    print(report)
