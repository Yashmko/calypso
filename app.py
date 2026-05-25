"""
CALYPSO - Flask Web Server
"She knows the waters. She sees the wrecks. She tells you what broke before you even ask."
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from agent import investigate, chat_followup
from queries import get_source_status
from db import init_db, save_investigation, get_recent_investigations, get_investigation
from report import send_to_slack

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def index():
    """Serve the main UI page."""
    return render_template("index.html")


@app.route("/slack", methods=["POST"])
def slack_route():
    """Trigger sending report to Slack."""
    try:
        report = request.get_json()
        if not report:
            return jsonify({"error": "No report data provided"}), 400
            
        success = send_to_slack(report)
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "Failed to send to Slack or webhook not configured"}), 500
            
    except Exception as e:
        logger.error(f"Error sending to slack: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/investigate", methods=["POST"])
def run_investigation():
    """
    Run an investigation based on the provided alert description and repository.
    
    Request body: {"alert": "...", "repo": "owner/repo", "compare_repo": "owner/repo2"}
    """
    try:
        data = request.get_json()
        
        if not data or "alert" not in data:
            return jsonify({
                "error": "Missing 'alert' field in request body"
            }), 400
        
        alert_description = data["alert"].strip()
        repo_full_name = data.get("repo", "").strip()
        compare_repo = data.get("compare_repo", "").strip() or None
        
        if not repo_full_name:
            return jsonify({
                "error": "Missing 'repo' field in request body. Please provide a repository in 'owner/repo' format."
            }), 400
        
        if not alert_description:
            return jsonify({
                "error": "Alert description cannot be empty"
            }), 400
        
        logger.info(f"Investigation for {repo_full_name} (comparing with {compare_repo}): {alert_description[:60]}...")
        
        # Run the investigation
        report = investigate(alert_description, repo_full_name, compare_repo)
        
        # Save to database
        status = "error" if "Error" in report.get("ai_analysis", "") else "success"
        save_investigation(repo_full_name, alert_description, report, status)
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error handling investigation request: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route("/investigations", methods=["GET"])
def get_investigations_route():
    """Return the last 10 cases."""
    return jsonify(get_recent_investigations(10))

@app.route("/investigations/<int:inv_id>", methods=["GET"])
def get_investigation_detail(inv_id):
    """Return a single investigation in detail."""
    inv = get_investigation(inv_id)
    if inv:
        return jsonify(inv)
    return jsonify({"error": "Investigation not found"}), 404


@app.route("/chat", methods=["POST"])
def run_chat():
    """
    Handle follow-up questions about an investigation.
    
    Request body: {"question": "...", "context_data": {...}, "alert": "..."}
    """
    try:
        data = request.get_json()
        question = data.get("question")
        context_data = data.get("context_data")
        alert = data.get("alert")
        
        if not question or not context_data:
            return jsonify({"error": "Missing question or context"}), 400
            
        answer = chat_followup(question, context_data, alert)
        return jsonify({"answer": answer})
        
    except Exception as e:
        logger.error(f"Error handling chat request: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/status")
def get_status():
    """Check Coral source connectivity."""
    return jsonify(get_source_status())


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    # Run on port 5000
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
