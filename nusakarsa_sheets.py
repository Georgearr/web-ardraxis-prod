import gspread
from google.oauth2.service_account import Credentials
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from environment variables
SPREADSHEET_URL = os.getenv("NUSAKARSA_SPREADSHEET_URL")
SHEETS_CREDENTIALS_JSON = os.getenv("NUSAKARSA_SHEETS_CREDENTIALS")

# Extract spreadsheet ID from URL if provided
if SPREADSHEET_URL:
    if "/d/" in SPREADSHEET_URL:
        SPREADSHEET_ID = SPREADSHEET_URL.split("/d/")[1].split("/")[0]
    else:
        SPREADSHEET_ID = SPREADSHEET_URL  # Assume it's already an ID
else:
    SPREADSHEET_ID = "1IvnzS9top7sTLgN1R1WdRYbIILnLSddUFSbAFab7So8"  # Default Nusakarsa spreadsheet

# SETUP INSTRUCTIONS:
# 1. Go to Google Cloud Console
# 2. Create a new project or use existing one
# 3. Enable Google Sheets API
# 4. Create a Service Account with Editor role
# 5. Generate and download the JSON key file
# 6. Copy .env.example to .env and fill in NUSAKARSA_SPREADSHEET_URL and NUSAKARSA_SHEETS_CREDENTIALS
# 7. Share the spreadsheet with the service account email (client_email from JSON)

# Sheet names for each competition
SHEETS = {
    "hias_bekal": "Hias Bekal",
    "nusantara_in_colors": "Nusantara in Colors",
    "tri_lomba": "Tri Lomba",
    "got_talent_nusantara": "Got Talent Nusantara",
    "jejak_juang_cerdas": "Jejak Juang Cerdas",
    "mystery_mission": "Mystery Mission",
    "balon_berantai": "Balon Berantai",
    "makan_kerupuk": "Makan Kerupuk",
    "sarung_sigap": "Sarung Sigap",
    "fashion_show": "Fashion Show",
}

# Participant limits for each competition
# Set to 0 or omit from dictionary for unlimited registrations
PARTICIPANT_LIMITS = {
    "hias_bekal": 0,
    "nusantara_in_colors": 0,
    "tri_lomba": 0,
    "got_talent_nusantara": 0,
    "jejak_juang_cerdas": 0,
    "mystery_mission": 0,
    "balon_berantai": 0,
    "makan_kerupuk": 0,
    "sarung_sigap": 0,
    "fashion_show": 0,
}

def get_google_sheets_client():
    """Initialize and return Google Sheets client."""
    try:
        # Try to load from environment variable first
        creds_info = os.getenv("NUSAKARSA_SHEETS_CREDENTIALS")
        
        if creds_info:
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[get_google_sheets_client] Loading credentials from environment variable...\n")
            try:
                creds_data = json.loads(creds_info)
                with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                    f.write(f"[get_google_sheets_client] Parsed JSON credentials from env\n")
            except json.JSONDecodeError as e:
                with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                    f.write(f"[get_google_sheets_client] JSON decode error from env: {e}\n")
                    f.write(f"[get_google_sheets_client] Falling back to JSON file\n")
                # Fall back to loading from JSON file
                with open("e-nusakarsa-bot-65a6ecc68313.json", "r") as f:
                    creds_data = json.load(f)
                with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                    f.write(f"[get_google_sheets_client] Loaded credentials from JSON file\n")
        else:
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[get_google_sheets_client] No credentials in env, loading from JSON file\n")
            # Load from JSON file if environment variable not set
            with open("e-nusakarsa-bot-65a6ecc68313.json", "r") as f:
                creds_data = json.load(f)
        
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[get_google_sheets_client] Service account email: {creds_data.get('client_email')}\n")

        creds = Credentials.from_service_account_info(creds_data, scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])
        
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[get_google_sheets_client] Created credentials object\n")
        
        client = gspread.authorize(creds)
        
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[get_google_sheets_client] Authorized gspread client\n")
        
        return client
    except Exception as e:
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[get_google_sheets_client] Error: {e}\n")
        raise

def append_to_sheet(client, sheet_name, data):
    """Append data to the specified sheet."""
    if not SPREADSHEET_ID:
        error_msg = "NUSAKARSA_SPREADSHEET_URL environment variable not set or invalid"
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[ERROR] {error_msg}\n")
        return False

    try:
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[INFO] Opening spreadsheet with ID: {SPREADSHEET_ID}\n")
        # Open the spreadsheet by ID
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[SUCCESS] Spreadsheet opened successfully: {spreadsheet.title}\n")

        # Get or create the sheet
        try:
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[INFO] Looking for sheet: {sheet_name}\n")
            sheet = spreadsheet.worksheet(sheet_name)
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[SUCCESS] Sheet found: {sheet_name}\n")
        except gspread.WorksheetNotFound:
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[INFO] Sheet '{sheet_name}' not found, creating it...\n")
            # Create sheet if it doesn't exist
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[SUCCESS] Sheet created: {sheet_name}\n")

        # Add timestamp
        data.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[INFO] Appending data: {data}\n")

        # Append the data
        result = sheet.append_row(data)
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[SUCCESS] Data appended successfully to {sheet_name}\n")
        return True

    except Exception as e:
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[ERROR] Error appending to {sheet_name}: {str(e)}\n")
            f.write(f"[ERROR] Error type: {type(e).__name__}\n")
        return False

def get_registration_count(client, sheet_name):
    """Get the current number of registrations for a competition."""
    try:
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.worksheet(sheet_name)
        
        # Get all values from the sheet
        all_values = sheet.get_all_values()
        
        # Count non-empty rows (excluding header if exists)
        # Assuming first row might be headers, start counting from row 2
        count = 0
        for row in all_values[1:]:  # Skip first row (headers)
            # Count if at least one cell in the row has data
            if any(cell.strip() for cell in row):
                count += 1
        
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[INFO] Current registration count for {sheet_name}: {count}\n")
        
        return count
    except gspread.WorksheetNotFound:
        # Sheet doesn't exist yet, so count is 0
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[INFO] Sheet {sheet_name} not found, count = 0\n")
        return 0
    except Exception as e:
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[ERROR] Error getting registration count for {sheet_name}: {str(e)}\n")
        return 0

def save_registration(competition, data_dict):
    """Save registration data for a specific competition."""
    try:
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Starting for competition: {competition}\n")
        
        if competition not in SHEETS:
            error_msg = f"Unknown competition: {competition}"
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[ERROR] {error_msg}\n")
            return False

        sheet_name = SHEETS[competition]
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Sheet name: {sheet_name}\n")

        # Check participant limit
        limit = PARTICIPANT_LIMITS.get(competition, 0)  # Default to 0 (no limit) if not specified
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Getting client for limit check...\n")
        try:
            client = get_google_sheets_client()
            current_count = get_registration_count(client, sheet_name)
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[save_registration] Current count: {current_count}, Limit: {limit}\n")
            
            if limit > 0 and current_count >= limit:
                with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                    f.write(f"[ERROR] Registration limit reached for {competition}. Current: {current_count}, Limit: {limit}\n")
                return "limit_reached"
        except Exception as e:
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[save_registration] Error checking limit: {e}\n")
            # Continue with registration if we can't check the limit (fail open)
        if competition == "hias_bekal":
            row_data = [
                data_dict.get("nama", "")
            ]
        elif competition == "nusantara_in_colors":
            row_data = [
                data_dict.get("nama", "")
            ]
        elif competition == "tri_lomba":
            row_data = [
                data_dict.get("nama", "")
            ]
        elif competition == "got_talent_nusantara":
            row_data = [
                data_dict.get("nama", "")
            ]
        elif competition == "jejak_juang_cerdas":
            row_data = [
                data_dict.get("nama", "")
            ]
        elif competition == "mystery_mission":
            row_data = [
                data_dict.get("nama", "")
            ]
        elif competition == "balon_berantai":
            row_data = [
                data_dict.get("nama", "")
            ]
        elif competition == "makan_kerupuk":
            row_data = [
                data_dict.get("nama", "")
            ]
        elif competition == "sarung_sigap":
            row_data = [
                data_dict.get("nama", "")
            ]
        elif competition == "fashion_show":
            row_data = [
                data_dict.get("nama", "")
            ]
        else:
            error_msg = f"No data mapping for competition: {competition}"
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[ERROR] {error_msg}\n")
            return False

        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Getting client...\n")
        try:
            client = get_google_sheets_client()
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[save_registration] Client obtained\n")
        except Exception as e:
            with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
                f.write(f"[save_registration] Client error: {e}\n")
            raise
        
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Appending to sheet...\n")
        result = append_to_sheet(client, sheet_name, row_data)
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[save_registration] Append result: {result}\n")
        return result
    except Exception as e:
        with open('nusakarsa_debug.log', 'a', encoding='utf-8') as f:
            f.write(f"[ERROR] Exception in save_registration: {e}\n")
            import traceback
            f.write(traceback.format_exc())
        return False

# Example usage
if __name__ == "__main__":
    # Test with sample data
    test_data = {
        "nama": "John Doe"
    }

    save_registration("hias_bekal", test_data)