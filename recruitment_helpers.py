import os
import json
import re
from datetime import datetime
from werkzeug.utils import secure_filename
import gspread
from google.oauth2.service_account import Credentials

from recruitment_config import (
    get_sekbid_data, get_school_metadata, get_progress_dir, get_spreadsheet_id,
    AUTOSAVE_DELAY,
)


class ConfigLoader:
    @staticmethod
    def load_sekbid(school_key=None):
        return get_sekbid_data(school_key)

    @staticmethod
    def get_sekbid_list(school_key=None):
        data = ConfigLoader.load_sekbid(school_key)
        result = []
        for key, val in data.items():
            result.append({
                "key": key,
                "label": key,
                "id": val.get("id", ""),
                "description": val.get("description", ""),
                "requirements": val.get("requirements", []),
                "questions": val.get("questions", []),
                "youtube": val.get("youtube", ""),
            })
        return result

    @staticmethod
    def get_school_config(school_key):
        return get_school_metadata(school_key)


class YouTubeEmbedHelper:
    @staticmethod
    def to_embed_url(url):
        if not url:
            return ""
        patterns = [
            r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)",
            r"(?:https?:\/\/)?youtu\.be\/([a-zA-Z0-9_-]+)",
            r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]+)",
        ]
        video_id = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                break
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}"
        return url


class GoogleSheetsManager:
    def __init__(self, spreadsheet_id=None):
        self.spreadsheet_id = spreadsheet_id or get_spreadsheet_id()
        self.credentials_path = "credentials.json"
        self._client = None

    def get_client(self):
        if self._client:
            return self._client
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(self.credentials_path, scopes=scope)
        self._client = gspread.authorize(creds)
        return self._client

    def ensure_sheet_exists(self, spreadsheet, sheet_name):
        try:
            return spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            return spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=30)

    def ensure_headers(self, worksheet, headers):
        existing = worksheet.get_all_values()
        if not existing or not existing[0]:
            worksheet.append_row(headers)
            return
        existing_headers = existing[0]
        if len(existing_headers) < len(headers):
            for i in range(len(existing_headers), len(headers)):
                worksheet.update_cell(1, i + 1, headers[i])

    def save_submission(self, sekbid_keys, data):
        if not self.spreadsheet_id:
            return False, "Spreadsheet ID not configured"

        client = self.get_client()
        spreadsheet = client.open_by_key(self.spreadsheet_id)

        headers = [
            "Timestamp", "Nama Lengkap", "Kelas",
            "Sekbid", "Visi dan Misi",
            "Motivasi", "Kelebihan", "Kekurangan",
            "Pengalaman Organisasi", "Skala Prioritas",
            "Link Sertifikat",
            "Link Tugas Sekbid",
        ]

        all_sekbid = ConfigLoader.load_sekbid()
        sekbid_labels = []
        for k in sekbid_keys:
            for name, val in all_sekbid.items():
                if val.get("id") == k:
                    sekbid_labels.append(name)
                    break
            else:
                sekbid_labels.append(k)

        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("nama", ""),
            data.get("kelas", ""),
            ", ".join(sekbid_labels),
            data.get("visi_misi", ""),
            data.get("motivasi", ""),
            data.get("kelebihan", ""),
            data.get("kekurangan", ""),
            data.get("pengalaman", ""),
            data.get("prioritas", ""),
            data.get("sertifikat_link", ""),
            data.get("google_drive_link", ""),
        ]

        for sekbid_key in sekbid_keys:
            sheet_name = sekbid_key
            try:
                worksheet = self.ensure_sheet_exists(spreadsheet, sheet_name)
                self.ensure_headers(worksheet, headers)
                worksheet.append_row(row)
            except Exception:
                continue

        return True, "Pendaftaran berhasil disimpan"


class ProgressManager:
    def __init__(self, progress_dir=None):
        self.progress_dir = progress_dir or get_progress_dir()
        os.makedirs(self.progress_dir, exist_ok=True)

    def _file_path(self, session_id):
        safe = secure_filename(str(session_id))
        return os.path.join(self.progress_dir, f"{safe}.json")

    def save(self, session_id, data):
        file_path = self._file_path(session_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load(self, session_id):
        file_path = self._file_path(session_id)
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def clear(self, session_id):
        file_path = self._file_path(session_id)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception:
            return False


class ValidationHelper:
    @staticmethod
    def validate_step1(data):
        errors = {}
        nama = data.get("nama", "").strip()
        kelas = data.get("kelas", "").strip()

        if not nama:
            errors["nama"] = "Nama lengkap wajib diisi"
        elif len(nama) < 3:
            errors["nama"] = "Nama lengkap minimal 3 karakter"

        if not kelas:
            errors["kelas"] = "Kelas wajib diisi"

        return errors

    @staticmethod
    def validate_step2(data):
        errors = {}
        sekbid = data.get("sekbid", [])
        if not sekbid or not isinstance(sekbid, list):
            errors["sekbid"] = "Pilih minimal satu Sekbid"
        elif len(sekbid) > 2:
            errors["sekbid"] = "Maksimal 2 Sekbid"
        return errors

    @staticmethod
    def validate_step3(data):
        errors = {}
        visi_misi = data.get("visi_misi", "").strip()
        motivasi = data.get("motivasi", "").strip()
        kelebihan = data.get("kelebihan", "").strip()
        kekurangan = data.get("kekurangan", "").strip()
        prioritas = data.get("prioritas", "").strip()

        if not visi_misi:
            errors["visi_misi"] = "Visi dan misi wajib diisi"
        elif len(visi_misi) < 10:
            errors["visi_misi"] = "Visi dan misi minimal 10 karakter"

        if not motivasi:
            errors["motivasi"] = "Motivasi wajib diisi"
        elif len(motivasi) < 10:
            errors["motivasi"] = "Motivasi minimal 10 karakter"

        if not kelebihan:
            errors["kelebihan"] = "Kelebihan wajib diisi"
        elif len(kelebihan) < 5:
            errors["kelebihan"] = "Kelebihan minimal 5 karakter"

        if not kekurangan:
            errors["kekurangan"] = "Kekurangan wajib diisi"

        if not prioritas:
            errors["prioritas"] = "Skala prioritas wajib diisi"
        elif not re.match(r"^[1-5](?:-[1-5])*$", prioritas):
            errors["prioritas"] = "Format harus angka 1-5 dipisah tanda (-). Contoh: 1-2-3-4-5"

        return errors

    @staticmethod
    def validate_step4(data):
        errors = {}
        drive_link = data.get("google_drive_link", "").strip()
        if not drive_link:
            errors["google_drive_link"] = "Link Google Drive wajib diisi"
        elif "drive.google.com" not in drive_link and "docs.google.com" not in drive_link:
            errors["google_drive_link"] = "Harap masukkan link Google Drive yang valid"
        return errors
