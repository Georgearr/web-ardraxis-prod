from flask import Flask, render_template, request, redirect, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

app = Flask(__name__)

def load_line_groups():
    with open('line_groups.json', 'r') as f:
        return json.load(f)

def get_google_sheets_client():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]
    
    google_creds = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
    if google_creds:
        creds_dict = json.loads(google_creds)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    
    client = gspread.authorize(creds)
    return client

def simpan_ke_google_sheets(sheet_name, data):
    try:
        client = get_google_sheets_client()
        spreadsheet_name = os.getenv('GOOGLE_SPREADSHEET_NAME', 'Meloria Event Registration')
        spreadsheet = client.open(spreadsheet_name)
        
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            worksheet.append_row(list(data.keys()))
        
        worksheet.append_row(list(data.values()))
        return True
    except Exception as e:
        print(f"Error saving to Google Sheets: {e}")
        return False

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

@app.route("/meloria/bahasa_mandarin", methods=["GET", "POST"])
def bahasa_mandarin():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("bahasa_mandarin", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("bahasa_mandarin", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/bahasa_mandarin.html")


@app.route("/meloria/bahasa_prancis", methods=["GET", "POST"])
def bahasa_prancis():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("bahasa_prancis", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("bahasa_prancis", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/bahasa_prancis.html")

@app.route("/meloria/bahasa_jerman", methods=["GET", "POST"])
def bahasa_jerman():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("bahasa_jerman", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("bahasa_jerman", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/bahasa_jerman.html")


@app.route("/meloria/bahasa_jepang", methods=["GET", "POST"])
def bahasa_jepang():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("bahasa_jepang", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("bahasa_jepang", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/bahasa_jepang.html")



@app.route("/meloria/bahasa_korea", methods=["GET", "POST"])
def bahasa_korea():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("bahasa_korea", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("bahasa_korea", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/bahasa_korea.html")


@app.route("/meloria/bahasa_arab", methods=["GET", "POST"])
def bahasa_arab():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("bahasa_arab", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("bahasa_arab", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/bahasa_arab.html")


@app.route("/meloria/web_cloning", methods=["GET", "POST"])
def web_cloning():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("web_cloning", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("web_cloning", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/web_cloning.html")

@app.route("/meloria/membaca_puisi", methods=["GET", "POST"])
def membaca_puisi():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("membaca_puisi", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("membaca_puisi", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/membaca_puisi.html")


@app.route("/meloria/menghias_totebag", methods=["GET", "POST"])
def menghias_totebag():
    if request.method == "POST":
        data = {
            "Nama Tim": request.form["nama_tim"],
            "Nama1": request.form["nama1"],
            "Kelas1": request.form["kelas1"],
            "ID Line1": request.form["idline1"],
            "Nama2": request.form["nama2"],
            "Kelas2": request.form["kelas2"],
            "ID Line2": request.form["idline2"]
        }
        if simpan_ke_google_sheets("menghias_totebag", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("menghias_totebag", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/menghias_totebag.html")


@app.route("/meloria/debat_bahasa_indonesia", methods=["GET", "POST"])
def debat_bahasa_indonesia():
    if request.method == "POST":
        data = {
            "Nama1": request.form["nama1"],
            "Kelas1": request.form["kelas1"],
            "ID Line1": request.form["idline1"],
            "Nama2": request.form["nama2"],
            "Kelas2": request.form["kelas2"],
            "ID Line2": request.form["idline2"],
            "Nama3": request.form["nama3"],
            "Kelas3": request.form["kelas3"],
            "ID Line3": request.form["idline3"]
        }
        if simpan_ke_google_sheets("debat_bahasa_indonesia", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("debat_bahasa_indonesia", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/debat_bahasa_indonesia.html")


@app.route("/meloria/debat_bahasa_inggris", methods=["GET", "POST"])
def debat_bahasa_inggris():
    if request.method == "POST":
        data = {
            "Nama1": request.form["nama1"],
            "Kelas1": request.form["kelas1"],
            "ID Line1": request.form["idline1"],
            "Nama2": request.form["nama2"],
            "Kelas2": request.form["kelas2"],
            "ID Line2": request.form["idline2"],
            "Nama3": request.form["nama3"],
            "Kelas3": request.form["kelas3"],
            "ID Line3": request.form["idline3"]
        }
        if simpan_ke_google_sheets("debat_bahasa_inggris", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("debat_bahasa_inggris", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/debat_bahasa_inggris.html")


@app.route("/meloria/competitive_programming", methods=["GET", "POST"])
def competitive_programming():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("competitive_programming", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("competitive_programming", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/competitive_programming.html")


@app.route("/meloria/desain_infografis", methods=["GET", "POST"])
def desain_infografis():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("desain_infografis", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("desain_infografis", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/desain_infografis.html")


@app.route("/meloria/cosplay", methods=["GET", "POST"])
def cosplay():
    if request.method == "POST":
        data = {
            "Nama1": request.form["nama1"],
            "Kelas1": request.form["kelas1"],
            "Karakter1": request.form["karakter1"],
            "ID Line1": request.form["idline1"],
            "Nama2": request.form["nama2"],
            "Kelas2": request.form["kelas2"],
            "Karakter2": request.form["karakter2"],
            "ID Line2": request.form["idline2"],
            "Nama3": request.form["nama3"],
            "Kelas3": request.form["kelas3"],
            "Karakter3": request.form["karakter3"],
            "ID Line3": request.form["idline3"],
            "Nama4": request.form["nama4"],
            "Kelas4": request.form["kelas4"],
            "Karakter4": request.form["karakter4"],
            "ID Line4": request.form["idline4"]
        }
        if simpan_ke_google_sheets("cosplay", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("cosplay", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/cosplay.html")

@app.route("/meloria/cerdas_cermat", methods=["GET", "POST"])
def cerdas_cermat():
    if request.method == "POST":
        data = {
            "Nama Kapten": request.form["nama1"],
            "ID Line": request.form["idline1"],
            "Nama Anggota 1": request.form["nama2"],
            "ID Line 1": request.form["idline2"],
            "Nama Anggota 2": request.form["nama3"],
            "ID Line 2": request.form["idline3"],
            "Kelas": request.form["kelas"]
        }
        if simpan_ke_google_sheets("cerdas_cermat", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("cerdas_cermat", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/cerdas_cermat.html")

@app.route("/meloria/igs_got_talent", methods=["GET", "POST"])
def igs_got_talent():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"],
            "Jenis Talent": request.form["jenis_talent"],
            "Nama Anggota": request.form["nama_anggota"]
        }
        if simpan_ke_google_sheets("igs_got_talent", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("igs_got_talent", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/igs_got_talent.html")

@app.route("/meloria/workshop_daur_ulang", methods=["GET", "POST"])
def workshop_daur_ulang():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"]
        }
        if simpan_ke_google_sheets("workshop_daur_ulang", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("workshop_daur_ulang", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/workshop_daur_ulang.html")

@app.route("/meloria/workshop_calligraphy", methods=["GET", "POST"])
def workshop_calligraphy():
    if request.method == "POST":
        data = {
            "Nama": request.form["nama"],
            "Kelas": request.form["kelas"],
            "ID Line": request.form["idline"],
            "Sesi": request.form["sesi"]
        }
        if simpan_ke_google_sheets("workshop_calligraphy", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("workshop_calligraphy", "")
            })
        return jsonify({"success": False}), 500

    return render_template("meloria/workshop_calligraphy.html")


@app.route("/meloria/boardgames")
def boardgames():
    return render_template("meloria/boardgames.html")

@app.route("/meloria/noraebang")
def noraebang():
    return render_template("meloria/noraebang.html")

@app.route("/meloria/wordchain")
def wordchain():
    return render_template("meloria/wordchain.html")

@app.route("/meloria/mystery_color")
def mystery_color():
    return render_template("meloria/mystery_color.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
