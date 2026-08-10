from flask import Flask, Response, make_response, render_template, request, jsonify, abort, session, redirect, url_for
from dotenv import load_dotenv
import os
import random
import json
import csv
import io
import re
from datetime import datetime
# import gspread  # Disabled temporarily (Recruitment migration)
# from google.oauth2.service_account import Credentials  # Disabled temporarily (Recruitment migration)

# Load environment variables FIRST
load_dotenv()

from salvatore_sheets import save_registration, get_registration_count, get_google_sheets_client, SHEETS, PARTICIPANT_LIMITS
from nusakarsa_sheets import save_registration, get_registration_count, get_google_sheets_client, SHEETS, PARTICIPANT_LIMITS
from ravenith_config import (
    RAVENITH_APPS_SCRIPT_URL,
    RAVENITH_BANNER,
    RAVENITH_COMPETITIONS,
    RAVENITH_LOMBA_ORDER,
    RAVENITH_POSTER_DIR,
)
from photobooth_config import PHOTOBOOTH_BANNER, PHOTOBOOTH_PAGE_SIZE
from services.google_drive import get_photos, search_photos, clear_cache, fetch_drive_image
from services.google_sheets import submit_recruitment
from recruitment_config import (
    RECRUITMENT_STATUS, AUTOSAVE_DELAY, ENABLE_DUPLICATE_CHECK, VALID_SCHOOLS,
    get_progress_dir, load_school_json,
)
from recruitment_helpers import (
    ProgressManager, ValidationHelper, ConfigLoader,
)

app = Flask(__name__)
app.secret_key = 'mpls_igs_2026_secret_key_for_session_management'

# ===============================
# CONFIG
# ===============================
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload
# app.config['UPLOAD_FOLDER'] = 'static/uploads/valentine'  # Disabled temporarily (Recruitment migration)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}

# ===============================
# FEATURE FLAGS
# ===============================
# Set True untuk menampilkan QR Code absensi di halaman cek data siswa,
# Set False untuk menyembunyikannya (ubah di sini, bukan di frontend)
SHOW_QRIS = True

# MPLS Configuration
MPLS_CONFIG = {
    "start_date": "2026-07-01",
    "end_date": "2026-07-07",
    "holidays": ["2026-07-04", "2026-07-05"],  # Sabtu & Minggu
    "event_days": ["2026-07-01", "2026-07-02", "2026-07-03", "2026-07-06", "2026-07-07"]
}

def get_mpls_config():
    return MPLS_CONFIG

def is_valid_mpls_date(date_str):
    """Check if date is within MPLS event days (excluding holidays)"""
    return date_str in MPLS_CONFIG["event_days"]

def get_mpls_days():
    """Get all valid MPLS event days"""
    return MPLS_CONFIG["event_days"]

# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Disabled temporarily (Recruitment migration)

def get_recruit_progress(school_key=None):
    return ProgressManager(progress_dir=get_progress_dir(school_key))

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ===============================
# GOOGLE SHEETS  # Disabled temporarily (Recruitment migration)
# ===============================
# scope = [
#     "https://www.googleapis.com/auth/spreadsheets",
#     "https://www.googleapis.com/auth/drive"
# ]
#
# creds = Credentials.from_service_account_file(
#     "valentine-sheet.json", scopes=scope
# )
# client = gspread.authorize(creds)
# sheet = client.open("Valentine_Order").sheet1
# Disabled temporarily (Recruitment migration)

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

# @app.route("/cupids_corner")  # Disabled temporarily (Recruitment migration)
# def cupids_corner():
#     return "Temporarily Disabled", 404

@app.route("/atthaira")
def atthaira():
    return render_template("e_atthaira_regist.html")

@app.route("/salvatore")
def salvatore():
    return render_template("e_salvatore.html")

# ===============================
# NUSAKARSA
# ===============================

@app.route("/nusakarsa")
def nusakarsa():
    return render_template("e_nusakarsa.html")

NUSAKARSA_COMPETITIONS = {
    "balon_berantai": "e_nusakarsa/balon_berantai.html",
    "mystery_mission": "e_nusakarsa/mystery_mission.html",
    "makan_kerupuk": "e_nusakarsa/makan_kerupuk.html",
    "poster": "e_nusakarsa/poster.html",
    "fashion_show": "e_nusakarsa/fashion_show.html",
    "sarung_sigap": "e_nusakarsa/sarung_sigap.html",
    "tri_lomba": "e_nusakarsa/tri_lomba.html",
    "got_talent_nusantara": "e_nusakarsa/got_talent_nusantara.html",
    "hias_bekal": "e_nusakarsa/hias_bekal.html",
    "jejak_juang_cerdas": "e_nusakarsa/jejak_juang_cerdas.html",
}

@app.route("/balon_berantai")
def balon_berantai():
    return render_template(NUSAKARSA_COMPETITIONS["balon_berantai"])

@app.route("/mystery_mission")
def mystery_mission():
    return render_template(NUSAKARSA_COMPETITIONS["mystery_mission"])

@app.route("/makan_kerupuk")
def makan_kerupuk():
    return render_template(NUSAKARSA_COMPETITIONS["makan_kerupuk"])

@app.route("/poster")
def poster():
    return render_template(NUSAKARSA_COMPETITIONS["poster"])

@app.route("/fashion_show")
def fashion_show():
    return render_template(NUSAKARSA_COMPETITIONS["fashion_show"])

@app.route("/sarung_sigap")
def sarung_sigap():
    return render_template(NUSAKARSA_COMPETITIONS["sarung_sigap"])

@app.route("/tri_lomba")
def tri_lomba():
    return render_template(NUSAKARSA_COMPETITIONS["tri_lomba"])

@app.route("/got_talent_nusantara")
def got_talent_nusantara():
    return render_template(NUSAKARSA_COMPETITIONS["got_talent_nusantara"])

@app.route("/jejak_juang_cerdas")
def jejak_juang_cerdas():
    return render_template(NUSAKARSA_COMPETITIONS["jejak_juang_cerdas"])

@app.route("/hias_bekal")
def hias_bekal():
    return render_template(NUSAKARSA_COMPETITIONS["hias_bekal"])

@app.route("/nusantara_in_colors")
def nusantara_in_colors():
    return render_template("e_nusakarsa/nusantara_in_colors.html")

@app.route("/register/<competition>", methods=["POST"])
def register_competition(competition):
    try:
        data = request.form.to_dict()
        with open('nusakarsa_debug.log', 'a') as f:
            f.write(f"[REGISTER] Competition: {competition}\n")
            f.write(f"[REGISTER] Data: {data}\n")
        result = save_registration(competition, data)
        with open('nusakarsa_debug.log', 'a') as f:
            f.write(f"[REGISTER] Result: {result}\n")
        
        if result == "limit_reached":
            return jsonify({"success": False, "message": "Sorry, the registration limit for this competition has been reached."}), 400
        elif result:
            return jsonify({"success": True, "message": "Registration successful!"})
        else:
            return jsonify({"success": False, "message": "Failed to save registration to spreadsheet."}), 500
    except Exception as e:
        with open('nusakarsa_debug.log', 'a') as f:
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


@app.route("/ravenith/photobooth")
def photobooth_page():
    return render_template(
        "photobooth/index.html",
        banner_file=PHOTOBOOTH_BANNER,
        api_photos_url="/api/photobooth/photos",
        page_size=PHOTOBOOTH_PAGE_SIZE,
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


@app.route("/api/photobooth/photos")
def api_photobooth_photos():
    keyword = request.args.get("q", "").strip()
    force = request.args.get("refresh") == "1"
    if keyword:
        result = search_photos(keyword, force_refresh=force)
    else:
        result = get_photos(force_refresh=force)
    return jsonify(result)


@app.route("/api/photobooth/image/<file_id>")
def api_photobooth_image(file_id):
    """Proxy gambar Drive agar bisa ditampilkan di <img> (hotlink Drive sering gagal)."""
    fetched = fetch_drive_image(file_id)
    if not fetched:
        abort(404)
    data, mime = fetched
    return Response(
        data,
        mimetype=mime,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@app.route("/api/photobooth/refresh", methods=["POST"])
def api_photobooth_refresh():
    clear_cache()
    return jsonify({"success": True, "message": "Cache cleared."})


# =============================== 
# API ROUTES
# ===============================

# === Reused for Nusakarsa ===
# @app.route("/register/<competition>", methods=["POST"])
# def register_competition(competition):
#     try:
#         data = request.form.to_dict()
#         with open('salvatore_debug.log', 'a') as f:
#             f.write(f"[REGISTER] Competition: {competition}\n")
#             f.write(f"[REGISTER] Data: {data}\n")
#         result = save_registration(competition, data)
#         with open('salvatore_debug.log', 'a') as f:
#             f.write(f"[REGISTER] Result: {result}\n")
        
#         if result == "limit_reached":
#             return jsonify({"success": False, "message": "Sorry, the registration limit for this competition has been reached."}), 400
#         elif result:
#             return jsonify({"success": True, "message": "Registration successful!"})
#         else:
#             return jsonify({"success": False, "message": "Failed to save registration to spreadsheet."}), 500
#     except Exception as e:
#         with open('salvatore_debug.log', 'a') as f:
#             f.write(f"[REGISTER ERROR] {str(e)}\n")
#         return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# @app.route("/api/registration-status/<competition>")
# def get_registration_status(competition):
#     """Get current registration count and limit for a competition."""
#     try:
#         if competition not in SHEETS:
#             return jsonify({"error": "Unknown competition"}), 404
        
#         limit = PARTICIPANT_LIMITS.get(competition, 0)
#         try:
#             client = get_google_sheets_client()
#             current_count = get_registration_count(client, SHEETS[competition])
#         except Exception as e:
#             # If we can't get the count, return limit as 0 (unlimited) to be safe
#             current_count = 0
        
#         return jsonify({
#             "competition": competition,
#             "current_count": current_count,
#             "limit": limit,
#             "spots_left": max(0, limit - current_count) if limit > 0 else -1,  # -1 means unlimited
#             "is_full": limit > 0 and current_count >= limit
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/valentine_order", methods=["POST"])  # Disabled temporarily (Recruitment migration)
# def valentine_order():
#     try:
#         # Get form data
#         name = request.form.get("name")
#         message = request.form.get("message")
#         file = request.files.get("file")

#         # Save file if uploaded
#         file_path = None
#         if file and allowed_file(file.filename):
#             filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)

#         # Prepare data for sheets
#         row_data = [
#             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             name,
#             message,
#             file_path or ""
#         ]

#         # Append to sheet
#         sheet.append_row(row_data)

#         return jsonify({"success": True, "message": "Order submitted successfully!"})

#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500
# Disabled temporarily (Recruitment migration)

# ===============================
# STUDENTS & ATTENDANCE SYSTEM
# ===============================

STUDENTS_FILE = os.path.join(app.static_folder, 'data', 'students.json')
ATTENDANCE_FILE = os.path.join(app.static_folder, 'data', 'attendance.json')
MENTORS_FILE = os.path.join(app.static_folder, 'data', 'mentors.json')

os.makedirs(os.path.join(app.static_folder, 'data'), exist_ok=True)

def load_json_file(file_path, default_val):
    if not os.path.exists(file_path):
        return default_val
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_val

def save_json_file(file_path, data):
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False

def find_student(students, student_id):
    for s in students:
        if s.get("id") == student_id:
            return s
    return None

def get_mentor_name(kelompok, sekolah):
    mentors = load_json_file(MENTORS_FILE, {})
    return mentors.get(sekolah, {}).get(kelompok, {}).get("name", "Belum ditentukan")

def get_attendance_status(student_id, date_str, attendance_list):
    for a in attendance_list:
        if a.get("student_id") == student_id and a.get("date") == date_str:
            return "Hadir", a.get("timestamp", "")
    today = datetime.now().strftime("%Y-%m-%d")
    if date_str < today:
        return "Tidak Hadir", ""
    elif date_str == today:
        return "Belum Absen", ""
    else:
        return "-", ""

def get_student_5day(student_id, attendance_list, mpls_days):
    result = []
    for day in mpls_days:
        status, ts = get_attendance_status(student_id, day, attendance_list)
        result.append({"date": day, "status": status, "timestamp": ts})
    return result

@app.route("/cek_data_siswa2026")
def cek_data_siswa_page():
    return render_template("cek_data_siswa2026.html", show_qris=SHOW_QRIS)

@app.route("/scanner")
def scanner_page():
    return render_template("scanner.html")

@app.route("/admin")
def admin_page():
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    return render_template("admin.html")

@app.route("/admin/login")
def admin_login():
    return render_template("admin_login.html")

@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username == 'osismpls' and password == 'OSISMPLS123':
        session['admin_authenticated'] = True
        return jsonify({"success": True, "message": "Login berhasil"})
    else:
        return jsonify({"success": False, "message": "Username atau password salah"}), 401

@app.route("/api/admin/check-auth")
def api_admin_check_auth():
    return jsonify({"authenticated": session.get('admin_authenticated', False)})

@app.route("/api/admin/logout", methods=["POST"])
def api_admin_logout():
    session.pop('admin_authenticated', None)
    return jsonify({"success": True, "message": "Logout berhasil"})

@app.route("/api/students/search")
def api_students_search():
    query = request.args.get("q", "").strip().lower()
    if not query:
        return jsonify([])
    students = load_json_file(STUDENTS_FILE, [])
    matches = []
    for s in students:
        if s.get("nama", "").strip().lower() == query:
            matches.append({
                "id": s.get("id"),
                "nama": s.get("nama"),
                "kelas": s.get("kelas"),
                "sekolah": s.get("sekolah"),
                "kelompok": s.get("kelompok")
            })
    return jsonify(matches[:1])

@app.route("/api/students/<student_id>")
def api_student_detail(student_id):
    students = load_json_file(STUDENTS_FILE, [])
    student = find_student(students, student_id)
    if not student:
        return jsonify({"success": False, "message": "Siswa tidak ditemukan"}), 404

    attendance = load_json_file(ATTENDANCE_FILE, [])
    mpls_days = get_mpls_days()
    five_day = get_student_5day(student_id, attendance, mpls_days)
    total_hadir = sum(1 for d in five_day if d['status'] == 'Hadir')

    return jsonify({
        "success": True,
        "student": {
            "id": student.get("id"),
            "nama": student.get("nama"),
            "kelas": student.get("kelas"),
            "sekolah": student.get("sekolah"),
            "kelompok": student.get("kelompok"),
            "mentor": get_mentor_name(student.get("kelompok", ""), student.get("sekolah")),
            "attendance_5day": five_day,
            "total_hadir": total_hadir,
            "total_days": len(mpls_days)
        }
    })

@app.route("/api/attendance/checkin", methods=["POST"])
def api_attendance_checkin():
    if request.is_json:
        data = request.get_json(silent=True) or {}
        student_id = data.get("student_id")
    else:
        student_id = request.form.get("student_id")

    if not student_id:
        try:
            raw_data = request.data.decode('utf-8').strip()
            if raw_data.startswith("STUDENT_"):
                student_id = raw_data
        except Exception:
            pass

    if not student_id:
        return jsonify({"success": False, "message": "ID Siswa diperlukan"}), 400

    students = load_json_file(STUDENTS_FILE, [])
    student = find_student(students, student_id)
    if not student:
        return jsonify({"success": False, "message": "Siswa tidak terdaftar"}), 404

    today = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not is_valid_mpls_date(today):
        return jsonify({
            "success": False,
            "message": f"Hari ini ({today}) bukan hari kegiatan MPLS atau hari libur."
        }), 400

    attendance = load_json_file(ATTENDANCE_FILE, [])

    for a in attendance:
        if a.get("student_id") == student_id and a.get("date") == today:
            return jsonify({
                "success": True,
                "message": f"{student.get('nama')} sudah absen hari ini.",
                "student": {
                    "nama": student.get("nama"),
                    "kelas": student.get("kelas"),
                    "sekolah": student.get("sekolah"),
                    "kelompok": student.get("kelompok"),
                    "mentor": get_mentor_name(student.get("kelompok", ""), student.get("sekolah")),
                    "checkin_time": a.get("timestamp"),
                    "date": a.get("date")
                }
            })

    new_record = {
        "student_id": student_id,
        "nama": student.get("nama"),
        "kelas": student.get("kelas"),
        "sekolah": student.get("sekolah"),
        "kelompok": student.get("kelompok"),
        "date": today,
        "timestamp": now_str
    }
    attendance.append(new_record)
    save_json_file(ATTENDANCE_FILE, attendance)

    return jsonify({
        "success": True,
        "message": f"Absen berhasil untuk {student.get('nama')}!",
        "student": {
            "nama": student.get("nama"),
            "kelas": student.get("kelas"),
            "sekolah": student.get("sekolah"),
            "kelompok": student.get("kelompok"),
            "mentor": get_mentor_name(student.get("kelompok", ""), student.get("sekolah")),
            "checkin_time": now_str,
            "date": today
        }
    })

@app.route("/api/admin/students", methods=["GET"])
def api_admin_students():
    students = load_json_file(STUDENTS_FILE, [])
    result = []
    for s in students:
        result.append({
            "id": s.get("id"),
            "nama": s.get("nama"),
            "kelas": s.get("kelas"),
            "sekolah": s.get("sekolah"),
            "kelompok": s.get("kelompok"),
            "mentor": get_mentor_name(s.get("kelompok", ""), s.get("sekolah"))
        })
    return jsonify(result)

@app.route("/api/admin/students/detail", methods=["GET"])
def api_admin_students_detail():
    students = load_json_file(STUDENTS_FILE, [])
    attendance = load_json_file(ATTENDANCE_FILE, [])
    mpls_days = get_mpls_days()
    result = []
    for s in students:
        five_day = get_student_5day(s["id"], attendance, mpls_days)
        result.append({
            "id": s.get("id"),
            "nama": s.get("nama"),
            "kelas": s.get("kelas"),
            "sekolah": s.get("sekolah"),
            "kelompok": s.get("kelompok"),
            "mentor": get_mentor_name(s.get("kelompok", ""), s.get("sekolah")),
            "attendance_5day": five_day,
            "total_hadir": sum(1 for d in five_day if d['status'] == 'Hadir'),
            "total_days": len(mpls_days)
        })
    return jsonify(result)

@app.route("/api/admin/students/by-school", methods=["GET"])
def api_admin_students_by_school():
    """Return students grouped by school (CGC/Mayor) with attendance for new admin panel."""
    students = load_json_file(STUDENTS_FILE, [])
    attendance = load_json_file(ATTENDANCE_FILE, [])
    mpls_days = get_mpls_days()
    
    # Group students by school
    schools = {}
    
    for s in students:
        school = s.get("sekolah", "Lainnya")
        if school not in schools:
            schools[school] = []
        
        five_day = get_student_5day(s["id"], attendance, mpls_days)
        schools[school].append({
            "id": s.get("id"),
            "nama": s.get("nama"),
            "attendance_5day": five_day,
            "total_hadir": sum(1 for d in five_day if d['status'] == 'Hadir'),
            "total_days": len(mpls_days)
        })
    
    return jsonify({
        "success": True,
        "schools": schools,
        "mpls_days": mpls_days
    })

@app.route("/api/admin/students/upload", methods=["POST"])
def api_admin_students_upload():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Tidak ada file yang diunggah"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "Nama file kosong"}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"success": False, "message": "Hanya file CSV yang diperbolehkan"}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
        csv_reader = csv.reader(stream)

        headers = next(csv_reader, None)
        if not headers:
            return jsonify({"success": False, "message": "File CSV kosong"}), 400

        cleaned_headers = [h.strip().lower() for h in headers]
        idx_nama = -1
        idx_kelas = -1

        for idx, h in enumerate(cleaned_headers):
            if 'nama' in h:
                idx_nama = idx
            elif 'kelas' in h:
                idx_kelas = idx

        if idx_nama == -1 or idx_kelas == -1:
            return jsonify({
                "success": False,
                "message": f"Header CSV harus berisi Nama, Kelas. Ditemukan: {', '.join(headers)}"
            }), 400

        new_students = []
        import_count = 0

        for row in csv_reader:
            if not row or len(row) <= max(idx_nama, idx_kelas):
                continue
            nama = row[idx_nama].strip()
            if not nama:
                continue
            kelas = row[idx_kelas].strip()
            student_id = f"STUDENT_{import_count + 1:04d}_{int(random.random()*10000):04d}"
            new_students.append({
                "id": student_id,
                "nama": nama,
                "kelas": kelas
            })
            import_count += 1

        if not new_students:
            return jsonify({"success": False, "message": "Tidak ada data siswa valid ditemukan dalam file CSV"}), 400

        save_json_file(STUDENTS_FILE, new_students)
        save_json_file(ATTENDANCE_FILE, [])

        return jsonify({
            "success": True,
            "message": f"Berhasil mengimpor {import_count} data siswa dan mengosongkan log absensi sebelumnya."
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"Gagal memproses file CSV: {str(e)}"}), 500

@app.route("/api/admin/students/clear", methods=["POST"])
def api_admin_students_clear():
    save_json_file(STUDENTS_FILE, [])
    save_json_file(ATTENDANCE_FILE, [])
    return jsonify({"success": True, "message": "Database siswa dan absensi telah dikosongkan."})

@app.route("/api/admin/attendance/clear", methods=["POST"])
def api_admin_attendance_clear():
    save_json_file(ATTENDANCE_FILE, [])
    return jsonify({"success": True, "message": "Semua data kehadiran telah dikosongkan."})

@app.route("/api/admin/attendance/delete", methods=["POST"])
def api_admin_attendance_delete():
    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    date = data.get("date")
    if not student_id or not date:
        return jsonify({"success": False, "message": "student_id dan date diperlukan"}), 400
    attendance = load_json_file(ATTENDANCE_FILE, [])
    new_list = [a for a in attendance if not (a.get("student_id") == student_id and a.get("date") == date)]
    if len(new_list) == len(attendance):
        return jsonify({"success": False, "message": "Data tidak ditemukan"}), 404
    save_json_file(ATTENDANCE_FILE, new_list)
    return jsonify({"success": True, "message": "Data kehadiran berhasil dihapus."})

@app.route("/api/admin/attendance", methods=["GET"])
def api_admin_attendance():
    attendance = load_json_file(ATTENDANCE_FILE, [])
    date_filter = request.args.get("date", "")
    today = datetime.now().strftime("%Y-%m-%d")
    if not date_filter:
        date_filter = today

    filtered = [a for a in attendance if a.get("date") == date_filter]
    result = []
    for a in filtered:
        result.append({
            "student_id": a.get("student_id"),
            "nama": a.get("nama"),
            "kelas": a.get("kelas"),
            "sekolah": a.get("sekolah"),
            "kelompok": a.get("kelompok"),
            "date": a.get("date"),
            "timestamp": a.get("timestamp")
        })
    return jsonify(result)

@app.route("/api/admin/stats", methods=["GET"])
def api_admin_stats():
    students = load_json_file(STUDENTS_FILE, [])
    attendance = load_json_file(ATTENDANCE_FILE, [])
    mpls_days = get_mpls_days()

    # Per-date stats based on computed status
    date_stats = {}
    for day in mpls_days:
        hadir = 0
        for s in students:
            status, _ = get_attendance_status(s["id"], day, attendance)
            if status == "Hadir":
                hadir += 1
        date_stats[day] = {
            "total": len(students),
            "hadir": hadir,
            "tidak_hadir": len(students) - hadir
        }

    # Today's quick stats
    today = datetime.now().strftime("%Y-%m-%d")
    today_present = 0
    for a in attendance:
        if a.get("date") == today:
            today_present += 1

    return jsonify({
        "total_students": len(students),
        "total_present": today_present,
        "total_absent": max(0, len(students) - today_present),
        "percentage": round(today_present / len(students) * 100, 1) if students else 0,
        "date_stats": date_stats
    })

@app.route("/api/admin/attendance/export", methods=["GET"])
def api_admin_attendance_export():
    students = load_json_file(STUDENTS_FILE, [])
    attendance = load_json_file(ATTENDANCE_FILE, [])
    mpls_days = get_mpls_days()

    dest = io.StringIO()
    writer = csv.writer(dest)

    header_row = ["No", "Nama", "Sekolah", "Kelas", "Kelompok", "Mentor"]
    for i, day in enumerate(mpls_days, 1):
        header_row.append(f"Hari {i} ({day})")
    writer.writerow(header_row)

    for idx, s in enumerate(students, 1):
        row = [
            idx,
            s.get("nama"),
            s.get("sekolah"),
            s.get("kelas"),
            s.get("kelompok"),
            get_mentor_name(s.get("kelompok", ""), s.get("sekolah"))
        ]
        for day in mpls_days:
            status, ts = get_attendance_status(s["id"], day, attendance)
            if status == "Hadir" and ts:
                row.append(f"Hadir {ts.split()[-1]}")
            else:
                row.append(status)
        writer.writerow(row)

    output = make_response(dest.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=rekap_absensi_mpls_2026.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8-sig"
    return output

@app.route("/api/admin/student/<student_id>/attendance", methods=["GET"])
def api_student_attendance_detail(student_id):
    students = load_json_file(STUDENTS_FILE, [])
    student = find_student(students, student_id)
    if not student:
        return jsonify({"success": False, "message": "Siswa tidak ditemukan"}), 404

    attendance = load_json_file(ATTENDANCE_FILE, [])
    mpls_days = get_mpls_days()
    five_day = get_student_5day(student_id, attendance, mpls_days)

    return jsonify({
        "success": True,
        "student": {
            "id": student.get("id"),
            "nama": student.get("nama"),
            "kelas": student.get("kelas"),
            "sekolah": student.get("sekolah"),
            "kelompok": student.get("kelompok"),
            "mentor": get_mentor_name(student.get("kelompok", ""), student.get("sekolah"))
        },
        "mpls_config": MPLS_CONFIG,
        "attendance_summary": five_day,
        "total_hadir": sum(1 for d in five_day if d['status'] == 'Hadir'),
        "total_days": len(mpls_days)
    })

@app.route("/api/mpls/config", methods=["GET"])
def api_mpls_config():
    return jsonify({"success": True, "config": MPLS_CONFIG})

# ===============================
# RECRUITMENT
# ===============================

# ===============================
# RECRUITMENT HELPERS
# ===============================

def _recruit_school_from_url():
    path = request.path
    for s in VALID_SCHOOLS:
        if path.startswith(f"/recruitment-{s}"):
            return s
    return None


def _session_key(base, school):
    return f"{base}_{school}" if school else base


def _recruitment_open_required():
    if RECRUITMENT_STATUS != "open":
        return jsonify({"success": False, "message": "Pendaftaran sudah ditutup."}), 403
    return None


def _render_recruitment(school_key):
    school_cfg = ConfigLoader.get_school_config(school_key)
    if RECRUITMENT_STATUS == "closed":
        return render_template(
            "recruitment_closed.html",
            school_config=school_cfg,
            recruitment_api_prefix=f"/recruitment-{school_key}" if school_key else "/recruitment",
        )
    sekbid_list = ConfigLoader.get_sekbid_list(school_key)
    return render_template(
        "recruitment.html",
        sekbid_list=sekbid_list,
        autosave_delay=AUTOSAVE_DELAY,
        recruitment_api_prefix=f"/recruitment-{school_key}" if school_key else "/recruitment",
        school_config=school_cfg,
    )


# ===============================
# RECRUITMENT ROUTES
# ===============================

@app.route("/recruitment")
def recruitment_old():
    abort(404)


@app.route("/recruitment-sma-mayor")
def recruitment_sma_mayor():
    return _render_recruitment("sma-mayor")


@app.route("/recruitment-sma-cgc")
def recruitment_sma_cgc():
    return _render_recruitment("sma-cgc")


# --- Progress ---

@app.route("/recruitment-sma-mayor/progress")
@app.route("/recruitment-sma-cgc/progress")
def recruitment_progress():
    closed = _recruitment_open_required()
    if closed:
        return closed
    school = _recruit_school_from_url()
    sk = _session_key("recruit_session_id", school)
    session_id = session.get(sk)
    if not session_id:
        return jsonify({"success": False, "progress": None})
    pm = get_recruit_progress(school)
    data = pm.load(session_id)
    return jsonify({"success": True, "progress": data})


# --- Autosave ---

@app.route("/recruitment-sma-mayor/autosave", methods=["POST"])
@app.route("/recruitment-sma-cgc/autosave", methods=["POST"])
def recruitment_autosave():
    closed = _recruitment_open_required()
    if closed:
        return closed
    try:
        data = request.get_json()
        if not data or "progress" not in data:
            return jsonify({"success": False, "message": "No data"}), 400
        school = _recruit_school_from_url()
        sk = _session_key("recruit_session_id", school)
        session_id = session.get(sk)
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session[sk] = session_id
        pm = get_recruit_progress(school)
        pm.save(session_id, data["progress"])
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# --- Clear ---

@app.route("/recruitment-sma-mayor/clear", methods=["POST"])
@app.route("/recruitment-sma-cgc/clear", methods=["POST"])
def recruitment_clear():
    closed = _recruitment_open_required()
    if closed:
        return closed
    school = _recruit_school_from_url()
    sk = _session_key("recruit_session_id", school)
    session_id = session.get(sk)
    if session_id:
        pm = get_recruit_progress(school)
        pm.clear(session_id)
        session.pop(sk, None)
    return jsonify({"success": True})


# --- Submit ---

@app.route("/recruitment-sma-mayor/submit", methods=["POST"])
@app.route("/recruitment-sma-cgc/submit", methods=["POST"])
def recruitment_submit():
    closed = _recruitment_open_required()
    if closed:
        return closed
    try:
        school = _recruit_school_from_url()
        sk = _session_key("recruit_session_id", school)
        submitted_key = _session_key("recruit_submitted", school)

        session_id = session.get(sk)
        pm = get_recruit_progress(school)
        progress = pm.load(session_id) if session_id else None

        nama = request.form.get("nama") or (progress.get("nama") if progress else "")
        kelas = request.form.get("kelas") or (progress.get("kelas") if progress else "")
        sekbid_list = request.form.getlist("sekbid") or (progress.get("sekbid") if progress else [])
        if isinstance(sekbid_list, str):
            sekbid_list = [sekbid_list]
        visi_misi = request.form.get("visi_misi") or (progress.get("visi_misi") if progress else "")
        motivasi = request.form.get("motivasi") or (progress.get("motivasi") if progress else "")
        kelebihan = request.form.get("kelebihan") or (progress.get("kelebihan") if progress else "")
        kekurangan = request.form.get("kekurangan") or (progress.get("kekurangan") if progress else "")
        pengalaman = request.form.get("pengalaman") or (progress.get("pengalaman") if progress else "")
        prioritas = request.form.get("prioritas") or (progress.get("prioritas") if progress else "")
        google_drive_link = request.form.get("google_drive_link") or (progress.get("google_drive_link") if progress else "")
        sertifikat_link = request.form.get("sertifikat_link") or (progress.get("sertifikat_link") if progress else "")

        if ENABLE_DUPLICATE_CHECK and session.get(submitted_key):
            return jsonify({"success": False, "message": "Anda sudah melakukan pendaftaran sebelumnya. Tidak dapat mendaftar ulang."}), 400

        errors_step1 = ValidationHelper.validate_step1({"nama": nama, "kelas": kelas})
        if errors_step1:
            return jsonify({"success": False, "message": "Data diri tidak valid: " + "; ".join(errors_step1.values())}), 400

        errors_step2 = ValidationHelper.validate_step2({"sekbid": sekbid_list})
        if errors_step2:
            return jsonify({"success": False, "message": "Form tidak valid: " + "; ".join(errors_step2.values())}), 400

        errors_step3 = ValidationHelper.validate_step3({
            "visi_misi": visi_misi, "motivasi": motivasi,
            "kelebihan": kelebihan, "kekurangan": kekurangan,
            "prioritas": prioritas,
        })
        if errors_step3:
            return jsonify({"success": False, "message": "Pertanyaan umum tidak valid: " + "; ".join(errors_step3.values())}), 400

        errors_step4 = ValidationHelper.validate_step4({"google_drive_link": google_drive_link})
        if errors_step4:
            return jsonify({"success": False, "message": "Link Google Drive tidak valid: " + "; ".join(errors_step4.values())}), 400

        data = {
            "nama": nama,
            "kelas": kelas,
            "visi_misi": visi_misi,
            "motivasi": motivasi,
            "kelebihan": kelebihan,
            "kekurangan": kekurangan,
            "pengalaman": pengalaman,
            "prioritas": prioritas,
            "google_drive_link": google_drive_link,
            "sertifikat_link": sertifikat_link,
        }

        school_config = load_school_json(school)
        if not school_config:
            return jsonify({"success": False, "message": "Konfigurasi sekolah tidak ditemukan"}), 500

        sekbid_ids = []
        all_sekbid = school_config.get("sekbid", {})
        for item in sekbid_list:
            for key, val in all_sekbid.items():
                if val.get("id") == item:
                    sekbid_ids.append(val["id"])
                    break

        success, message = submit_recruitment(school_config, data, sekbid_ids or sekbid_list)
        if not success:
            return jsonify({"success": False, "message": message}), 500

        if ENABLE_DUPLICATE_CHECK:
            session[submitted_key] = True
        pm.clear(session_id)

        return jsonify({"success": True, "message": "Pendaftaran berhasil dikirim! Tim kami akan meninjau dan menghubungi Anda."})

    except Exception as e:
        return jsonify({"success": False, "message": "Terjadi kesalahan: " + str(e)}), 500


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
