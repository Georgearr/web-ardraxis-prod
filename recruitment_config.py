import os
import json
from dotenv import load_dotenv

load_dotenv()

RECRUITMENT_ENABLED = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

AUTOSAVE_DELAY = 1
SESSION_TIMEOUT = 86400

VALID_SCHOOLS = {"sma-mayor", "sma-cgc"}


def get_sekbid_json_path(school_key=None):
    if school_key:
        safe = school_key.replace("-", "_")
        return os.path.join(BASE_DIR, "config", f"recruitment_{safe}.json")
    return os.path.join(BASE_DIR, "config", "recruitment_sekbid.json")


def get_progress_dir(school_key=None):
    base = os.path.join(BASE_DIR, "progress_data")
    if school_key:
        return os.path.join(base, school_key)
    return base


def load_school_json(school_key):
    path = get_sekbid_json_path(school_key)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_sekbid_data(school_key=None):
    path = get_sekbid_json_path(school_key)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "sekbid" in data:
                return data["sekbid"]
            return data
    except Exception:
        return {}


def get_school_metadata(school_key):
    data = load_school_json(school_key)
    if data and "school" in data:
        return data["school"]
    return {
        "name": school_key.upper() if school_key else "Sekolah",
        "short": school_key.split("-")[-1].upper() if school_key and "-" in school_key else "",
        "title": "Recruitment OSIS",
        "subtitle": "Bergabunglah menjadi bagian dari OSIS periode 2026/2027",
        "hero_title": "Rekrutmen Pengurus OSIS",
        "hero_text": "",
        "success_text": "Terima kasih telah mendaftar.",
    }
