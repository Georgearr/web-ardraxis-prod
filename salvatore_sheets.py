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
    SPREADSHEET_ID = None

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
    if not SHEETS_CREDENTIALS_JSON:
        raise ValueError("SALVATORE_SHEETS_CREDENTIALS environment variable not set")

    try:
        creds_info = json.loads(SHEETS_CREDENTIALS_JSON)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in SALVATORE_SHEETS_CREDENTIALS: {e}")

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(creds_info, scopes=scope)
    client = gspread.authorize(creds)
    return client

def append_to_sheet(client, sheet_name, data):
    """Append data to the specified sheet."""
    if not SPREADSHEET_ID:
        error_msg = "SALVATORE_SPREADSHEET_URL environment variable not set or invalid"
        print(f"❌ {error_msg}")
        return False

    try:
        print(f"🔄 Opening spreadsheet with ID: {SPREADSHEET_ID}")
        # Open the spreadsheet by ID
        spreadsheet = client.open_by_key(SPREADSHEET_ID)
        print(f"✅ Spreadsheet opened successfully: {spreadsheet.title}")

        # Get or create the sheet
        try:
            print(f"🔄 Looking for sheet: {sheet_name}")
            sheet = spreadsheet.worksheet(sheet_name)
            print(f"✅ Sheet found: {sheet_name}")
        except gspread.WorksheetNotFound:
            print(f"📝 Sheet '{sheet_name}' not found, creating it...")
            # Create sheet if it doesn't exist
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            print(f"✅ Sheet created: {sheet_name}")

        # Add timestamp
        data.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(f"📊 Appending data: {data}")

        # Append the data
        result = sheet.append_row(data)
        print(f"✅ Data appended successfully to {sheet_name}")
        return True

    except Exception as e:
        print(f"❌ Error appending to {sheet_name}: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        return False

def save_registration(competition, data_dict):
    """Save registration data for a specific competition."""
    if competition not in SHEETS:
        print(f"❌ Unknown competition: {competition}")
        return False

    sheet_name = SHEETS[competition]

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
        print(f"❌ No data mapping for competition: {competition}")
        return False

    client = get_google_sheets_client()
    return append_to_sheet(client, sheet_name, row_data)

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