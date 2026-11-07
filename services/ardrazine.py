"""Ardrazine magazine asset loader.

Membaca aset halaman majalah di ``static/img/ardrazine`` (format WebP, JPG, PNG, SVG).
Menghasilkan daftar item yang terurut secara numerik berdasarkan nomor urut di awal nama file,
dilengkapi metadata resolusi, aspect ratio, dan ukuran file.
Hasil di-cache dalam memori secara thread-safe.
"""

import logging
import os
import re
import threading
from PIL import Image

log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARDRAZINE_DIR = os.path.join(BASE_DIR, "static", "img", "ardrazine")

# Format nama file: {order}_{identifier}.{ext} atau {order}.{ext}
_FILENAME_RE = re.compile(
    r"^(\d+)(?:[A-Za-z0-9._-]*)\.(webp|jpg|jpeg|png|svg)$",
    re.IGNORECASE,
)

_cache_lock = threading.Lock()
_cache_signature = None
_cache_items = ()


def _build_signature(directory):
    try:
        names = os.listdir(directory)
    except OSError:
        return (directory, None)

    entries = []
    for name in sorted(names):
        match = _FILENAME_RE.match(name)
        if not match:
            continue
        full_path = os.path.join(directory, name)
        try:
            stat = os.stat(full_path)
            if os.path.isfile(full_path):
                entries.append((name, stat.st_mtime_ns, stat.st_size))
        except OSError:
            continue
    return (directory, tuple(entries))


def _get_image_dimensions(file_path):
    try:
        with Image.open(file_path) as img:
            return img.size  # (width, height)
    except Exception as exc:
        log.warning("Gagal membaca dimensi %s: %s", file_path, exc)
        return 1240, 1754


def _scan_magazine_pages(directory):
    try:
        names = os.listdir(directory)
    except OSError:
        return ()

    # Kelompokkan file berdasarkan nomor urut (order)
    pages_map = {}
    for name in names:
        match = _FILENAME_RE.match(name)
        if not match:
            continue
        order = int(match.group(1))
        ext = match.group(2).lower()
        full_path = os.path.join(directory, name)
        if not os.path.isfile(full_path):
            continue

        if order not in pages_map:
            pages_map[order] = {}
        pages_map[order][ext] = name

    sorted_orders = sorted(pages_map.keys())
    total_pages = len(sorted_orders)
    items = []

    for order in sorted_orders:
        formats = pages_map[order]
        # Prioritaskan WebP, fallback ke JPG/JPEG/PNG/SVG
        primary_ext = None
        for ext_candidate in ("webp", "jpg", "jpeg", "png", "svg"):
            if ext_candidate in formats:
                primary_ext = ext_candidate
                break
        if not primary_ext:
            continue

        primary_file = formats[primary_ext]
        jpg_file = formats.get("jpg") or formats.get("jpeg")
        full_path = os.path.join(directory, primary_file)

        width, height = _get_image_dimensions(full_path)
        ratio = f"{width} / {height}" if width and height else "1240 / 1754"

        try:
            size_bytes = os.path.getsize(full_path)
            size_kb = round(size_bytes / 1024, 1)
        except OSError:
            size_kb = 0

        # Label halaman
        if order == 1:
            label = "Cover Depan"
        elif order == total_pages and total_pages > 1:
            label = "Cover Belakang"
        else:
            label = f"Halaman {order}"

        items.append({
            "order": order,
            "filename": primary_file,
            "jpg_filename": jpg_file,
            "label": label,
            "width": width,
            "height": height,
            "ratio": ratio,
            "size_kb": size_kb,
        })

    return tuple(items)


def load_magazine_items(directory=None):
    """Kembalikan daftar item majalah (tuple of dict) dalam urutan numerik."""
    directory = os.path.abspath(directory or ARDRAZINE_DIR)
    signature = _build_signature(directory)

    global _cache_signature, _cache_items
    with _cache_lock:
        if signature == _cache_signature and _cache_items:
            return _cache_items
        items = _scan_magazine_pages(directory)
        _cache_signature = signature
        _cache_items = items
        return items


def clear_cache():
    """Reset cache (berguna untuk testing atau reload manual)."""
    global _cache_signature, _cache_items
    with _cache_lock:
        _cache_signature = None
        _cache_items = ()
