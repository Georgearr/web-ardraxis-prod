import os
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


def _ensure_headers(worksheet):
    existing = worksheet.get_all_values()
    if not existing or not existing[0]:
        worksheet.append_row(HEADERS)
        return
    existing_headers = existing[0]
    if len(existing_headers) < len(HEADERS):
        for i in range(len(existing_headers), len(HEADERS)):
            worksheet.update_cell(1, i + 1, HEADERS[i])


def submit_recruitment(school_config, form_data, sekbid_keys):
    spreadsheet_id = school_config.get("google", {}).get("spreadsheet_id", "")
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

    sekbid_data = school_config.get("sekbid", {})
    labels = []
    for k in sekbid_keys:
        found = None
        for name, val in sekbid_data.items():
            if val.get("id") == k:
                found = name
                break
        labels.append(found or k)

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

    for sekbid_key in sekbid_keys:
        try:
            worksheet = _ensure_sheet(spreadsheet, sekbid_key)
            _ensure_headers(worksheet)
            worksheet.append_row(row)
        except Exception as e:
            continue

    return True, "Pendaftaran berhasil disimpan"
