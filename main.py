from flask import Flask, render_template, request, jsonify
import os
import random
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "valentine-sheet.json", scope
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

@app.route("/egg_shell_mosaic_sprint")
def mosaic():
    return render_template("e_salvatore/mosaic.html")

@app.route("/story_telling_rohani")
def storytelling():
    return render_template("e_salvatore/storytelling.html")

@app.route("/menyanyi_lagu_rohani")
def nyanyi():
    return render_template("e_salvatore/nyanyi.html")

@app.route("/quiz_alkitab_dan_pengetahuan_umum_agama")
def kuis_alkitab():
    return render_template("e_salvatore/kuis_alkitab.html")

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
