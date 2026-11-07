import os
import shutil
import re

# 1. Fotokabinet cleanup: keep only 1 image per person and 1 per sekbid
with open('templates/about_us.html', 'r', encoding='utf-8') as f:
    text = f.read()

sekbid_imgs = re.findall(r'sekbid_image:\s*\[\s*"([^"]+)"', text)
member_imgs = re.findall(r'images:\s*\[\s*"([^"]+)"', text)
keep_relative = set(sekbid_imgs + member_imgs)

base_fotokabinet = os.path.abspath('static/img/fotokabinet')
deleted_kabinet_count = 0
deleted_kabinet_bytes = 0

for root, dirs, files in os.walk(base_fotokabinet):
    for file in files:
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, base_fotokabinet).replace('\\', '/')
        if rel_path not in keep_relative:
            deleted_kabinet_bytes += os.path.getsize(full_path)
            os.remove(full_path)
            deleted_kabinet_count += 1

print(f"Deleted {deleted_kabinet_count} extra images in fotokabinet ({deleted_kabinet_bytes / (1024*1024):.2f} MB saved).")

# Remove any empty subdirectories in fotokabinet
for root, dirs, files in os.walk(base_fotokabinet, topdown=False):
    for d in dirs:
        dir_path = os.path.join(root, d)
        if not os.listdir(dir_path):
            os.rmdir(dir_path)

# 2. Delete event image folders
folders_to_delete = [
    'static/img/afterevent',
    'static/img/festiora',
    'static/img/meloria',
    'static/img/nusakarsa',
    'static/img/ravenith',
    'static/img/salvatore',
    'static/img/valentine'
]

deleted_folder_bytes = 0
for folder in folders_to_delete:
    abs_folder = os.path.abspath(folder)
    if os.path.exists(abs_folder):
        size = sum(os.path.getsize(os.path.join(r, f)) for r, d, files in os.walk(abs_folder) for f in files)
        deleted_folder_bytes += size
        shutil.rmtree(abs_folder)
        print(f"Deleted folder {folder} ({size / (1024*1024):.2f} MB).")

# 3. Clean redundant .jpg in ardrazine (keep WebP)
ardrazine_dir = os.path.abspath('static/img/ardrazine')
deleted_jpg_count = 0
deleted_jpg_bytes = 0
for f in os.listdir(ardrazine_dir):
    if f.lower().endswith('.jpg') or f.lower().endswith('.jpeg'):
        p = os.path.join(ardrazine_dir, f)
        deleted_jpg_bytes += os.path.getsize(p)
        os.remove(p)
        deleted_jpg_count += 1

print(f"Deleted {deleted_jpg_count} redundant jpg in ardrazine ({deleted_jpg_bytes / (1024*1024):.2f} MB saved).")

total_saved_mb = (deleted_kabinet_bytes + deleted_folder_bytes + deleted_jpg_bytes) / (1024*1024)
print(f"\nTOTAL DISK SPACE SAVED: {total_saved_mb:.2f} MB!")
