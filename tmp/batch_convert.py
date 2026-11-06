import os
import sys
import glob
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARDRAZINE_DIR = os.path.join(BASE_DIR, "static", "img", "ardrazine")
TMP_DIR = os.path.join(BASE_DIR, "tmp")

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

print(f"Using browser: {chrome_path}")

svg_files = sorted(glob.glob(os.path.join(ARDRAZINE_DIR, "*.svg")), key=lambda p: int(re.match(r"^(\d+)", os.path.basename(p)).group(1)))
print(f"Found {len(svg_files)} SVG files to convert.")

def convert_file(svg_path):
    base_name = os.path.basename(svg_path)
    stem, _ = os.path.splitext(base_name)
    tmp_png = os.path.join(TMP_DIR, f"{stem}.png")
    out_webp = os.path.join(ARDRAZINE_DIR, f"{stem}.webp")
    out_jpg = os.path.join(ARDRAZINE_DIR, f"{stem}.jpg")

    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--window-size=1240,1754",
        f"--screenshot={tmp_png}",
        f"file:///{os.path.abspath(svg_path)}"
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Convert to WebP & JPG with PIL
    img = Image.open(tmp_png)
    
    # Save WebP
    img.save(out_webp, "WEBP", quality=85, method=6)
    
    # Save JPG
    rgb_img = img.convert("RGB")
    rgb_img.save(out_jpg, "JPEG", quality=85, optimize=True)

    # Clean up tmp png
    if os.path.exists(tmp_png):
        os.remove(tmp_png)

    orig_size = os.path.getsize(svg_path) / (1024 * 1024)
    webp_size = os.path.getsize(out_webp) / 1024
    jpg_size = os.path.getsize(out_jpg) / 1024

    return (stem, orig_size, webp_size, jpg_size)

t0 = time.time()
# Run with 4 concurrent workers to convert fast
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(convert_file, svg_files))
t1 = time.time()

print(f"\nAll {len(results)} files converted in {t1 - t0:.2f} seconds!")
total_orig = sum(r[1] for r in results)
total_webp = sum(r[2] for r in results) / 1024
total_jpg = sum(r[3] for r in results) / 1024

print(f"Total original SVG size: {total_orig:.2f} MB")
print(f"Total WebP size: {total_webp:.2f} MB")
print(f"Total JPG size: {total_jpg:.2f} MB")
print(f"Compression ratio: {total_orig / total_webp:.1f}x smaller!")
