"""
CALYPSO - Flask Web Server
"She knows the waters. She sees the wrecks. She tells you what broke before you even ask."
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from agent import investigate, chat_followup
from queries import get_source_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route("/")
def index():
    """Serve the main UI page."""
    return render_template("index.html")


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
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error handling investigation request: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


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
