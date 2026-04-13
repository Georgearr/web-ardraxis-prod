import gspread
from google.oauth2.service_account import Credentials
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables
SPREADSHEET_URL = os.getenv("SALVATORE_SPREADSHEET_URL")
SHEETS_CREDENTIALS_JSON = os.getenv("SALVATORE_SHEETS_CREDENTIALS")

# Extract spreadsheet ID from URL if provided
if SPREADSHEET_URL:
    if "/d/" in SPREADSHEET_URL:
        SPREADSHEET_ID = SPREADSHEET_URL.split("/d/")[1].split("/")[0]
    else:
        SPREADSHEET_ID = SPREADSHEET_URL  # Assume it's already an ID
else:
    SPREADSHEET_ID = "1rrTL6mtohSIxU51y027AClnd5C0I3Vn2xUWM3QK9yoE"  # Default Salvatoré spreadsheet

# SETUP INSTRUCTIONS:
# 1. Go to Google Cloud Console
# 2. Create a new project or use existing one
# 3. Enable Google Sheets API
# 4. Create a Service Account with Editor role
# 5. Generate and download the JSON key file
# 6. Copy .env.example to .env and fill in SALVATORE_SPREADSHEET_URL and SALVATORE_SHEETS_CREDENTIALS
# 7. Share the spreadsheet with the service account email (client_email from JSON)

# Sheet names for each competition
SHEETS = {
    "bernyanyi_rohani": "Bernyanyi_Rohani",
    "quiz_alkitab": "Quiz_Alkitab",
    "egg_shell_mosaic": "Egg_Shell_Mosaic",
    "story_telling_rohani": "Story_Telling_Rohani"
}

def get_google_sheets_client():
    """Initialize and return Google Sheets client."""
    try:
        # Use the original Salvatoré credentials from .env
        import os
        from dotenv import load_dotenv
        load_dotenv()

        creds_info = os.getenv("SALVATORE_SHEETS_CREDENTIALS")
        
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[get_google_sheets_client] Loading credentials...\n")
            if creds_info:
                # Log first 50 chars of creds to verify it's loaded
                f.write(f"[get_google_sheets_client] Creds found, starts with: {creds_info[:50]}...\n")
            else:
                f.write(f"[get_google_sheets_client] WARNING: No credentials found!\n")
        
        if not creds_info:
            raise ValueError("SALVATORE_SHEETS_CREDENTIALS environment variable not set")

        import json
        creds_data = json.loads(creds_info)
        
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[get_google_sheets_client] Parsed JSON credentials\n")
            f.write(f"[get_google_sheets_client] Service account email: {creds_data.get('client_email')}\n")

        creds = Credentials.from_service_account_info(creds_data, scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])
        
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[get_google_sheets_client] Created credentials object\n")
        
        client = gspread.authorize(creds)
        
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[get_google_sheets_client] Authorized gspread client\n")
        
        return client
    except Exception as e:
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[get_google_sheets_client] Error: {e}\n")
        raise

def append_to_sheet(client, sheet_name, data):
    """Append data to the specified sheet."""
    if not SPREADSHEET_ID:
        error_msg = "SALVATORE_SPREADSHEET_URL environment variable not set or invalid"
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[ERROR] {error_msg}\n")
        return False

    try:
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[INFO] Opening spreadsheet with ID: {SPREADSHEET_ID}\n")
        # Open the spreadsheet by ID
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[SUCCESS] Spreadsheet opened successfully: {spreadsheet.title}\n")

        # Get or create the sheet
        try:
            with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[INFO] Looking for sheet: {sheet_name}\n")
            sheet = spreadsheet.worksheet(sheet_name)
            with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[SUCCESS] Sheet found: {sheet_name}\n")
        except gspread.WorksheetNotFound:
            with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[INFO] Sheet '{sheet_name}' not found, creating it...\n")
            # Create sheet if it doesn't exist
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[SUCCESS] Sheet created: {sheet_name}\n")

        # Add timestamp
        data.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[INFO] Appending data: {data}\n")

        # Append the data
        result = sheet.append_row(data)
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[SUCCESS] Data appended successfully to {sheet_name}\n")
        return True

    except Exception as e:
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[ERROR] Error appending to {sheet_name}: {str(e)}\n")
            f.write(f"[ERROR] Error type: {type(e).__name__}\n")
        return False

def save_registration(competition, data_dict):
    """Save registration data for a specific competition."""
    try:
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Starting for competition: {competition}\n")
        
        if competition not in SHEETS:
            error_msg = f"Unknown competition: {competition}"
            with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[ERROR] {error_msg}\n")
            return False

        sheet_name = SHEETS[competition]
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Sheet name: {sheet_name}\n")

        # Convert data dict to list based on competition
        if competition == "bernyanyi_rohani":
            row_data = [
                data_dict.get("nama", ""),
               data_dict.get("kategori", ""),
                data_dict.get("kelas", ""),
                data_dict.get("agama", ""),
                data_dict.get("judul", "")
            ]
        elif competition == "quiz_alkitab":
            row_data = [
                data_dict.get("kategori", ""),
                data_dict.get("nama-ketua", ""),
                data_dict.get("agama-ketua", ""),
                data_dict.get("nama-anggota", ""),
                data_dict.get("agama-anggota", ""),
                data_dict.get("kelas", "")
            ]
        elif competition == "egg_shell_mosaic":
            row_data = [
                data_dict.get("nama", ""),
                data_dict.get("kategori", ""),
                data_dict.get("kelas", ""),
                data_dict.get("agama", "")
            ]
        elif competition == "story_telling_rohani":
            row_data = [
                data_dict.get("nama", ""),
                data_dict.get("kategori", ""),
                data_dict.get("kelas", ""),
                data_dict.get("agama", ""),
                data_dict.get("tema", "")
            ]
        else:
            error_msg = f"No data mapping for competition: {competition}"
            with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[ERROR] {error_msg}\n")
            return False

        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Getting client...\n")
        try:
            client = get_google_sheets_client()
            with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[save_registration] Client obtained\n")
        except Exception as e:
            with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[save_registration] Client error: {e}\n")
            raise
        
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Appending to sheet...\n")
        result = append_to_sheet(client, sheet_name, row_data)
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Append result: {result}\n")
        return result
    except Exception as e:
        with open('salvatore_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[ERROR] Exception in save_registration: {e}\n")
            import traceback
            f.write(traceback.format_exc())
        return False

# Example usage
if __name__ == "__main__":
    # Test with sample data
    test_data = {
        "nama": "John Doe",
        "kategori": "SMA",
        "kelas": "12A",
        "agama": "Kristen"
    }

    save_registration("egg_shell_mosaic", test_data)