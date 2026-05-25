"""
Report Formatter
Formats the AI-generated incident report into a structured JSON response.
"""

import json
import logging
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def send_to_slack(report: dict) -> bool:
    """Post a concise incident summary to a Slack webhook."""
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        logger.error("SLACK_WEBHOOK_URL not configured.")
        return False
        
    try:
        # Extract a short summary from the AI analysis
        ai_summary = "No summary available."
        if "ai_analysis" in report and report["ai_analysis"]:
            lines = report["ai_analysis"].split("\n")
            for line in lines:
                if line.strip() and not line.startswith("#"):
                    ai_summary = line[:300] + ("..." if len(line) > 300 else "")
                    break
                    
        stats = report.get("stats", {})
        correlations = stats.get("cross_source_correlations", 0)
        
        message = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 CALYPSO Incident Report"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{ai_summary}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"*{stats.get('sentry_issues_found', 0)}* Sentry Issues | *{stats.get('github_commits_analyzed', 0)}* Commits | *{correlations}* Correlations"
                        }
                    ]
                }
            ]
        }
        
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(message).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            return response.status == 200
            
    except Exception as e:
        logger.error(f"Failed to send to Slack: {e}")
        return False


def format_report(ai_analysis: str, raw_data: dict) -> dict:
    """
    Format the incident report into a structured response.
    
    Args:
        ai_analysis: The markdown report from Gemini
        raw_data: Dict containing all the raw data collected from queries
        
    Returns:
        Structured report dict with timestamp, analysis, stats, and raw data
    """
    try:
        # Calculate stats
        sentry_issues = raw_data.get("sentry_issues", [])
        github_commits = raw_data.get("github_commits", [])
        security_alerts = raw_data.get("security_alerts", [])
        open_prs = raw_data.get("open_prs", [])
        cross_joins = raw_data.get("cross_source_joins", [])
        timeline = raw_data.get("timeline", [])
        
        stats = {
            "sentry_issues_found": len(sentry_issues),
            "github_commits_analyzed": len(github_commits),
            "security_alerts_found": len(security_alerts),
            "open_prs_found": len(open_prs),
            "cross_source_correlations": len(cross_joins),
            "timeline_events": len(timeline)
        }
        
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ai_analysis": ai_analysis,
            "stats": stats,
            "raw_data": {
                "sentry_issues": sentry_issues[:10],
                "github_commits": github_commits[:10],
                "security_alerts": security_alerts[:10],
                "open_prs": open_prs[:10],
                "cross_source_joins": cross_joins[:10],
                "timeline": timeline[:20]
            }
        }
        
        logger.info(f"Report formatted: {stats}")
        return report
        
    except Exception as e:
        logger.error(f"Error formatting report: {e}")
        # Return a minimal valid report even on error
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ai_analysis": ai_analysis or "Report generation partially failed.",
            "stats": {
                "sentry_issues_found": 0,
                "github_commits_analyzed": 0,
                "security_alerts_found": 0,
                "open_prs_found": 0,
                "cross_source_correlations": 0
            },
            "raw_data": {},
            "error": str(e)
        }


if __name__ == "__main__":
    # Quick test
    test_ai = "## Test Report\n\nThis is a test."
    test_data = {
        "sentry_issues": [{"title": "Error 1"}, {"title": "Error 2"}],
        "github_commits": [{"sha": "abc"}],
        "security_alerts": [],
        "open_prs": [{"number": 1}],
        "cross_source_joins": [{"sha": "abc", "sentry_error": "Error 1"}]
    }
    
    result = format_report(test_ai, test_data)
    print(json.dumps(result, indent=2))
