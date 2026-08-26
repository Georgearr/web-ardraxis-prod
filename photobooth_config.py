"""
Konfigurasi Ravenith Photobooth.
Salin URL deployment Google Apps Script ke .env: RAVENITH_PHOTOBOOTH_GAS_URL
"""

import os

# Endpoint Google Apps Script (wajib diisi di .env untuk production)
PHOTOBOOTH_GAS_URL = os.getenv(
    "RAVENITH_PHOTOBOOTH_GAS_URL",
    os.getenv(
        "PHOTOBOOTH_GAS_URL",
        "https://script.google.com/macros/s/AKfycbz4hYDqkggDwrURThLylLmC1s_rZCIWGwHthky-lSgFjx2wEfBK9KOjoxlDasOYgId8pA/exec",
    ),
)

# Cache response GAS (detik)
PHOTOBOOTH_CACHE_TTL_SECONDS = int(os.getenv("PHOTOBOOTH_CACHE_TTL_SECONDS", "300"))

# Banner hero (file di static/img/banner/)
PHOTOBOOTH_BANNER = os.getenv("PHOTOBOOTH_BANNER", "salvatore_banner.png")

# Pagination default
PHOTOBOOTH_PAGE_SIZE = int(os.getenv("PHOTOBOOTH_PAGE_SIZE", "12"))

# Tema (selaras Ravenith / Bodhivara)
PHOTOBOOTH_THEME = {
    "bg": "#e4a464",
    "container": "#c68441",
    "container_dark": "#b67637",
    "primary": "#c08141",
    "primary_dark": "#a93320",
    "text": "#ffffff",
    "accent": "#fff9f6",
}
