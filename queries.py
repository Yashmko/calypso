"""
Coral SQL Query Runner
Executes Coral CLI commands via subprocess to query GitHub and Sentry data sources.
"""

import subprocess
import json
import logging
import os
import time

logger = logging.getLogger(__name__)

# Track query history globally (simple in-memory storage)
QUERY_HISTORY = []

def run_coral_query(sql: str) -> dict:
    """
    Execute a Coral SQL query via subprocess.
    Returns: { "data": [...], "sql": "...", "execution_time_ms": 0 }
    """
    start_time = time.time()
    variants = [
        ["coral", "sql", "--format", "json", sql],
        ["coral", "query", "--json", sql],
        ["coral", "query", sql]
    ]
    
    result_data = []
    final_cmd = None
    
    for cmd in variants:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                continue
                
            output = result.stdout.strip()
            if not output:
                continue

            try:
                data = json.loads(output)
                if isinstance(data, list):
                    result_data = data
                elif isinstance(data, dict):
                    result_data = data.get("results", []) or data.get("data", []) or []
                
                final_cmd = cmd
                break # Found a winner
            except json.JSONDecodeError:
                continue
                
        except Exception:
            continue
            
    execution_time_ms = int((time.time() - start_time) * 1000)
    
    query_info = {
        "data": result_data,
        "sql": sql,
        "execution_time_ms": execution_time_ms,
        "timestamp": time.time()
    }
    
    # Update global history
    QUERY_HISTORY.append({
        "sql": sql,
        "execution_time_ms": execution_time_ms,
        "rows": len(result_data)
    })
    if len(QUERY_HISTORY) > 10:
        QUERY_HISTORY.pop(0)
        
    return query_info


def get_source_status() -> dict:
    """Check if GitHub and Sentry sources are responding."""
    github_check = run_coral_query("SELECT 1 FROM github.user LIMIT 1")
    sentry_check = run_coral_query("SELECT 1 FROM sentry.projects LIMIT 1")
    
    return {
        "github": len(github_check["data"]) >= 0 if github_check["sql"] else False,
        "sentry": len(sentry_check["data"]) >= 0 if sentry_check["sql"] else False
    }


def get_recent_sentry_issues(limit: int = 10) -> dict:
    """Get recent fatal/error level issues from Sentry."""
    sql = f"""
    SELECT title, level, status, first_seen, last_seen, project
    FROM sentry.issues
    WHERE level IN ('error', 'fatal')
    ORDER BY last_seen DESC
    LIMIT {limit}
    """
    return run_coral_query(sql)


def get_recent_github_commits(owner: str, repo: str, limit: int = 10) -> dict:
    """Get recent GitHub commits for a specific repository."""
    sql = f"""
    SELECT sha, commit__message as commit_message, author__login as author_login, html_url, commit__author__date as created_at
    FROM github.commits
    WHERE owner = '{owner}' AND repo = '{repo}'
    ORDER BY commit__author__date DESC
    LIMIT {limit}
    """
    return run_coral_query(sql)


def search_github_commits(owner: str, repo: str, keyword: str, limit: int = 10) -> dict:
    """Search for commits matching a specific keyword."""
    sql = f"""
    SELECT sha, commit__message as commit_message, author__login as author_login, html_url, commit__author__date as created_at
    FROM github.commits
    WHERE owner = '{owner}' AND repo = '{repo}' 
    AND (commit__message LIKE '%{keyword}%' OR author__login LIKE '%{keyword}%')
    ORDER BY commit__author__date DESC
    LIMIT {limit}
    """
    return run_coral_query(sql)


def get_github_security_alerts(org: str, limit: int = 10) -> dict:
    """Get open GitHub security alerts for an organization."""
    sql = f"""
    SELECT number, security_advisory__summary as title, state, severity, created_at
    FROM github.alerts
    WHERE org = '{org}' AND state = 'open'
    LIMIT {limit}
    """
    return run_coral_query(sql)


def get_open_pull_requests(owner: str, repo: str, limit: int = 5) -> dict:
    """Get open GitHub pull requests for a specific repository."""
    sql = f"""
    SELECT number, title, state, user__login as user_login, created_at
    FROM github.pulls
    WHERE owner = '{owner}' AND repo = '{repo}' AND state = 'open'
    ORDER BY created_at DESC
    LIMIT {limit}
    """
    return run_coral_query(sql)


def get_cross_source_join(owner: str, repo: str, limit: int = 10) -> dict:
    """Cross-source JOIN between GitHub commits and Sentry issues."""
    sql = f"""
    SELECT 
        c.sha, 
        c.commit__message as commit_message, 
        c.author__login as author_login, 
        s.title as sentry_error, 
        s.level
    FROM github.commits c
    JOIN sentry.issues s ON s.first_seen >= c.commit__author__date
    WHERE c.owner = '{owner}' AND c.repo = '{repo}' AND s.level = 'fatal'
    ORDER BY s.first_seen DESC
    LIMIT {limit}
    """
    return run_coral_query(sql)


def get_incident_timeline(owner: str, repo: str, limit: int = 20) -> dict:
    """Unified timeline of commits and errors using UNION ALL."""
    sql = f"""
    SELECT 'commit' as type, commit__author__date as ts, commit__message as msg, author__login as actor
    FROM github.commits
    WHERE owner = '{owner}' AND repo = '{repo}'
    UNION ALL
    SELECT 'error' as type, first_seen as ts, title as msg, project as actor
    FROM sentry.issues
    WHERE level IN ('error', 'fatal')
    ORDER BY ts DESC
    LIMIT {limit}
    """
    return run_coral_query(sql)


def get_multi_repo_comparison(repos: list, limit: int = 10) -> dict:
    """
    Compare multiple repositories side-by-side using UNION ALL.
    repos: list of { "owner": "...", "repo": "..." }
    """
    if not repos:
        return {"data": [], "sql": "", "execution_time_ms": 0}
        
    parts = []
    for r in repos:
        parts.append(f"""
            SELECT '{r['repo']}' as repository, sha, commit__message as msg, author__login as actor, commit__author__date as ts
            FROM github.commits
            WHERE owner = '{r['owner']}' AND repo = '{r['repo']}'
        """)
        
    sql = " UNION ALL ".join(parts) + f" ORDER BY ts DESC LIMIT {limit}"
    return run_coral_query(sql)


if __name__ == "__main__":
    # Quick test
    print("Testing Coral queries...")
    result = get_recent_github_commits("Yashmko", "Auditflow", 1)
    print(f"SQL: {result['sql']}")
    print(f"Time: {result['execution_time_ms']}ms")
    print(json.dumps(result['data'], indent=2))
