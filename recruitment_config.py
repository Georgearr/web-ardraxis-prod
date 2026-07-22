import os
import json
from dotenv import load_dotenv

load_dotenv()

RECRUITMENT_ENABLED = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SEKBID_JSON_PATH = os.path.join(BASE_DIR, "config", "recruitment_sekbid.json")

PROGRESS_DIR = os.path.join(BASE_DIR, "progress_data")

SPREADSHEET_ID = os.getenv("RECRUITMENT_SPREADSHEET_ID", "")

AUTOSAVE_DELAY = 1
SESSION_TIMEOUT = 86400

SEKBID_SHEETS = {
    "sekbid_1": "Sekbid_1_Keimanan",
    "sekbid_2": "Sekbid_2_Budi_Pekerti",
    "sekbid_3": "Sekbid_3_Kepribadian",
    "sekbid_4": "Sekbid_4_Demokrasi",
    "sekbid_5": "Sekbid_5_Kewirausahaan",
    "sekbid_6": "Sekbid_6_Jasmani",
    "sekbid_7": "Sekbid_7_Sastra_Budaya",
    "sekbid_8": "Sekbid_8_Teknologi",
    "sekbid_9": "Sekbid_9_Bahasa_Asing",
    "sekbid_10": "Sekbid_10_Sosial",
}
