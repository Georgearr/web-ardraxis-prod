"""Konfigurasi lomba Ravenith — limit, link LINE, metadata sheet."""

import os

# Ganti nama file di static/img/banner/ (bebas, sesuaikan ekstensi .png / .jpg)
RAVENITH_BANNER = "ravenith_banner.png"

# Poster tiap lomba: taruh di static/img/ravenith/ (ganti nama file di bawah)
RAVENITH_POSTER_DIR = "img/ravenith"

RAVENITH_APPS_SCRIPT_URL = os.getenv(
    "RAVENITH_APPS_SCRIPT_URL",
    "https://script.google.com/macros/s/AKfycbxD-dED0fur927OKcUPyAh2NcOIk6n_0zCl3A4Eq4aQVEpG3Zfbk-4icB_THg5BCSETpA/exec",
)

# limit: 0 = tidak ada batas; limit_type: "team" | "participant"
RAVENITH_COMPETITIONS = {
    "sweet_evidence": {
        "title": "Sweet Evidence",
        "poster": "sweet_evidence.png",
        "sheet_name": "Sweet_Evidence",
        "limit": 10,
        "limit_type": "team",
        "line_group": "https://line.me/ti/g/JtG6F7WJ-H",
    },
    "escape_room": {
        "title": "Escape Room",
        "poster": "escape_room.png",
        "sheet_name": "Escape_Room",
        "limit": 0,
        "limit_type": "team",
        "line_group": "https://line.me/R/ti/g/7KzfvrMZ5F",
    },
    "secret_investigation": {
        "title": "Secret Investigation",
        "poster": "secret_investigation.png",
        "sheet_name": "Secret_Investigation",
        "limit": 0,
        "limit_type": "team",
        "line_group": "https://line.me/R/ti/g/c-ZG_expwt",
    },
    "family_100": {
        "title": "Family 100",
        "poster": "family_100.jpg",
        "sheet_name": "Family_100",
        "limit": 0,
        "limit_type": "team",
        "line_group": "https://line.me/R/ti/g/trLe7TC_2M",
    },
    "badminton": {
        "title": "Badminton",
        "poster": "badminton.jpg",
        "sheet_name": "Badminton",
        "limit": 12,
        "limit_type": "team",
        "line_group": "https://line.me/R/ti/g/t6vtrWjXKE",
    },
    "design_disguise": {
        "title": "Design your Disguise Workshop",
        "poster": "design_your_disguise.png",
        "sheet_name": "Design_Disguise",
        "limit": 20,
        "limit_type": "participant",
        "line_group": "https://line.me/R/ti/g/vgspCn7DNk",
        "payment_drive": "https://drive.google.com/drive/folders/1HT9vJxXjDKCQcaRPxtJh04xWrOL2b6D-?usp=share_link",
    },
    "futsal": {
        "title": "Lomba Futsal",
        "poster": "futsal.jpg",
        "sheet_name": "Futsal",
        "limit": 16,
        "limit_type": "team",
        "line_group": "https://line.me/R/ti/g/8CR9r7XtZc",
    },
    "fotografi": {
        "title": "Fotografi",
        "poster": "photography.jpg",
        "sheet_name": "Fotografi",
        "limit": 15,
        "limit_type": "team",
        "line_group": "https://line.me/R/ti/g/2w64T59nRQ",
    },
    "esport": {
        "title": "E-Sport (Mobile Legends)",
        "poster": "esport.jpg",
        "sheet_name": "E_Sport",
        "limit": 16,
        "limit_type": "team",
        "line_group": "https://line.me/R/ti/g/eyz_f3nYwL",
    },
    "ultimate_heist": {
        "title": "Ultimate Heist",
        "poster": "ultimate_heist.png",
        "sheet_name": "Ultimate_Heist",
        "limit": 0,
        "limit_type": "team",
        "line_group": "https://line.me/ti/g/Bvkj95tmYG",
    },
}

# Urutan tampil di halaman utama
RAVENITH_LOMBA_ORDER = [
    "sweet_evidence",
    "escape_room",
    "secret_investigation",
    "family_100",
    "badminton",
    "design_disguise",
    "futsal",
    "fotografi",
    "esport",
    "ultimate_heist",
]
