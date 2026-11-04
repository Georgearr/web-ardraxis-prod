"""Ardrazine magazine asset loader.

Membaca seluruh file ``.svg`` di ``static/img/ardrazine``, memvalidasi dan
mensanitasi isi setiap SVG, lalu menyimpan hasilnya sebagai markup inline siap
tempel. Hasilnya di-cache berdasarkan (nama, ukuran, mtime) supaya route
``/magazine`` tidak membaca dan mem-parse ulang seluruh direktori pada setiap
request.
"""

import logging
import os
import re
import threading
from xml.etree import ElementTree as ET

from markupsafe import Markup

log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARDRAZINE_DIR = os.path.join(BASE_DIR, "static", "img", "ardrazine")

SVG_NAMESPACE = "http://www.w3.org/2000/svg"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"

# Format nama file: {order}_{identifier}_{identifier}.svg
# Angka paling depan adalah nomor urut, sisanya identifier (boleh > 1 segmen).
_FILENAME_RE = re.compile(r"^(\d+)(?:_[A-Za-z0-9.-]+)+\.svg$", re.IGNORECASE)

_XMLNS_RE = re.compile(rb'xmlns(?::([\w.-]+))?\s*=\s*"([^"]*)"')
_ENTITY_DECL_RE = re.compile(rb"<!ENTITY", re.IGNORECASE)
_LENGTH_RE = re.compile(r"^\s*([0-9]*\.?[0-9]+)")
_SCHEME_RE = re.compile(r"^([A-Za-z][A-Za-z0-9+.\-]*):")
_SAFE_DATA_URI_RE = re.compile(r"^data:image/(?:png|jpe?g|gif|webp|avif|bmp)\b", re.IGNORECASE)
_UNSAFE_STYLE_RE = re.compile(
    r"(?:javascript|vbscript)\s*:|expression\s*\(|behaviou?r\s*:|-moz-binding",
    re.IGNORECASE,
)

# Elemen yang tidak pernah dibutuhkan untuk rendering gambar dan bisa
# dieksploitasi untuk menjalankan skrip di halaman.
_BLOCKED_ELEMENTS = frozenset(
    {
        "script",
        "foreignobject",
        "iframe",
        "frame",
        "frameset",
        "object",
        "embed",
        "applet",
        "audio",
        "video",
        "handler",
    }
)

_ALLOWED_URI_SCHEMES = frozenset({"http", "https", "mailto", "tel", "ftp"})

_cache_lock = threading.Lock()
_cache_signature = None
_cache_items = ()


def _local_name(name):
    """Kembalikan nama tanpa namespace: ``{uri}href`` -> ``href``."""
    if name.startswith("{"):
        return name.split("}", 1)[1]
    return name


def _is_unsafe_uri(value):
    """True bila URL berpotensi mengeksekusi skrip atau memuat konten berbahaya."""
    value = value.strip()
    if not value or value.startswith("#"):
        return False
    if _SAFE_DATA_URI_RE.match(value):
        return False
    match = _SCHEME_RE.match(value)
    if match is None:
        return False
    # Termasuk "data:" yang bukan gambar raster (sudah ditangani di atas).
    return match.group(1).lower() not in _ALLOWED_URI_SCHEMES


def _register_namespaces(raw):
    """Daftarkan prefix xmlns asli supaya hasil serialisasi tetap valid.

    Tanpa ini ``xlink:href`` bisa berubah menjadi ``ns0:href`` yang tidak
    dikenali parser HTML sehingga gambar di dalam SVG tidak tampil.
    """
    for prefix, uri in _XMLNS_RE.findall(raw):
        if not uri:
            continue
        try:
            declared_prefix = prefix.decode("ascii") if prefix else ""
            declared_uri = uri.decode("ascii")
        except UnicodeDecodeError:
            continue

        # Prefix kosong hanya boleh dipakai satu namespace: SVG.
        # Selain itu biarkan ET membuat prefix sendiri (ns0, ns1, ...).
        if declared_uri == SVG_NAMESPACE:
            declared_prefix = ""
        elif not declared_prefix:
            continue

        try:
            ET.register_namespace(declared_prefix, declared_uri)
        except (ValueError, TypeError):
            continue

    # Dua namespace di bawah ini wajib menang: <svg> tanpa prefix supaya tetap
    # dikenali parser HTML, xlink:href supaya atributnya tidak kehilangan
    # namespace-nya.
    for prefix, uri in (("", SVG_NAMESPACE), ("xlink", XLINK_NAMESPACE)):
        try:
            ET.register_namespace(prefix, uri)
        except (ValueError, TypeError):
            continue


def _sanitize_element(element):
    for child in list(element):
        local = _local_name(child.tag).lower()
        if local in _BLOCKED_ELEMENTS:
            element.remove(child)
        elif local == "style" and _UNSAFE_STYLE_RE.search(child.text or ""):
            element.remove(child)
        else:
            _sanitize_element(child)

    for attribute in list(element.attrib):
        local = _local_name(attribute)
        lowered = local.lower()
        value = element.attrib[attribute]
        if lowered.startswith("on"):
            del element.attrib[attribute]
        elif lowered in ("href", "src"):
            if _is_unsafe_uri(value):
                del element.attrib[attribute]
        elif lowered == "style" and _UNSAFE_STYLE_RE.search(value):
            del element.attrib[attribute]


def _parse_svg(raw):
    # xml.etree ElementTree rentan terhadap "billion laughs" / quadratic blowup,
    # jadi deklarasi entity ditolak sebelum file diparse sama sekali.
    if _ENTITY_DECL_RE.search(raw):
        raise ValueError("deklarasi DTD entity tidak diizinkan")

    root = ET.fromstring(raw)

    if root.tag not in ("svg", "{%s}svg" % SVG_NAMESPACE):
        raise ValueError("root element bukan <svg>")
    return root


def _to_float(value):
    if not value:
        return None
    match = _LENGTH_RE.match(value)
    if not match:
        return None
    try:
        number = float(match.group(1))
    except ValueError:
        return None
    return number if number > 0 else None


def _intrinsic_size(root):
    """Kembalikan (width, height) intrinsik dari atribut root atau viewBox."""
    width = _to_float(root.get("width"))
    height = _to_float(root.get("height"))
    if width and height:
        return width, height

    view_box = root.get("viewBox") or root.get("viewbox")
    if view_box:
        parts = [part for part in re.split(r"[\s,]+", view_box.strip()) if part]
        if len(parts) == 4:
            try:
                box_width = float(parts[2])
                box_height = float(parts[3])
            except ValueError:
                box_width = box_height = 0
            if box_width > 0 and box_height > 0:
                return box_width, box_height
    return None, None


def _build_signature(directory):
    try:
        names = os.listdir(directory)
    except OSError:
        return (directory, None)

    entries = []
    for name in sorted(names):
        if not _FILENAME_RE.match(name):
            continue
        try:
            stat = os.stat(os.path.join(directory, name))
        except OSError:
            continue
        if not os.path.isfile(os.path.join(directory, name)):
            continue
        entries.append((name, stat.st_mtime_ns, stat.st_size))
    return (directory, tuple(entries))


def _ordered_names(directory):
    try:
        names = os.listdir(directory)
    except OSError:
        return []

    collected = []
    for name in names:
        match = _FILENAME_RE.match(name)
        if not match:
            continue
        if not os.path.isfile(os.path.join(directory, name)):
            continue
        collected.append((int(match.group(1)), name))

    # Urut numerik berdasar nomor urut, nama file sebagai secondary key.
    collected.sort(key=lambda entry: (entry[0], entry[1]))
    return collected


def _load_item(path, order, name):
    with open(path, "rb") as handle:
        raw = handle.read()

    _register_namespaces(raw)
    root = _parse_svg(raw)
    _sanitize_element(root)

    markup = Markup(ET.tostring(root, encoding="unicode"))
    width, height = _intrinsic_size(root)
    ratio = None
    if width and height:
        ratio = "%g / %g" % (width, height)

    return {
        "order": order,
        "name": name,
        "markup": markup,
        "width": width,
        "height": height,
        "ratio": ratio,
    }


def _load_items(directory):
    items = []
    for order, name in _ordered_names(directory):
        try:
            items.append(_load_item(os.path.join(directory, name), order, name))
        except Exception as exc:  # file rusak/kasar dilewati, route tetap jalan
            log.warning("Ardrazine: melewati %s (%s)", name, exc)
    return tuple(items)


def load_magazine_items(directory=None):
    """Kembalikan daftar item magazine (tuple of dict) dalam urutan numerik."""
    directory = os.path.abspath(directory or ARDRAZINE_DIR)
    signature = _build_signature(directory)

    global _cache_signature, _cache_items
    with _cache_lock:
        if signature == _cache_signature:
            return _cache_items
        items = _load_items(directory)
        _cache_signature = signature
        _cache_items = items
        return items


def clear_cache():
    """Reset cache (berguna untuk testing)."""
    global _cache_signature, _cache_items
    with _cache_lock:
        _cache_signature = None
        _cache_items = ()
