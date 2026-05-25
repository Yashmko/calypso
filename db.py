import sqlite3
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = "investigations.db"

def init_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS investigations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    repo TEXT NOT NULL,
                    alert_text TEXT NOT NULL,
                    ai_summary TEXT NOT NULL,
                    sentry_count INTEGER NOT NULL,
                    commit_count INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    full_report JSON NOT NULL
                )
            ''')
            conn.commit()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

def save_investigation(repo: str, alert_text: str, report: dict, status: str = "success") -> int:
    try:
        ai_summary = ""
        # Extract a short summary from the AI analysis
        if "ai_analysis" in report and report["ai_analysis"]:
            lines = report["ai_analysis"].split("\n")
            for line in lines:
                if line.strip() and not line.startswith("#"):
                    ai_summary = line[:200] + ("..." if len(line) > 200 else "")
                    break

        sentry_count = len(report.get("raw_data", {}).get("sentry_issues", []))
        commit_count = len(report.get("raw_data", {}).get("github_commits", []))
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO investigations (timestamp, repo, alert_text, ai_summary, sentry_count, commit_count, status, full_report)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.utcnow().isoformat(), repo, alert_text, ai_summary, sentry_count, commit_count, status, json.dumps(report)))
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Failed to save investigation: {e}")
        return -1

def get_recent_investigations(limit: int = 10) -> list:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, timestamp, repo, alert_text, ai_summary, sentry_count, commit_count, status 
                FROM investigations 
                ORDER BY id DESC LIMIT ?
            ''', (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Failed to fetch recent investigations: {e}")
        return []

def get_investigation(inv_id: int) -> dict:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT full_report FROM investigations WHERE id = ?', (inv_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["full_report"])
            return None
    except Exception as e:
        logger.error(f"Failed to fetch investigation {inv_id}: {e}")
        return None
