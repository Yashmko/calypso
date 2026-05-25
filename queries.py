"""
Coral SQL Query Runner
Executes Coral CLI commands via subprocess to query GitHub and Sentry data sources.
"""

import subprocess
import json
import logging
import os
import time
import re

logger = logging.getLogger(__name__)

# Track query history globally (simple in-memory storage)
QUERY_HISTORY = []

def sanitize_input(val: str) -> str:
    """Strip special characters and strictly validate input to prevent SQL safety issues."""
    if not val:
        raise ValueError("Input value cannot be empty.")
        
    val_str = str(val).strip()
    if len(val_str) > 200:
        raise ValueError("Input value exceeds maximum allowed length.")
        
    # Allow alphanumeric, underscore, hyphen, dot, and space (for keywords)
    cleaned = re.sub(r'[^a-zA-Z0-9\._\-\s/]', '', val_str)
    
    if not cleaned or cleaned.isspace():
        raise ValueError(f"Input '{val}' contains only invalid characters.")
        
    return cleaned

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

    result_data = None
    last_error = ""

    for cmd in variants:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                last_error = result.stderr.strip() or result.stdout.strip() or f"Process exited with code {result.returncode}"
                continue

            output = result.stdout.strip()
            if not output:
                last_error = "Empty output returned from Coral."
                continue

            try:
                data = json.loads(output)
                if isinstance(data, list):
                    result_data = data
                elif isinstance(data, dict):
                    result_data = data.get("results", []) or data.get("data", []) or []

                break # Found a winner
            except json.JSONDecodeError as e:
                last_error = f"JSON parse error: {e}"
                continue

        except Exception as e:
            last_error = str(e)
            continue

    if result_data is None:
        logger.error(f"Coral query failed. Last error: {last_error} | SQL: {sql}")
        raise RuntimeError(f"Coral query failed: {last_error}")

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


def _check_source_connectivity(sql: str) -> bool:
    """Run a lightweight query purely to check return code (0 = connected)."""
    try:
        result = subprocess.run(
            ["coral", "sql", "--format", "json", sql],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def get_source_status() -> dict:
    """Check if GitHub and Sentry sources are responding."""
    return {
        "github": _check_source_connectivity("SELECT 1 FROM github.user LIMIT 1"),
        "sentry": _check_source_connectivity("SELECT 1 FROM sentry.projects LIMIT 1")
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
    owner, repo = sanitize_input(owner), sanitize_input(repo)
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
    owner, repo, keyword = sanitize_input(owner), sanitize_input(repo), sanitize_input(keyword)
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
    org = sanitize_input(org)
    sql = f"""
    SELECT number, security_advisory__summary as title, state, severity, created_at
    FROM github.alerts
    WHERE org = '{org}' AND state = 'open'
    LIMIT {limit}
    """
    return run_coral_query(sql)


def get_open_pull_requests(owner: str, repo: str, limit: int = 5) -> dict:
    """Get open GitHub pull requests for a specific repository."""
    owner, repo = sanitize_input(owner), sanitize_input(repo)
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
    owner, repo = sanitize_input(owner), sanitize_input(repo)
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
    owner, repo = sanitize_input(owner), sanitize_input(repo)
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
        owner, repo = sanitize_input(r['owner']), sanitize_input(r['repo'])
        parts.append(f"""
            SELECT '{repo}' as repository, sha, commit__message as msg, author__login as actor, commit__author__date as ts
            FROM github.commits
            WHERE owner = '{owner}' AND repo = '{repo}'
        """)
        
    sql = " UNION ALL ".join(parts) + f" ORDER BY ts DESC LIMIT {limit}"
    return run_coral_query(sql)


if __name__ == "__main__":
    # Quick test
    print("Testing Coral queries...")
    result = get_recent_github_commits("Yashmko", "calypso", 1)
    print(f"SQL: {result['sql']}")
    print(f"Time: {result['execution_time_ms']}ms")
    print(json.dumps(result['data'], indent=2))
