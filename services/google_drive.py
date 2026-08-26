"""
Ambil daftar foto photobooth dari Google Apps Script (Google Drive).
Tanpa database; cache in-memory 5 menit.
"""

import json
import re
import ssl
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

from photobooth_config import PHOTOBOOTH_GAS_URL, PHOTOBOOTH_CACHE_TTL_SECONDS

_CACHE: dict[str, Any] = {
    "photos": None,
    "fetched_at": 0.0,
    "error": None,
}

_DRIVE_FILE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{10,}$")


def _https_context() -> ssl.SSLContext:
    """CA bundle untuk HTTPS (Python macOS sering tanpa cert.pem bawaan)."""
    return ssl.create_default_context(cafile=certifi.where())


def _photo_for_client(photo: dict[str, Any]) -> dict[str, Any]:
    """URL tampilan lewat proxy Flask — Drive /uc?export=view sering gagal di <img>."""
    out = dict(photo)
    fid = (out.get("id") or "").strip()
    if not fid:
        return out
    if not out.get("downloadUrl"):
        out["downloadUrl"] = f"https://drive.google.com/uc?export=download&id={fid}"
    out["url"] = f"/api/photobooth/image/{fid}"
    return out


def _photos_for_client(photos: list[Any]) -> list[dict[str, Any]]:
    return [_photo_for_client(p) for p in photos if isinstance(p, dict)]


def _drive_image_sources(file_id: str) -> list[str]:
    return [
        f"https://drive.google.com/thumbnail?id={file_id}&sz=w1200",
        f"https://drive.google.com/uc?export=view&id={file_id}",
    ]


def _looks_like_image(data: bytes) -> bool:
    if len(data) < 12:
        return False
    if data[:8] == b"\x89PNG\r\n\x1a\n" or data[:2] == b"\xff\xd8":
        return True
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    return False


def _guess_mime(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:2] == b"\xff\xd8":
        return "image/jpeg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def fetch_drive_image(file_id: str) -> tuple[bytes, str] | None:
    """
    Ambil bytes gambar dari Drive (thumbnail / view).
    Folder/file harus bisa diakses publik (Anyone with the link).
    """
    file_id = (file_id or "").strip()
    if not _DRIVE_FILE_ID_RE.match(file_id):
        return None

    headers = {"User-Agent": "Mozilla/5.0 (compatible; RavenithPhotobooth/1.0)"}
    for src in _drive_image_sources(file_id):
        try:
            req = Request(src, headers=headers)
            with urlopen(req, timeout=25, context=_https_context()) as resp:
                data = resp.read()
                ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
                if not data or len(data) < 200:
                    continue
                if "image/" in ctype:
                    return data, ctype
                if _looks_like_image(data):
                    return data, _guess_mime(data)
        except (HTTPError, URLError, TimeoutError, OSError):
            continue
    return None


def _gas_configured() -> bool:
    url = (PHOTOBOOTH_GAS_URL or "").strip()
    return bool(url) and "PASTE_GAS_URL" not in url


def _fetch_from_gas(params: dict[str, str] | None = None) -> dict[str, Any]:
    if not _gas_configured():
        return {
            "success": False,
            "photos": [],
            "message": "URL Google Apps Script belum dikonfigurasi (RAVENITH_PHOTOBOOTH_GAS_URL).",
        }

    query = params or {}
    url = PHOTOBOOTH_GAS_URL
    if query:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{urlencode(query)}"

    req = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(req, timeout=30, context=_https_context()) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            if not isinstance(data, dict):
                return {"success": False, "photos": [], "message": "Format JSON tidak valid."}
            if "photos" not in data:
                data["photos"] = []
            return data
    except HTTPError as e:
        return {
            "success": False,
            "photos": [],
            "message": f"HTTP error {e.code}: {e.reason}",
        }
    except URLError as e:
        return {
            "success": False,
            "photos": [],
            "message": f"Koneksi gagal: {e.reason}",
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "photos": [],
            "message": "Response bukan JSON valid.",
        }
    except Exception as e:
        return {
            "success": False,
            "photos": [],
            "message": str(e),
        }


def _cache_valid() -> bool:
    if _CACHE["photos"] is None and _CACHE["error"] is None:
        return False
    age = time.time() - _CACHE["fetched_at"]
    return age < PHOTOBOOTH_CACHE_TTL_SECONDS


def _refresh_cache(params: dict[str, str] | None = None) -> dict[str, Any]:
    data = _fetch_from_gas(params)
    _CACHE["fetched_at"] = time.time()
    if data.get("success"):
        _CACHE["photos"] = data.get("photos") or []
        _CACHE["error"] = None
    else:
        _CACHE["photos"] = []
        _CACHE["error"] = data.get("message", "Gagal memuat foto.")
    return data


def get_photos(force_refresh: bool = False) -> dict[str, Any]:
    """
    Mengambil semua foto dari GAS (dengan cache 5 menit).
    Returns: { success, photos: [{ id, name, url }], message? }
    """
    if not force_refresh and _cache_valid() and _CACHE["error"] is None:
        return {
            "success": True,
            "photos": _photos_for_client(list(_CACHE["photos"] or [])),
            "cached": True,
        }

    if not force_refresh and _cache_valid() and _CACHE["error"]:
        return {
            "success": False,
            "photos": [],
            "message": _CACHE["error"],
            "cached": True,
        }

    data = _refresh_cache({"action": "list"})
    data["cached"] = False
    if data.get("success"):
        data["photos"] = _photos_for_client(data.get("photos") or [])
    return data


def search_photos(keyword: str, force_refresh: bool = False) -> dict[str, Any]:
    """
    Filter foto berdasarkan nama (client-side setelah fetch, atau via GAS jika mendukung).
    """
    keyword = (keyword or "").strip().lower()
    result = get_photos(force_refresh=force_refresh)

    if not result.get("success"):
        return result

    photos = result.get("photos") or []
    if not keyword:
        return {**result, "photos": photos}

    filtered = [
        p
        for p in photos
        if keyword in (p.get("name") or "").lower()
        or keyword in (p.get("id") or "").lower()
    ]
    return {**result, "photos": filtered, "search": keyword}


def clear_cache() -> None:
    """Hapus cache (untuk admin / refresh manual)."""
    _CACHE["photos"] = None
    _CACHE["fetched_at"] = 0.0
    _CACHE["error"] = None
