import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_PATHS = [
    "secrets/google-service-account.json",
    "config/credentials.json",
    "credentials.json",
]

TIMEZONE = ZoneInfo("Asia/Jakarta")

HEADERS = [
    "Timestamp", "Sekolah", "Nama", "Kelas",
    "Pilihan 1", "Pilihan 2",
    "Visi Misi", "Motivasi",
    "Kelebihan", "Kekurangan",
    "Pengalaman Organisasi",
    "Link Google Drive Sertifikat",
    "Skala Prioritas",
    "Link Google Drive Tugas Sekbid 1",
    "Link Google Drive Tugas Sekbid 2",
]

UNDANGAN_HEADERS = [
    "Timestamp", "Jalur", "Sekolah", "Nama", "Kelas",
    "Pilihan 1", "Pilihan 2",
    "Visi Misi", "Motivasi",
    "Kelebihan", "Kekurangan",
    "Pengalaman Organisasi",
    "Link Google Drive Sertifikat",
    "Skala Prioritas",
    "Link Google Drive Tugas Sekbid 1",
    "Link Google Drive Tugas Sekbid 2",
]

JALUR_UNDANGAN_SHEET_NAMES = {
    "sub_sekbid_desain_ddv": "Desain-DDV",
    "hubungan_masyarakat_dan_publikasi": "Publikasi",
    "komunikasi": "Komunikasi",
    "sub_sekbid_producer": "Producer",
    "sub_sekbid_video_editor": "Editor",
    "sub_sekbid_dokumentasi_ddv": "Dokumentasi-DDV",
    "sub_sekbid_kreatif_ddv": "Kreatif",
    "sosial": "Sosial",
    "bela_negara": "Bela-Negara",
    "bahasa": "Bahasa",
    "apresiasi_seni_dan_olahraga": "Apres",
    "multimedia_website": "Web",
    "sub_sekbid_illustrator": "Illus",
}


def _find_credentials():
    for path in CREDENTIALS_PATHS:
        if os.path.exists(path):
            return path
    return None


def _get_credentials_path():
    path = _find_credentials()
    if path:
        return path
    locations = "\n".join(f"- {p}" for p in CREDENTIALS_PATHS)
    raise FileNotFoundError(
        "Google Service Account credentials not found.\n"
        "Expected locations:\n"
        f"{locations}"
    )


def get_client():
    creds_path = _get_credentials_path()
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPE)
    return gspread.authorize(creds)


def _now_jakarta():
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")


def _ensure_sheet(spreadsheet, sheet_name):
    try:
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=30)


def _ensure_headers(worksheet, headers=None):
    headers = headers or HEADERS
    existing = worksheet.get_all_values()
    if not existing or not existing[0]:
        worksheet.append_row(headers)
        return
    existing_headers = existing[0]
    if len(existing_headers) < len(headers):
        for i in range(len(existing_headers), len(headers)):
            worksheet.update_cell(1, i + 1, headers[i])


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _jalur_label(school_config):
    name = (school_config.get("school") or {}).get("name", "")
    if "undangan" in name.lower() or "jalurundangan" in name.lower():
        return "Undangan"
    return "Umum"


def _sekbid_labels(school_config, sekbid_keys):
    sekbid_data = school_config.get("sekbid", {})
    labels = []
    for k in sekbid_keys:
        found = None
        for name, val in sekbid_data.items():
            if val.get("id") == k:
                found = name
                break
        labels.append(found or k)
    return labels


def _build_row(school_config, form_data, labels, undangan=False):
    p1 = labels[0] if len(labels) > 0 else ""
    p2 = labels[1] if len(labels) > 1 else ""
    school_name = school_config.get("school", {}).get("name", "")
    row = [
        _now_jakarta(),
        school_name,
        form_data.get("nama", ""),
        form_data.get("kelas", ""),
        p1,
        p2,
        form_data.get("visi_misi", ""),
        form_data.get("motivasi", ""),
        form_data.get("kelebihan", ""),
        form_data.get("kekurangan", ""),
        form_data.get("pengalaman", ""),
        form_data.get("sertifikat_link", ""),
        form_data.get("prioritas", ""),
        form_data.get("google_drive_link", ""),
        "",
    ]
    if undangan:
        row.insert(1, _jalur_label(school_config))
    return row


def _post_apps_script(url, payload):
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    opener = urllib.request.build_opener(_NoRedirect)
    current = url
    last_error = None
    for _ in range(6):
        req = urllib.request.Request(current, data=body, headers=headers, method="POST")
        try:
            with opener.open(req, timeout=45) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw) if raw else {}
                if data.get("success"):
                    return True, data.get("message") or "Pendaftaran berhasil disimpan"
                return False, data.get("message") or "Gagal menyimpan ke spreadsheet"
        except urllib.error.HTTPError as e:
            location = e.headers.get("Location") if e.headers else None
            if e.code in (301, 302, 303, 307, 308) and location:
                current = location
                continue
            last_error = e.read().decode("utf-8", errors="replace") if e.fp else str(e)
            break
        except Exception as e:
            last_error = str(e)
            break
    return False, last_error or "Gagal mengirim ke Google Apps Script"


def submit_recruitment(school_config, form_data, sekbid_keys):
    google_cfg = school_config.get("google") or {}
    apps_script_url = (google_cfg.get("apps_script_url") or "").strip()
    labels = _sekbid_labels(school_config, sekbid_keys)

    if apps_script_url:
        payload = {
            "timestamp": _now_jakarta(),
            "jalur": _jalur_label(school_config),
            "sekolah": school_config.get("school", {}).get("name", ""),
            "nama": form_data.get("nama", ""),
            "kelas": form_data.get("kelas", ""),
            "pilihan1": labels[0] if labels else "",
            "pilihan2": labels[1] if len(labels) > 1 else "",
            "visi_misi": form_data.get("visi_misi", ""),
            "motivasi": form_data.get("motivasi", ""),
            "kelebihan": form_data.get("kelebihan", ""),
            "kekurangan": form_data.get("kekurangan", ""),
            "pengalaman": form_data.get("pengalaman", ""),
            "sertifikat_link": form_data.get("sertifikat_link", ""),
            "prioritas": form_data.get("prioritas", ""),
            "google_drive_link": form_data.get("google_drive_link", ""),
            "sekbid_ids": list(sekbid_keys),
        }
        return _post_apps_script(apps_script_url, payload)

    spreadsheet_id = google_cfg.get("spreadsheet_id", "")
    if not spreadsheet_id:
        return False, "Spreadsheet ID tidak dikonfigurasi"

    try:
        client = get_client()
    except FileNotFoundError as e:
        return False, str(e)
    except GoogleAuthError as e:
        return False, f"Google Auth Error: {e}"
    except Exception as e:
        return False, f"Gagal memuat kredensial: {e}"

    try:
        spreadsheet = client.open_by_key(spreadsheet_id)
    except gspread.exceptions.SpreadsheetNotFound:
        return False, (
            f"Spreadsheet dengan ID '{spreadsheet_id}' tidak ditemukan.\n"
            "Periksa apakah ID sudah benar dan Service Account memiliki akses."
        )
    except gspread.exceptions.APIError as e:
        if "403" in str(e) or "permission" in str(e).lower():
            return False, (
                "Permission denied.\n"
                "Please share the spreadsheet with the Service Account email as Editor."
            )
        return False, f"Google Sheets API Error: {e}"
    except Exception as e:
        return False, f"Gagal terhubung ke Google Sheets: {e}"

    row = _build_row(school_config, form_data, labels)
    use_undangan_names = _jalur_label(school_config) == "Undangan"
    targets = []
    if use_undangan_names:
        targets.append("Semua")
    for sekbid_key in sekbid_keys:
        if use_undangan_names:
            targets.append(JALUR_UNDANGAN_SHEET_NAMES.get(sekbid_key, sekbid_key))
        else:
            targets.append(sekbid_key)

    for sheet_name in targets:
        try:
            worksheet = _ensure_sheet(spreadsheet, sheet_name)
            _ensure_headers(worksheet)
            worksheet.append_row(row)
        except Exception:
            continue

    return True, "Pendaftaran berhasil disimpan"
