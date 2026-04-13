from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import random
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Load environment variables FIRST
load_dotenv()

from salvatore_sheets import save_registration

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

# ===============================
# SALVATORE
# ===============================

@app.route("/salvatore")
def salvatore():
    return render_template("e_salvatore.html")

@app.route("/egg_shell_mosaic")
def mosaic():
    return render_template("e_salvatore/mosaic.html")

@app.route("/story_telling_rohani")
def storytelling():
    return render_template("e_salvatore/storytelling.html")

@app.route("/bernyanyi_rohani")
def nyanyi():
    return render_template("e_salvatore/nyanyi.html")

@app.route("/quiz_alkitab")
def quiz_alkitab():
    return render_template("e_salvatore/quiz_alkitab.html")

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
        if result:
            return jsonify({"success": True, "message": "Registration successful!"})
        else:
            return jsonify({"success": False, "message": "Failed to save registration to spreadsheet."}), 500
    except Exception as e:
        with open('salvatore_debug.log', 'a') as f:
            f.write(f"[REGISTER ERROR] {str(e)}\n")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

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
