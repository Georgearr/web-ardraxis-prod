from flask import Flask, Response, make_response, render_template, request, jsonify, abort, session, redirect, url_for
from dotenv import load_dotenv
import os
import random
import json
import csv
import io
import re
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
from photobooth_config import PHOTOBOOTH_BANNER, PHOTOBOOTH_PAGE_SIZE
from services.google_drive import get_photos, search_photos, clear_cache, fetch_drive_image

app = Flask(__name__)
app.secret_key = 'mpls_igs_2026_secret_key_for_session_management'

# ===============================
# CONFIG
# ===============================
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload
app.config['UPLOAD_FOLDER'] = 'static/uploads/valentine'
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}

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
            json.dump(data, f, indent=4)
        return True
    except Exception:
        return False

def get_student_mentor(student_jenis, student_kelompok, student_sub_kelompok):
    mentors = load_json_file(MENTORS_FILE, {})
    
    # Normalize types
    jenis = "Mayor" if student_jenis and "mayor" in student_jenis.lower() else "CGC"
    
    # Normalize kelompok: e.g. "Kelompok 1" -> extract 1 -> "Kelompok 1"
    kelompok_num = None
    if student_kelompok:
        match = re.search(r'\d+', str(student_kelompok))
        if match:
            kelompok_num = match.group(0)
            
    kelompok_key = f"Kelompok {kelompok_num}" if kelompok_num else str(student_kelompok).strip()
    sub_key = str(student_sub_kelompok).upper().strip() if student_sub_kelompok else "A"
    if sub_key not in ["A", "B"]:
        sub_key = "A" # fallback
        
    try:
        return mentors[jenis][kelompok_key][sub_key]['name']
    except KeyError:
        try:
            return mentors[jenis][kelompok_key][sub_key]
        except KeyError:
            return "Belum ditentukan"

@app.route("/cek_data_siswa2026")
def cek_data_siswa_page():
    return render_template("cek_data_siswa2026.html")

@app.route("/admin")
def admin_page():
    # Check if user is authenticated
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
    
    # Hardcoded credentials as requested
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
        if query in s.get("nama", "").lower():
            matches.append({
                "id": s.get("id"),
                "nama": s.get("nama"),
                "kelas": s.get("kelas"),
                "kelompok": s.get("kelompok"),
                "jenis": s.get("jenis")
            })
            if len(matches) >= 15: # limit to top 15 results
                break
    return jsonify(matches)

@app.route("/api/students/<student_id>")
def api_student_detail(student_id):
    students = load_json_file(STUDENTS_FILE, [])
    student = None
    for s in students:
        if s.get("id") == student_id:
            student = s
            break
            
    if not student:
        return jsonify({"success": False, "message": "Siswa tidak ditemukan"}), 404
        
    mentor = get_student_mentor(
        student.get("jenis"),
        student.get("kelompok"),
        student.get("sub_kelompok")
    )
    
    attendance = load_json_file(ATTENDANCE_FILE, [])
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check if student is present TODAY
    is_present = False
    checkin_time = ""
    attendance_history = []
    
    for a in attendance:
        if a.get("student_id") == student_id:
            attendance_history.append({
                "date": a.get("date"),
                "timestamp": a.get("timestamp")
            })
            if a.get("date") == today:
                is_present = True
                checkin_time = a.get("timestamp", "")
                
    response_data = {
        "success": True,
        "student": {
            "id": student.get("id"),
            "nama": student.get("nama"),
            "kelas": student.get("kelas"),
            "kelompok": student.get("kelompok"),
            "jenis": student.get("jenis"),
            "sub_kelompok": student.get("sub_kelompok"),
            "mentor": mentor,
            "is_present": is_present,
            "checkin_time": checkin_time,
            "attendance_history": attendance_history,
            "total_days_present": len(attendance_history)
        }
    }
    return jsonify(response_data)

@app.route("/api/attendance/checkin", methods=["POST"])
def api_attendance_checkin():
    # Supports JSON, URL-encoded form data, and raw text (for direct QR scanners scanning raw ID)
    if request.is_json:
        data = request.get_json(silent=True) or {}
        student_id = data.get("student_id")
    else:
        student_id = request.form.get("student_id")
        
    # If not found yet, maybe the scanner sent raw body
    if not student_id:
        try:
            # Check if raw data is student ID
            raw_data = request.data.decode('utf-8').strip()
            if raw_data.startswith("STUDENT_"):
                student_id = raw_data
        except Exception:
            pass
            
    if not student_id:
        return jsonify({"success": False, "message": "ID Siswa diperlukan"}), 400
        
    students = load_json_file(STUDENTS_FILE, [])
    student = None
    for s in students:
        if s.get("id") == student_id:
            student = s
            break
            
    if not student:
        return jsonify({"success": False, "message": "Siswa tidak terdaftar"}), 404
    
    # Get current date for multi-day tracking
    today = datetime.now().strftime("%Y-%m-%d")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Validate if today is a valid MPLS event day
    if not is_valid_mpls_date(today):
        return jsonify({
            "success": False, 
            "message": f"Hari ini ({today}) bukan hari kegiatan MPLS atau hari libur."
        }), 400
        
    attendance = load_json_file(ATTENDANCE_FILE, [])
    
    # Check if student already checked in TODAY
    for a in attendance:
        if a.get("student_id") == student_id and a.get("date") == today:
            mentor = get_student_mentor(student.get("jenis"), student.get("kelompok"), student.get("sub_kelompok"))
            return jsonify({
                "success": True,
                "message": f"Siswa {student.get('nama')} sudah absen hari ini.",
                "student": {
                    "nama": student.get("nama"),
                    "kelas": student.get("kelas"),
                    "kelompok": student.get("kelompok"),
                    "jenis": student.get("jenis"),
                    "mentor": mentor,
                    "checkin_time": a.get("timestamp"),
                    "date": a.get("date")
                }
            })
            
    # New check-in for today
    new_record = {
        "student_id": student_id,
        "nama": student.get("nama"),
        "kelas": student.get("kelas"),
        "kelompok": student.get("kelompok"),
        "jenis": student.get("jenis"),
        "date": today,
        "timestamp": now_str
    }
    attendance.append(new_record)
    save_json_file(ATTENDANCE_FILE, attendance)
    
    mentor = get_student_mentor(student.get("jenis"), student.get("kelompok"), student.get("sub_kelompok"))
    
    return jsonify({
        "success": True,
        "message": f"Absen berhasil untuk {student.get('nama')}!",
        "student": {
            "nama": student.get("nama"),
            "kelas": student.get("kelas"),
            "kelompok": student.get("kelompok"),
            "jenis": student.get("jenis"),
            "mentor": mentor,
            "checkin_time": now_str,
            "date": today
        }
    })

@app.route("/api/admin/students", methods=["GET"])
def api_admin_students():
    students = load_json_file(STUDENTS_FILE, [])
    for s in students:
        s["mentor"] = get_student_mentor(s.get("jenis"), s.get("kelompok"), s.get("sub_kelompok"))
    return jsonify(students)

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
        idx_kelompok = -1
        idx_jenis = -1
        idx_sub = -1
        
        for idx, h in enumerate(cleaned_headers):
            if 'nama' in h:
                idx_nama = idx
            elif 'kelas' in h:
                idx_kelas = idx
            elif 'kelompok' in h or 'group' in h:
                idx_kelompok = idx
            elif 'jenis' in h or 'type' in h or 'kategori' in h:
                idx_jenis = idx
            elif 'sub' in h or 'pembina' in h or 'sub kelompok' in h or 'sub-kelompok' in h:
                idx_sub = idx
                
        if idx_nama == -1 or idx_kelas == -1 or idx_kelompok == -1:
            return jsonify({
                "success": False, 
                "message": f"Header CSV harus berisi Nama, Kelas, Kelompok. Ditemukan: {', '.join(headers)}"
            }), 400
            
        new_students = []
        import_count = 0
        
        for row in csv_reader:
            if not row or len(row) <= max(idx_nama, idx_kelas, idx_kelompok):
                continue
                
            nama = row[idx_nama].strip()
            if not nama:
                continue
                
            kelas = row[idx_kelas].strip()
            kelompok = row[idx_kelompok].strip()
            
            if kelompok and not kelompok.lower().startswith('kelompok'):
                kelompok = f"Kelompok {kelompok}"
                
            jenis = "Mayor"
            if idx_jenis != -1 and idx_jenis < len(row):
                val_jenis = row[idx_jenis].strip()
                if val_jenis.lower() == 'cgc':
                    jenis = 'CGC'
                    
            sub_kelompok = "A"
            if idx_sub != -1 and idx_sub < len(row):
                val_sub = row[idx_sub].strip().upper()
                if val_sub in ['A', 'B']:
                    sub_kelompok = val_sub
                    
            student_id = f"STUDENT_{import_count + 1:04d}_{int(random.random()*10000):04d}"
            
            new_students.append({
                "id": student_id,
                "nama": nama,
                "kelas": kelas,
                "kelompok": kelompok,
                "jenis": jenis,
                "sub_kelompok": sub_kelompok
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

@app.route("/api/admin/attendance", methods=["GET"])
def api_admin_attendance():
    attendance = load_json_file(ATTENDANCE_FILE, [])
    students = load_json_file(STUDENTS_FILE, [])
    
    # Get date filter from query params (default to today)
    date_filter = request.args.get("date", "")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # If no date filter, use today
    if not date_filter:
        date_filter = today
    
    # Filter attendance by date
    filtered_attendance = [a for a in attendance if a.get("date") == date_filter]
    
    result = []
    for a in filtered_attendance:
        student_id = a.get("student_id")
        student = next((s for s in students if s.get("id") == student_id), None)
        
        mentor = "Belum ditentukan"
        sub_kelompok = "-"
        if student:
            sub_kelompok = student.get("sub_kelompok", "-")
            mentor = get_student_mentor(student.get("jenis"), student.get("kelompok"), sub_kelompok)
            
        result.append({
            "student_id": student_id,
            "nama": a.get("nama"),
            "kelas": a.get("kelas"),
            "kelompok": a.get("kelompok"),
            "jenis": a.get("jenis"),
            "sub_kelompok": sub_kelompok,
            "mentor": mentor,
            "date": a.get("date"),
            "timestamp": a.get("timestamp")
        })
    return jsonify(result)

@app.route("/api/admin/stats", methods=["GET"])
def api_admin_stats():
    students = load_json_file(STUDENTS_FILE, [])
    attendance = load_json_file(ATTENDANCE_FILE, [])
    
    # Get date filter from query params (default to today)
    date_filter = request.args.get("date", "")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # If no date filter, use today
    if not date_filter:
        date_filter = today
    
    # Filter attendance by date
    filtered_attendance = [a for a in attendance if a.get("date") == date_filter]
    
    total = len(students)
    present = len(filtered_attendance)
    absent = max(0, total - present)
    
    percentage = (present / total * 100) if total > 0 else 0
    
    class_stats = {}
    group_stats = {}
    
    for s in students:
        cls = s.get("kelas", "Lainnya")
        grp = f"{s.get('kelompok')} ({s.get('jenis')})"
        
        if cls not in class_stats:
            class_stats[cls] = {"total": 0, "present": 0}
        if grp not in group_stats:
            group_stats[grp] = {"total": 0, "present": 0}
            
        class_stats[cls]["total"] += 1
        group_stats[grp]["total"] += 1
        
    for a in filtered_attendance:
        s_id = a.get("student_id")
        student = next((s for s in students if s.get("id") == s_id), None)
        if student:
            cls = student.get("kelas", "Lainnya")
            grp = f"{student.get('kelompok')} ({student.get('jenis')})"
            
            if cls in class_stats:
                class_stats[cls]["present"] += 1
            if grp in group_stats:
                group_stats[grp]["present"] += 1
                
    return jsonify({
        "total_students": total,
        "total_present": present,
        "total_absent": absent,
        "percentage": round(percentage, 1),
        "class_stats": class_stats,
        "group_stats": group_stats
    })

@app.route("/api/admin/attendance/export", methods=["GET"])
def api_admin_attendance_export():
    students = load_json_file(STUDENTS_FILE, [])
    attendance = load_json_file(ATTENDANCE_FILE, [])
    
    dest = io.StringIO()
    writer = csv.writer(dest)
    
    writer.writerow(["ID Siswa", "Nama Siswa", "Kelas", "Kelompok", "Jenis", "Sub-Kelompok", "Kakak Pembina", "Status Kehadiran", "Waktu Absen"])
    
    for s in students:
        student_id = s.get("id")
        att = next((a for a in attendance if a.get("student_id") == student_id), None)
        status = "Hadir" if att else "Belum Hadir"
        time_str = att.get("timestamp") if att else "-"
        
        mentor = get_student_mentor(s.get("jenis"), s.get("kelompok"), s.get("sub_kelompok"))
        
        writer.writerow([
            student_id,
            s.get("nama"),
            s.get("kelas"),
            s.get("kelompok"),
            s.get("jenis"),
            s.get("sub_kelompok"),
            mentor,
            status,
            time_str
        ])
        
    output = make_response(dest.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=rekap_absensi_mpls_2026.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output

@app.route("/api/admin/student/<student_id>/attendance", methods=["GET"])
def api_student_attendance_detail(student_id):
    """Get detailed attendance history for a specific student"""
    students = load_json_file(STUDENTS_FILE, [])
    student = next((s for s in students if s.get("id") == student_id), None)
    
    if not student:
        return jsonify({"success": False, "message": "Siswa tidak ditemukan"}), 404
    
    attendance = load_json_file(ATTENDANCE_FILE, [])
    mpls_days = get_mpls_days()
    
    # Get all attendance records for this student
    student_attendance = [a for a in attendance if a.get("student_id") == student_id]
    attended_dates = {a.get("date") for a in student_attendance}
    
    # Build attendance summary for each MPLS day
    attendance_summary = []
    for day in mpls_days:
        is_present = day in attended_dates
        record = next((a for a in student_attendance if a.get("date") == day), None)
        
        attendance_summary.append({
            "date": day,
            "is_present": is_present,
            "timestamp": record.get("timestamp") if record else None
        })
    
    mentor = get_student_mentor(student.get("jenis"), student.get("kelompok"), student.get("sub_kelompok"))
    
    return jsonify({
        "success": True,
        "student": {
            "id": student.get("id"),
            "nama": student.get("nama"),
            "kelas": student.get("kelas"),
            "kelompok": student.get("kelompok"),
            "jenis": student.get("jenis"),
            "sub_kelompok": student.get("sub_kelompok"),
            "mentor": mentor
        },
        "mpls_config": MPLS_CONFIG,
        "attendance_summary": attendance_summary,
        "total_present": len(attended_dates),
        "total_days": len(mpls_days),
        "absent_dates": [day for day in mpls_days if day not in attended_dates]
    })

@app.route("/api/mpls/config", methods=["GET"])
def api_mpls_config():
    """Get MPLS configuration"""
    return jsonify({
        "success": True,
        "config": MPLS_CONFIG
    })

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
