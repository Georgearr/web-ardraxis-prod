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


def _format_programs(programs):
    """
    Convert list of program dicts into a multi-line plain-text block.
    Each program is rendered as:
        Program N
        Nama Program: ...
        Tujuan: ...
        Target: ...
        Deskripsi: ...
    Programs are separated by a blank line.
    """
    if not programs:
        return ""
    blocks = []
    for idx, prog in enumerate(programs, 1):
        if not isinstance(prog, dict):
            continue
        lines = [f"Program {idx}"]
        lines.append(f"Nama Program: {str(prog.get('nama_program', '')).strip()}")
        lines.append(f"Tujuan: {str(prog.get('tujuan', '')).strip()}")
        lines.append(f"Target: {str(prog.get('target', '')).strip()}")
        lines.append(f"Deskripsi: {str(prog.get('deskripsi', '')).strip()}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _format_experience(has_experience, experiences_text):
    """
    Render experience as a plain-text block readable by non-IT admins.
    """
    is_yes = has_experience in [True, "true", "Ya", "ya"]
    if not is_yes:
        return "Tidak memiliki pengalaman sebelumnya."
    text = str(experiences_text or "").strip()
    if not text:
        return "Tidak memiliki pengalaman sebelumnya."
    items = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not items:
        return "Tidak memiliki pengalaman sebelumnya."
    bullet_lines = "\n".join(f"- {item}" for item in items)
    return f"Ya\nPengalaman:\n{bullet_lines}"


def _format_url_list(urls):
    """
    Join URL list with newlines, preserving raw URLs.
    """
    if not urls:
        return ""
    cleaned = [str(u).strip() for u in urls if str(u or "").strip()]
    return "\n".join(cleaned)


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
    Returns: (success: bool, error_message: str | None)
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
            submitted_at = _now_jakarta_str()

            programs_text = _format_programs(data.get("programs", []))
            experience_text = _format_experience(
                data.get("has_experience"),
                data.get("experiences", "")
            )
            cert_urls_text = _format_url_list(data.get("certificate_urls", []))
            talent_urls_text = _format_url_list(data.get("talent_video_urls", []))

            row = [
                submitted_at,
                str(data.get("full_name", "")).strip(),
                str(data.get("class", "")).strip(),
                str(data.get("vision_mission", "")).strip(),
                programs_text,
                str(data.get("motivation_letter", "")).strip(),
                experience_text,
                cert_urls_text,
                talent_urls_text,
                str(data.get("commitment", "Ya, saya yakin.")).strip(),
                "Submitted"
            ]

            ws.append_row(row)
            return True, None
        except Exception as e:
            return False, f"Failed to record application to Google Sheets: {str(e)}"
