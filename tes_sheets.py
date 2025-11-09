import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load credentials JSON dari .env
creds_info = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))

# Buat objek credentials
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(creds_info, scopes=scopes)

# Bangun service untuk Sheets API
service = build("sheets", "v4", credentials=creds)

# Ambil spreadsheet ID dari URL
spreadsheet_url = os.getenv("GOOGLE_SPREADSHEET_URL")
spreadsheet_id = spreadsheet_url.split("/d/")[1].split("/")[0]

# Uji tulis ke Sheet
range_name = "Sheet1!A1"
values = [["Halo dari Flask 👋"]]
body = {"values": values}

# Update data ke spreadsheet
result = service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range=range_name,
    valueInputOption="RAW",
    body=body
).execute()

print("✅ Data berhasil ditulis ke Google Sheets!")
