from flask import Flask, render_template, request, jsonify, abort
from dotenv import load_dotenv
import os
import random
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Load environment variables FIRST
load_dotenv()

from salvatore_sheets import save_registration, get_registration_count, get_google_sheets_client, SHEETS, PARTICIPANT_LIMITS
from ravenith_config import (
    RAVENITH_APPS_SCRIPT_URL,
    RAVENITH_BANNER,
    RAVENITH_COMPETITIONS,
    RAVENITH_LOMBA_ORDER,
    RAVENITH_POSTER_DIR,
)

app = Flask(__name__)

# ===============================
# CONFIG
# ===============================
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload
app.config['UPLOAD_FOLDER'] = 'static/uploads/valentine'
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ===============================
# GOOGLE SHEETS
# ===============================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "valentine-sheet.json", scopes=scope
)
client = gspread.authorize(creds)
sheet = client.open("Valentine_Order").sheet1

# ===============================
# ROUTES HTML
# ===============================
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

@app.route("/coming_soon")
def coming_soon():
    return render_template("coming_soon.html")

@app.errorhandler(404)
def handle_404(error):
    return render_template("404.html"), 404

@app.route("/meloria")
def meloria():
    return render_template("e_meloria.html")

@app.route("/festiora")
def festiora():
    return render_template("e_festiora.html")

@app.route("/cupids_corner")
def cupids_corner():
    return render_template("valentine_order.html")

@app.route("/atthaira")
def atthaira():
    return render_template("e_atthaira_regist.html")

@app.route("/salvatore")
def salvatore():
    return render_template("e_salvatore.html")

# ===============================
# RAVENITH
# ===============================

@app.route("/ravenith")
def ravenith():
    return render_template(
        "e_ravenith.html",
        competitions=RAVENITH_COMPETITIONS,
        lomba_order=RAVENITH_LOMBA_ORDER,
        banner_file=RAVENITH_BANNER,
        poster_dir=RAVENITH_POSTER_DIR,
    )


@app.route("/ravenith/<competition>")
def ravenith_lomba(competition):
    if competition not in RAVENITH_COMPETITIONS:
        abort(404)
    return render_template(
        f"e_ravenith/{competition}.html",
        competition_id=competition,
        meta=RAVENITH_COMPETITIONS[competition],
        apps_script_url=RAVENITH_APPS_SCRIPT_URL,
    )

# =============================== 
# API ROUTES
# ===============================

@app.route("/register/<competition>", methods=["POST"])
def register_competition(competition):
    try:
        data = request.form.to_dict()
        with open('salvatore_debug.log', 'a') as f:
            f.write(f"[REGISTER] Competition: {competition}\n")
            f.write(f"[REGISTER] Data: {data}\n")
        result = save_registration(competition, data)
        with open('salvatore_debug.log', 'a') as f:
            f.write(f"[REGISTER] Result: {result}\n")
        
        if result == "limit_reached":
            return jsonify({"success": False, "message": "Sorry, the registration limit for this competition has been reached."}), 400
        elif result:
            return jsonify({"success": True, "message": "Registration successful!"})
        else:
            return jsonify({"success": False, "message": "Failed to save registration to spreadsheet."}), 500
    except Exception as e:
        with open('salvatore_debug.log', 'a') as f:
            f.write(f"[REGISTER ERROR] {str(e)}\n")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route("/api/registration-status/<competition>")
def get_registration_status(competition):
    """Get current registration count and limit for a competition."""
    try:
        if competition not in SHEETS:
            return jsonify({"error": "Unknown competition"}), 404
        
        limit = PARTICIPANT_LIMITS.get(competition, 0)
        try:
            client = get_google_sheets_client()
            current_count = get_registration_count(client, SHEETS[competition])
        except Exception as e:
            # If we can't get the count, return limit as 0 (unlimited) to be safe
            current_count = 0
        
        return jsonify({
            "competition": competition,
            "current_count": current_count,
            "limit": limit,
            "spots_left": max(0, limit - current_count) if limit > 0 else -1,  # -1 means unlimited
            "is_full": limit > 0 and current_count >= limit
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/valentine_order", methods=["POST"])
def valentine_order():
    try:
        # Get form data
        name = request.form.get("name")
        message = request.form.get("message")
        file = request.files.get("file")

        # Save file if uploaded
        file_path = None
        if file and allowed_file(file.filename):
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

        # Prepare data for sheets
        row_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name,
            message,
            file_path or ""
        ]

        # Append to sheet
        sheet.append_row(row_data)

        return jsonify({"success": True, "message": "Order submitted successfully!"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
