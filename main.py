from flask import Flask, render_template, request, redirect, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
import json
import os
import re

# --- Google Sheets Setup ---
with open("credentials.json") as f:
    SERVICE_ACCOUNT_INFO = json.load(f)

# Ruang lingkup izin untuk Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Buat credentials dan client
creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
client = gspread.authorize(creds)

# ID spreadsheet utama (pastikan diisi benar)
SPREADSHEET_ID = "1FZEjJ8x5QDow7VtK1zHmy6kziHpshq_Es22Nvtcy2tM"


SHEET_URLS = {
    "totebag": "https://docs.google.com/spreadsheets/d/1FZEjJ8x5QDow7VtK1zHmy6kziHpshq_Es22Nvtcy2tM/edit?gid=1916165016#gid=1916165016",
    "debat": "https://docs.google.com/spreadsheets/d/1FZEjJ8x5QDow7VtK1zHmy6kziHpshq_Es22Nvtcy2tM/edit?gid=1294090782#gid=1294090782",
    "workshop_calligraphy_sesi1": "https://docs.google.com/spreadsheets/d/1FZEjJ8x5QDow7VtK1zHmy6kziHpshq_Es22Nvtcy2tM/edit?gid=497107046#gid=497107046",
    "workshop_calligraphy_sesi2": "https://docs.google.com/spreadsheets/d/1FZEjJ8x5QDow7VtK1zHmy6kziHpshq_Es22Nvtcy2tM/edit?gid=932272936#gid=932272936",
    "workshop_daur_ulang": "https://docs.google.com/spreadsheets/d/1FZEjJ8x5QDow7VtK1zHmy6kziHpshq_Es22Nvtcy2tM/edit?gid=1994986451#gid=1994986451"
}

# Kuota maksimum tiap kegiatan
LIMITS = {
    "totebag": 10,
    "debat": 16,
    "workshop_calligraphy_sesi1": 8,
    "workshop_calligraphy_sesi2": 8,
    "workshop_daur_ulang": 30
}

app = Flask(__name__)

def cek_kuota(event_name):
    try:
        sheet_url = SHEET_URLS[event_name]
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        sheet_gid = sheet_url.split("gid=")[1]
        sheet = client.open_by_key(sheet_id).get_worksheet_by_id(int(sheet_gid))
        existing_records = sheet.get_all_records()
        return len(existing_records) < LIMITS[event_name]
    except Exception as e:
        print(f"⚠️ Gagal memeriksa kuota {event_name}: {e}")
        return False
    
def get_sheet_data(sheet_name):
    try:
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(sheet_name)
        records = sheet.get_all_records()
        return records
    except Exception as e:
        print("Gagal membaca sheet:", e)
        return []



def load_line_groups():
    with open('line_groups.json', 'r') as f:
        return json.load(f)

def extract_spreadsheet_id(url):
    """Extract spreadsheet ID from Google Sheets URL"""
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if match:
        return match.group(1)
    return url  # If already an ID, return as is

def get_google_sheets_client():
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPE)
    return gspread.authorize(creds)


def simpan_ke_google_sheets(sheet_name, data):
    try:
        # Pastikan sheet terdaftar
        if sheet_name not in SHEET_URLS:
            raise ValueError(f"Sheet '{sheet_name}' tidak ditemukan di konfigurasi SHEET_URLS")

        client = get_google_sheets_client()

        # Ambil spreadsheet ID & gid dari URL
        sheet_url = SHEET_URLS[sheet_name]
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        spreadsheet = client.open_by_key(sheet_id)

        # Buka worksheet berdasarkan gid
        gid_part = sheet_url.split("gid=")[1]
        worksheet = None
        for ws in spreadsheet.worksheets():
            if str(ws.id) == gid_part:
                worksheet = ws
                break
        if not worksheet:
            raise ValueError(f"Tidak menemukan worksheet dengan gid {gid_part}")

        # Cek jumlah peserta saat ini
        records = worksheet.get_all_values()
        jumlah_peserta = len(records) - 1 if records else 0  # kurangi header

        # Batasan
        limit = LIMITS.get(sheet_name, None)
        if limit and jumlah_peserta >= limit:
            print(f"❌ Kuota {sheet_name} sudah penuh ({limit} orang).")
            return False

        # Simpan ke sheet
        worksheet.append_row(list(data.values()))
        print(f"✅ Data berhasil ditambahkan ke {sheet_name}")
        return True

    except Exception as e:
        print(f"❌ Error saving to Google Sheets ({sheet_name}):\n{e}")
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


@app.route("/meloria/totebag", methods=["GET", "POST"])
def lomba_totebag():
    if request.method == "POST":
        # Ambil data dari form
        nama_tim = request.form.get("nama_tim")
        nama1 = request.form.get("nama1")
        kelas1 = request.form.get("kelas1")
        idline1 = request.form.get("idline1")
        nama2 = request.form.get("nama2")
        kelas2 = request.form.get("kelas2")
        idline2 = request.form.get("idline2")

        # Buat dict untuk disimpan ke Google Sheets
        data = {
            "Nama Tim": nama_tim,
            "Nama Peserta 1": nama1,
            "Kelas Peserta 1": kelas1,
            "ID Line Peserta 1": idline1,
            "Nama Peserta 2": nama2,
            "Kelas Peserta 2": kelas2,
            "ID Line Peserta 2": idline2
        }

        # 🔹 Ambil sheet ID & GID dengan benar (hapus karakter '#' jika ada)
        sheet_url = SHEET_URLS["totebag"]
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        sheet_gid = sheet_url.split("gid=")[1].split("#")[0]

        try:
            sheet = client.open_by_key(sheet_id).get_worksheet_by_id(int(sheet_gid))
        except Exception as e:
            return jsonify({"success": False, "message": f"Gagal membuka Google Sheet: {str(e)}"}), 500

        # 🔹 Cek jumlah peserta yang sudah terdaftar
        try:
            existing_records = sheet.get_all_records()
            if len(existing_records) >= LIMITS["totebag"]:
                return jsonify({
                    "success": False,
                    "message": "Kuota lomba Totebag sudah penuh!"
                }), 400
        except Exception as e:
            return jsonify({"success": False, "message": f"Gagal membaca data sheet: {str(e)}"}), 500

        # 🔹 Simpan ke Google Sheets
        if simpan_ke_google_sheets("totebag", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("totebag", "")
            })
        else:
            return jsonify({"success": False, "message": "Gagal menyimpan ke Google Sheets"}), 500

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
            "Nama 1": request.form["nama1"],
            "Kelas 1": request.form["kelas1"],
            "ID Line 1": request.form["idline1"],
            "Nama 2": request.form["nama2"],
            "Kelas 2": request.form["kelas2"],
            "ID Line 2": request.form["idline2"],
            "Nama 3": request.form["nama3"],
            "Kelas 3": request.form["kelas3"],
            "ID Line 3": request.form["idline3"]
        }

        # 🔹 Cek limit tim
        sheet_name = "debat_bahasa_inggris"
        max_tim = 10  # maksimal 10 tim

        sheet_data = get_sheet_data(sheet_name)
        if len(sheet_data) >= max_tim:
            return jsonify({"success": False, "message": "Kuota Penuh"}), 400

        # 🔹 Simpan data
        if simpan_ke_google_sheets(sheet_name, data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("debat_bahasa_inggris", "")
            })
        return jsonify({"success": False, "message": "Gagal menyimpan ke Google Sheets"}), 500

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
        # Ambil data dari form
        nama = request.form.get("nama")
        kelas = request.form.get("kelas")
        id_line = request.form.get("idline")

        # Pastikan semua field terisi
        if not nama or not kelas or not id_line:
            return jsonify({"success": False, "message": "Semua field wajib diisi"}), 400

        # Siapkan data untuk disimpan
        data = {
            "Nama": nama,
            "Kelas": kelas,
            "ID Line": id_line
        }

        # 🔹 Ambil sheet ID & GID dari SHEET_URLS
        sheet_url = SHEET_URLS["workshop_daur_ulang"]
        sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        sheet_gid = sheet_url.split("gid=")[1].split("#")[0]

        try:
            sheet = client.open_by_key(sheet_id).get_worksheet_by_id(int(sheet_gid))
        except Exception as e:
            return jsonify({"success": False, "message": f"Gagal membuka Google Sheet: {str(e)}"}), 500

        # 🔹 Cek jumlah peserta yang sudah terdaftar
        existing_records = sheet.get_all_records()
        if len(existing_records) >= LIMITS["workshop_daur_ulang"]:
            return jsonify({"success": False, "message": "Kuota Workshop Daur Ulang sudah penuh!"}), 400

        # 🔹 Simpan ke Google Sheets
        if simpan_ke_google_sheets("workshop_daur_ulang", data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("workshop_daur_ulang", "")
            })
        else:
            return jsonify({"success": False, "message": "Gagal menyimpan ke Google Sheets"}), 500

    # GET request → render halaman
    return render_template("meloria/workshop_daur_ulang.html")


@app.route("/meloria/workshop_calligraphy", methods=["GET", "POST"])
def workshop_calligraphy():
    if request.method == "POST":
        nama = request.form.get("nama")
        kelas = request.form.get("kelas")
        id_line = request.form.get("idline")
        sesi = request.form.get("sesi")

        if not nama or not kelas or not id_line or not sesi:
            return jsonify({"success": False, "message": "Semua field wajib diisi"}), 400

        data = {
            "Nama": nama,
            "Kelas": kelas,
            "ID Line": id_line,
            "Sesi": sesi
        }

        # 🔹 Cek limit peserta
        sheet_name = "workshop_calligraphy"
        max_per_sesi = 8

        # Ambil data dari sheet
        sheet_data = get_sheet_data(sheet_name)
        jumlah_sesi_1 = sum(1 for row in sheet_data if row.get("Sesi") == "Sesi 1 (08:00 - 09:30)")
        jumlah_sesi_2 = sum(1 for row in sheet_data if row.get("Sesi") == "Sesi 2 (10:15 - 11:45)")

        if sesi == "Sesi 1 (08:00 - 09:30)" and jumlah_sesi_1 >= max_per_sesi:
            return jsonify({"success": False, "message": "Sesi 1 sudah penuh"}), 400
        elif sesi == "Sesi 2 (10:15 - 11:45)" and jumlah_sesi_2 >= max_per_sesi:
            return jsonify({"success": False, "message": "Sesi 2 sudah penuh"}), 400

        if simpan_ke_google_sheets(sheet_name, data):
            line_groups = load_line_groups()
            return jsonify({
                "success": True,
                "line_link": line_groups.get("workshop_calligraphy", "")
            })
        else:
            return jsonify({"success": False, "message": "Gagal menyimpan ke Google Sheets"}), 500

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


def extract_spreadsheet_id(url):
    """Extract spreadsheet ID from Google Sheets URL"""
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
    if match:
        return match.group(1)
    return url  # If already an ID, return as is


def get_google_sheets_client():
    """Return authorized gspread client"""
    try:
        # Ambil credential dari .env
        credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        if not credentials_json:
            raise Exception("❌ GOOGLE_SHEETS_CREDENTIALS belum diset di .env")

        creds_dict = json.loads(credentials_json)

        # Scope modern (disarankan)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except json.JSONDecodeError:
        raise Exception("❌ GOOGLE_SHEETS_CREDENTIALS bukan JSON yang valid")
    except Exception as e:
        raise Exception(f"❌ Error in get_google_sheets_client(): {e}")


def simpan_ke_google_sheets(sheet_name, data):
    """Save registration data to a specific sheet in the spreadsheet"""
    try:
        client = get_google_sheets_client()
        spreadsheet_url = os.getenv("GOOGLE_SPREADSHEET_URL", "").strip()

        if not spreadsheet_url:
            raise Exception("❌ GOOGLE_SPREADSHEET_URL tidak diset di .env")

        # Ambil spreadsheet ID dari URL atau langsung ID
        spreadsheet_id = extract_spreadsheet_id(spreadsheet_url)
        spreadsheet = client.open_by_key(spreadsheet_id)

        # Coba buka worksheet
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            # Pastikan header ada
            if worksheet.row_count == 0 or not worksheet.row_values(1):
                worksheet.append_row(list(data.keys()))
        except gspread.exceptions.WorksheetNotFound:
            # Buat worksheet baru kalau belum ada
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            worksheet.append_row(list(data.keys()))

        # Tambah data ke baris baru
        worksheet.append_row(list(data.values()))
        print(f"✅ Data berhasil disimpan ke sheet: {sheet_name}")
        return True

    except Exception as e:
        print(f"❌ Error saving to Google Sheets ({sheet_name}): {e}")
        return False

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)