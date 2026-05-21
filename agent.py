"""
SRE Investigator - Main Orchestrator
Coordinates data collection from Coral and AI analysis from Gemini to produce incident reports.
"""

import logging
from queries import (
    get_recent_sentry_issues,
    get_recent_github_commits,
    get_github_security_alerts,
    get_open_pull_requests,
    get_cross_source_join,
    get_incident_timeline,
    search_github_commits,
    get_multi_repo_comparison,
    QUERY_HISTORY
)
from gemini import generate_incident_report, answer_followup_question
from report import format_report

logger = logging.getLogger(__name__)


def investigate(alert_description: str, repo_full_name: str = "Yashmko/Auditflow", compare_repo: str = None) -> dict:
    """
    Main investigation orchestrator with optional multi-repo comparison.
    """
    logger.info(f"Starting investigation for: {alert_description[:60]}...")
    
    try:
        # 1. Parse Primary Repo
        owner, repo = _parse_repo(repo_full_name)
        
        # 2. Collect Data with Telemetry
        queries_meta = {}
        
        # Sentry Issues
        res = get_recent_sentry_issues(10)
        sentry_issues = res["data"]
        queries_meta["sentry_issues"] = {"sql": res["sql"], "time": res["execution_time_ms"]}
        
        # GitHub Commits
        res = get_recent_github_commits(owner, repo, 10)
        github_commits = res["data"]
        queries_meta["github_commits"] = {"sql": res["sql"], "time": res["execution_time_ms"]}
        
        # Related Commits (Keyword Search)
        keywords = _extract_keywords(alert_description)
        related_commits = []
        if keywords:
            res = search_github_commits(owner, repo, keywords[0], 5)
            related_commits = res["data"]
            queries_meta["related_commits"] = {"sql": res["sql"], "time": res["execution_time_ms"]}
            
        # Security Alerts
        res = get_github_security_alerts(owner, 10)
        security_alerts = res["data"]
        queries_meta["security_alerts"] = {"sql": res["sql"], "time": res["execution_time_ms"]}
        
        # Open PRs
        res = get_open_pull_requests(owner, repo, 5)
        open_prs = res["data"]
        queries_meta["open_prs"] = {"sql": res["sql"], "time": res["execution_time_ms"]}
        
        # Cross-Source JOIN
        res = get_cross_source_join(owner, repo, 10)
        cross_source_joins = res["data"]
        queries_meta["cross_source_joins"] = {"sql": res["sql"], "time": res["execution_time_ms"]}
        
        # Incident Timeline
        res = get_incident_timeline(owner, repo, 15)
        timeline = res["data"]
        queries_meta["timeline"] = {"sql": res["sql"], "time": res["execution_time_ms"]}
        
        # Optional: Multi-Repo Comparison
        comparison_data = []
        if compare_repo:
            c_owner, c_repo = _parse_repo(compare_repo)
            res = get_multi_repo_comparison([
                {"owner": owner, "repo": repo},
                {"owner": c_owner, "repo": c_repo}
            ], 10)
            comparison_data = res["data"]
            queries_meta["comparison"] = {"sql": res["sql"], "time": res["execution_time_ms"]}
            
        # 3. Organize for Gemini
        github_data = {
            "repo": repo_full_name,
            "github_commits": github_commits,
            "related_commits": related_commits,
            "security_alerts": security_alerts,
            "open_prs": open_prs
        }
        
        sentry_data = {
            "sentry_issues": sentry_issues,
            "cross_source_joins": cross_source_joins,
            "timeline": timeline,
            "comparison_data": comparison_data
        }
        
        # 4. Generate AI Report
        ai_analysis = generate_incident_report(alert_description, github_data, sentry_data)
        
        # 5. Format Final Result
        raw_data = {
            "sentry_issues": sentry_issues,
            "github_commits": github_commits,
            "security_alerts": security_alerts,
            "open_prs": open_prs,
            "cross_source_joins": cross_source_joins,
            "timeline": timeline,
            "comparison": comparison_data
        }
        
        report = format_report(ai_analysis, raw_data)
        report["queries_meta"] = queries_meta
        report["live_history"] = list(reversed(QUERY_HISTORY[-5:]))
        
        return report
        
    except Exception as e:
        logger.error(f"Investigation failed: {e}")
        return format_report(f"## Error\n{str(e)}", {})


def chat_followup(question: str, context_data: dict, alert: str) -> str:
    """Handle follow-up questions."""
    return answer_followup_question(question, context_data, alert)


def _parse_repo(full_name: str):
    """Parse 'owner/repo' string."""
    if "/" in full_name:
        return full_name.split("/", 1)
    return full_name, ""


def _extract_keywords(text: str) -> list:
    """Extract 1-2 important technical keywords."""
    stop_words = {'the', 'in', 'and', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'is', 'are', 'was', 'were', 'errors', 'error', 'degradation', 'incident', 'investigation', 'testing', 'alert'}
    words = [w.lower().strip('.,!?()') for w in text.split()]
    keywords = [w for w in words if len(w) > 3 and w not in stop_words]
    return keywords


if __name__ == "__main__":
    res = investigate("Test", "Yashmko/Auditflow")
    print(f"Meta keys: {res['queries_meta'].keys()}")
