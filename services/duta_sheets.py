import os
import json
import re
import threading
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
    "valentine-sheet.json",
]

TIMEZONE = ZoneInfo("Asia/Jakarta")
_SHEET_LOCK = threading.Lock()

DUTA_HEADERS = [
    "application_id",
    "submitted_at",
    "full_name",
    "class",
    "vision_mission",
    "programs",
    "motivation_letter",
    "has_experience",
    "experiences",
    "certificate_urls",
    "talent_video_urls",
    "commitment",
    "status"
]


def _now_jakarta_str():
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")


def get_duta_credentials():
    """
    Construct Credentials using Duta Siswa IGS namespaced environment variables
    (DUTA_CLIENT_EMAIL & DUTA_PRIVATE_KEY) or fall back to service account JSON files.
    """
    client_email = os.environ.get("DUTA_CLIENT_EMAIL")
    private_key = os.environ.get("DUTA_PRIVATE_KEY")

    if client_email and private_key:
        # Handle newline characters in private key safely
        formatted_private_key = private_key.replace("\\n", "\n")
        info = {
            "type": "service_account",
            "client_email": client_email,
            "private_key": formatted_private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        return Credentials.from_service_account_info(info, scopes=SCOPE)

    # Fall back to file search
    for path in CREDENTIALS_PATHS:
        if os.path.exists(path):
            return Credentials.from_service_account_file(path, scopes=SCOPE)

    raise FileNotFoundError(
        "Duta Siswa Google Service Account credentials not found. "
        "Please set DUTA_CLIENT_EMAIL and DUTA_PRIVATE_KEY in .env "
        "or place a service account JSON file in secrets/ or root directory."
    )


def get_duta_client():
    creds = get_duta_credentials()
    return gspread.authorize(creds)


def _ensure_applications_sheet(spreadsheet):
    try:
        ws = spreadsheet.worksheet("Applications")
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title="Applications", rows=1000, cols=20)

    existing = ws.get_all_values()
    if not existing or not existing[0]:
        ws.append_row(DUTA_HEADERS)
    else:
        # Ensure header row has required columns if empty or incomplete
        existing_headers = existing[0]
        if len(existing_headers) < len(DUTA_HEADERS):
            ws.update(f"A1:{chr(64 + len(DUTA_HEADERS))}1", [DUTA_HEADERS])
    return ws


def _generate_application_id(worksheet):
    """
    Generate Application ID format: IGS-DUTA-2026-XXXX (e.g. IGS-DUTA-2026-0001)
    """
    records = worksheet.get_all_values()
    max_seq = 0

    if len(records) > 1:
        # Check column 0 for existing IDs
        pattern = re.compile(r"^IGS-DUTA-2026-(\d{4})$")
        for row in records[1:]:
            if row and row[0]:
                match = pattern.match(row[0].strip())
                if match:
                    seq = int(match.group(1))
                    if seq > max_seq:
                        max_seq = seq

    new_seq = max_seq + 1
    return f"IGS-DUTA-2026-{new_seq:04d}"


def save_duta_application(data):
    """
    Saves a single application to Google Sheets for Duta Siswa IGS.
    data format:
    {
        "full_name": str,
        "class": str,
        "vision_mission": str,
        "programs": list[dict],
        "motivation_letter": str,
        "has_experience": str | bool,
        "experiences": str,
        "certificate_urls": list[str],
        "talent_video_urls": list[str],
        "commitment": str
    }
    Returns: (success: bool, app_id_or_error: str)
    """
    sheets_id = os.environ.get("DUTA_GOOGLE_SHEETS_ID")

    try:
        client = get_duta_client()
    except Exception as e:
        return False, f"Credential Authentication Error: {str(e)}"

    try:
        if sheets_id and sheets_id.strip():
            spreadsheet = client.open_by_key(sheets_id.strip())
        else:
            spreadsheet = client.open("Duta Siswa IGS — Pendaftaran")
    except gspread.exceptions.SpreadsheetNotFound:
        return False, f"Spreadsheet with ID or title '{sheets_id}' not found. Check Google Sheets permissions."
    except Exception as e:
        return False, f"Failed to connect to Google Sheets: {str(e)}"

    with _SHEET_LOCK:
        try:
            ws = _ensure_applications_sheet(spreadsheet)
            app_id = _generate_application_id(ws)
            submitted_at = _now_jakarta_str()

            has_exp_str = "Ya" if (data.get("has_experience") in [True, "true", "Ya", "ya"]) else "Tidak"

            # Serialize lists cleanly as JSON strings
            programs_json = json.dumps(data.get("programs", []), ensure_ascii=False)
            cert_urls_json = json.dumps(data.get("certificate_urls", []), ensure_ascii=False)
            talent_urls_json = json.dumps(data.get("talent_video_urls", []), ensure_ascii=False)

            row = [
                app_id,
                submitted_at,
                str(data.get("full_name", "")).strip(),
                str(data.get("class", "")).strip(),
                str(data.get("vision_mission", "")).strip(),
                programs_json,
                str(data.get("motivation_letter", "")).strip(),
                has_exp_str,
                str(data.get("experiences", "")).strip(),
                cert_urls_json,
                talent_urls_json,
                str(data.get("commitment", "Ya, saya yakin.")).strip(),
                "Submitted"
            ]

            ws.append_row(row)
            return True, app_id
        except Exception as e:
            return False, f"Failed to record application to Google Sheets: {str(e)}"
