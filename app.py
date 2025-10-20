import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_from_directory
import json
from datetime import datetime
import secrets

# Get port from environment variable or use default
port = int(os.environ.get('PORT', 5000))

app = Flask(__name__)

# Data file
DATA_FILE = "survey_results.json"

# Generate a secure random key for initiator verification
INITIATOR_SECRET = os.environ.get('INITIATOR_SECRET', secrets.token_hex(16))

def init_data():
    """Initialize data structure"""
    if not os.path.exists(DATA_FILE):
        data = {
            "results": [],
            "distribution": {
                "excellent": 0,  # 90-98 points
                "good_or_below": 0  # 30-89 points
            },
            "settings": {
                "total_leaders": 6,
                "max_excellent": 2,
                "min_good_or_below": 4
            }
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    """Load data"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """Save data"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Home page"""
    # Explicitly specify file path
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'survey_final.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Static file service"""
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), filename)

@app.route('/api/submit', methods=['POST'])
def submit_scores():
    """Submit scores"""
    try:
        # Get request data
        data = request.get_json()
        responder_id = data.get('responder_id')
        scores = data.get('scores', [])
        
        # Validate input
        if not responder_id:
            return jsonify({"success": False, "message": "Please enter employee ID"}), 400
        
        if len(scores) != 6:
            return jsonify({"success": False, "message": "Please rate all 6 leaders"}), 400
        
        # Check score range
        for score in scores:
            if not (30 <= score <= 98):
                return jsonify({"success": False, "message": "Scores must be between 30-98"}), 400
        
        # Load existing data
        app_data = load_data()
        settings = app_data["settings"]
        
        # Calculate distribution for this submission
        excellent_count = sum(1 for s in scores if 90 <= s <= 98)
        good_or_below_count = sum(1 for s in scores if 30 <= s <= 89)
        
        # Check if current vote meets requirements (2 excellent, 4 good or below)
        if excellent_count > 2:
            return jsonify({"success": False, "message": "Current vote exceeds excellent limit (max 2)"}), 400
            
        if good_or_below_count < 4:
            return jsonify({"success": False, "message": "Current vote lacks good/below (min 4)"}), 400
        
        # Save results
        app_data["results"].append({
            "responder_id": responder_id,
            "scores": scores,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update distribution statistics
        for score in scores:
            if 90 <= score <= 98:
                app_data["distribution"]["excellent"] += 1
            elif 30 <= score <= 89:
                app_data["distribution"]["good_or_below"] += 1
        
        save_data(app_data)
        
        return jsonify({"success": True, "message": "Survey submitted successfully"})
    
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/results')
def get_results():
    """Get results (requires correct secret)"""
    # Get secret from header or query parameter
    secret = request.headers.get('X-Initiator-Secret') or request.args.get('secret')
    
    # Verify secret
    if not secret or secret != INITIATOR_SECRET:
        return jsonify({"success": False, "message": "Unauthorized access"}), 403
    
    try:
        data = load_data()
        return jsonify({
            "success": True,
            "distribution": data["distribution"],
            "results": data["results"]
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    init_data()
    # In cloud deployment environment, listen on 0.0.0.0 and use environment variable for port
    app.run(debug=False, host='0.0.0.0', port=port)