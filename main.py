from flask import Flask, render_template, request, jsonify
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# ===============================
# GOOGLE SHEETS SETUP
# ===============================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file("e-festiora-sheets-3bfd5f4f75a2.json", scopes=SCOPES)
gc = gspread.authorize(creds)

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1eOUPWVbY3X8uCHIOdTFnTBhUSXJaCcbRlh8yuo3F2vw/edit"
sh = gc.open_by_url(SPREADSHEET_URL)
ws = sh.sheet1  # atau sesuaikan worksheet yang digunakan

# ===============================
# ROUTES HTML
# ===============================
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

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

@app.route("/festiora/follow_the_harmony")
def follow_the_harmony():
    return render_template("Festiora/follow_the_harmony.html")

@app.route("/festiora/speed_drawing")
def speed_drawing():
    return render_template("Festiora/speed_drawing.html")

@app.route("/festiora/real_life_boardgame")
def real_life_boardgame():
    return render_template("Festiora/real_life_boardgame.html")

@app.route("/festiora/trivia_showdown")
def trivia_showdown():
    return render_template("Festiora/trivia_showdown.html")

@app.route("/festiora/triquest")
def triquest():
    return render_template("Festiora/triquest.html")

@app.route("/festiora/mlbb")
def mlbb():
    return render_template("Festiora/lomba_e_sport_mlbb.html")

@app.route("/festiora/case_crackers")
def case_crackers():
    return render_template("Festiora/case_crackers.html")

@app.route("/festiora/family_100")
def family_100():
    return render_template("Festiora/family_100.html")

@app.route("/festiora/workshop_robotic")
def workshop_robotic():
    return render_template("Festiora/workshop_robotic.html")

@app.route("/festiora/basket")
def basket():
    return render_template("Festiora/basket.html")

# ===============================
# ROUTE POST UNTUK FORM FESTIORA
# ===============================
@app.route("/festiora_submit/<lomba>", methods=["POST"])
def festiora_submit(lomba):
    data = request.form.to_dict()

    # ===============================
    # Tentukan sheet dan row per lomba
    # ===============================
    if lomba == "follow_the_harmony":
        ws = sh.worksheet("Follow The Harmony")
        row = [
            data.get("peserta1",""),
            data.get("peserta2",""),
            data.get("peserta3",""),
            data.get("kelas",""),
            data.get("idline","")
        ]
    elif lomba == "speed_drawing":
        ws = sh.worksheet("Speed Drawing")
        row = [
            data.get("peserta1",""),
            data.get("peserta2",""),
            data.get("peserta3",""),
            data.get("kelas",""),
            data.get("idline","")
        ]
    elif lomba == "trivia_showdown":
        ws = sh.worksheet("Trivia Showdown")
        row = [
            data.get("peserta1",""),
            data.get("peserta2",""),
            data.get("peserta3",""),
            data.get("kelas",""),
            data.get("idline","")
        ]
    elif lomba == "real_life_boardgame":
        ws = sh.worksheet("Real life boardgame")
        row = [
            data.get("peserta",""),
            data.get("kelas",""),
            data.get("idline","")
        ]
    elif lomba == "workshop_robotic":
        ws = sh.worksheet("Workshop Robotic")
        row = [
            data.get("peserta",""),
            data.get("kelas",""),
            data.get("idline","")
        ]
    elif lomba == "triquest":
        ws = sh.worksheet("TriQuest")
        row = [
            data.get("kapten",""),
            data.get("idline_kapten",""),
            data.get("anggota1",""),
            data.get("idline_anggota1",""),
            data.get("anggota2",""),
            data.get("idline_anggota2",""),
            data.get("anggota3",""),
            data.get("idline_anggota3",""),
            data.get("anggota4",""),
            data.get("idline_anggota4",""),
            data.get("kelas","")
        ]
    elif lomba == "mlbb":
        ws = sh.worksheet("Lomba E-Sport (MLBB)")
        row = [
            data.get("kapten",""),
            data.get("idline_kapten",""),
            data.get("anggota1",""),
            data.get("idline_anggota1",""),
            data.get("anggota2",""),
            data.get("idline_anggota2",""),
            data.get("anggota3",""),
            data.get("idline_anggota3",""),
            data.get("anggota4",""),
            data.get("idline_anggota4",""),
            data.get("kelas","")
        ]
    elif lomba == "case_crackers":
        ws = sh.worksheet("Case Crackers")
        row = [
            data.get("kelompok",""),
            data.get("ketua",""),
            data.get("idline_ketua",""),
            data.get("anggota1",""),
            data.get("idline_anggota1",""),
            data.get("anggota2",""),
            data.get("idline_anggota2",""),
            data.get("anggota3",""),
            data.get("idline_anggota3","")
        ]
    elif lomba == "family_100":
        ws = sh.worksheet("Family 100")
        row = [
            data.get("kelas",""),
            data.get("ketua",""),
            data.get("idline_ketua",""),
            data.get("anggota1",""),
            data.get("idline_anggota1",""),
            data.get("anggota2",""),
            data.get("idline_anggota2",""),
            data.get("anggota3",""),
            data.get("idline_anggota3",""),
            data.get("anggota4",""),
            data.get("idline_anggota4","")
        ]
    elif lomba == "basket":
        ws = sh.worksheet("Basket")
        row = [
            data.get("ketua",""),
            data.get("idline_ketua",""),
            data.get("anggota1",""),
            data.get("idline_anggota1",""),
            data.get("anggota2",""),
            data.get("idline_anggota2",""),
            data.get("cadangan",""),
            data.get("idline_cadangan",""),
            data.get("kelas","")
        ]
    else:
        return jsonify({"status":"error","message":"Lomba tidak dikenali"}), 400

    # ===============================
    # Tambahkan data ke sheet
    # ===============================
    try:
        ws.append_row(row)
        return jsonify({"status":"ok"})
    except Exception as e:
        print("Error:", e)
        return jsonify({"status":"error","message":str(e)}), 500

# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
