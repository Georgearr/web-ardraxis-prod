import re
from flask import Blueprint, render_template, request, jsonify
from services.duta_sheets import save_duta_application

duta_bp = Blueprint("duta", __name__, url_prefix="/dutasmaigs")

# Regex to validate HTTP/HTTPS URL format safely
URL_PATTERN = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)


def is_valid_url(url_str):
    if not isinstance(url_str, str):
        return False
    url_str = url_str.strip()
    if not url_str:
        return False
    # Prevent dangerous schemes or local system URLs
    lower = url_str.lower()
    if lower.startswith("javascript:") or lower.startswith("data:") or lower.startswith("file:"):
        return False
    return bool(URL_PATTERN.match(url_str))


def count_paragraphs(text):
    if not text:
        return 0
    # Split text by double newlines or lines containing only whitespace
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    return len(paragraphs)


@duta_bp.route("/", methods=["GET"], strict_slashes=False)
@duta_bp.route("", methods=["GET"], strict_slashes=False)
def index():
    return render_template("dutasmaigs/index.html")


@duta_bp.route("/api/submit", methods=["POST"])
def submit_application():
    try:
        data = request.get_json(silent=True)
        if not data or not isinstance(data, dict):
            return jsonify({
                "success": False,
                "message": "Format data tidak valid. Silakan kirimkan data JSON."
            }), 400

        full_name = str(data.get("full_name", "")).strip()
        student_class = str(data.get("class", "")).strip()
        vision_mission = str(data.get("vision_mission", "")).strip()
        programs = data.get("programs", [])
        motivation_letter = str(data.get("motivation_letter", "")).strip()
        has_experience = data.get("has_experience")
        experiences = str(data.get("experiences", "")).strip()
        certificate_urls = data.get("certificate_urls", [])
        talent_video_urls = data.get("talent_video_urls", [])
        commitment = str(data.get("commitment", "")).strip()
        agreement = data.get("agreement")

        # 1. Validate Personal
        if not full_name:
            return jsonify({"success": False, "message": "Nama Lengkap wajib diisi."}), 400
        if not student_class:
            return jsonify({"success": False, "message": "Kelas wajib diisi."}), 400
        if len(student_class) > 30:
            return jsonify({"success": False, "message": "Kelas maksimal 30 karakter."}), 400

        # 2. Validate Vision Mission
        if not vision_mission:
            return jsonify({"success": False, "message": "Visi dan Misi Duta IGS wajib diisi."}), 400
        if len(vision_mission) > 1000:
            return jsonify({"success": False, "message": "Visi dan Misi maksimal 1000 karakter."}), 400

        # 3. Validate Work Programs
        if not isinstance(programs, list) or len(programs) == 0:
            return jsonify({"success": False, "message": "Minimal harus menambahkan 1 program kerja."}), 400
        for i, prog in enumerate(programs, 1):
            if not isinstance(prog, dict) or not str(prog.get("nama_program", "")).strip():
                return jsonify({"success": False, "message": f"Nama Program Kerja #{i} wajib diisi."}), 400

        # 4. Validate Motivation Letter (Max 3 paragraphs)
        if not motivation_letter:
            return jsonify({"success": False, "message": "Motivation letter wajib diisi."}), 400
        if count_paragraphs(motivation_letter) > 3:
            return jsonify({"success": False, "message": "Motivation letter maksimal 3 paragraf."}), 400

        # 5. Validate Experience
        is_exp_yes = has_experience in [True, "true", "Ya", "ya"]

        # 6. Validate Certificate URLs
        cleaned_cert_urls = []
        if isinstance(certificate_urls, list):
            for i, url in enumerate(certificate_urls, 1):
                url_str = str(url).strip()
                if url_str:
                    if not is_valid_url(url_str):
                        return jsonify({"success": False, "message": f"Link Sertifikat #{i} tidak valid. Masukkan URL HTTP/HTTPS yang benar."}), 400
                    cleaned_cert_urls.append(url_str)

        # 7. Validate Talent Video URLs (Min 1 video required)
        cleaned_talent_urls = []
        if isinstance(talent_video_urls, list):
            for i, url in enumerate(talent_video_urls, 1):
                url_str = str(url).strip()
                if url_str:
                    if not is_valid_url(url_str):
                        return jsonify({"success": False, "message": f"Link Video Bakat #{i} tidak valid. Masukkan URL HTTP/HTTPS yang benar."}), 400
                    cleaned_talent_urls.append(url_str)

        if len(cleaned_talent_urls) == 0:
            return jsonify({"success": False, "message": "Silakan masukkan minimal 1 link video bakat."}), 400

        # 8. Validate Commitment & Agreement
        if commitment != "Ya, saya yakin.":
            return jsonify({"success": False, "message": "Anda harus memilih 'Ya, saya yakin.' untuk mengirimkan pendaftaran."}), 400
        if agreement not in [True, "true", "on", "1"]:
            return jsonify({"success": False, "message": "Anda wajib mengonfirmasi kebenaran data dan bersedia mengikuti seluruh rangkaian kegiatan."}), 400

        # Construct safe payload for Google Sheets
        payload = {
            "full_name": full_name,
            "class": student_class,
            "vision_mission": vision_mission,
            "programs": programs,
            "motivation_letter": motivation_letter,
            "has_experience": is_exp_yes,
            "experiences": experiences if is_exp_yes else "",
            "certificate_urls": cleaned_cert_urls,
            "talent_video_urls": cleaned_talent_urls,
            "commitment": commitment,
        }

        success, result_or_err = save_duta_application(payload)
        if not success:
            return jsonify({
                "success": False,
                "message": "Pendaftaran belum berhasil dikirim. Silakan coba kembali."
            }), 500

        return jsonify({
            "success": True,
            "applicationId": result_or_err,
            "message": "Pendaftaran berhasil dikirim!"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Terjadi kesalahan pada sistem. Silakan coba beberapa saat lagi."
        }), 500
