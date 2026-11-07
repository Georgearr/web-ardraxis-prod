import re
import os
import glob

with open('templates/about_us.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Extract sekbid_image[0]
sekbid_imgs = re.findall(r'sekbid_image:\s*\[\s*"([^"]+)"', text)
print(f"Found {len(sekbid_imgs)} sekbid primary images:")
for s in sekbid_imgs[:5]:
    print(" ", s)

# Extract member.images[0]
member_imgs = re.findall(r'images:\s*\[\s*"([^"]+)"', text)
print(f"Found {len(member_imgs)} member primary images:")
for m in member_imgs[:5]:
    print(" ", m)

keep_relative = set(sekbid_imgs + member_imgs)
print(f"Total unique images to keep in fotokabinet: {len(keep_relative)}")

# Check against filesystem
base_dir = os.path.abspath('static/img/fotokabinet')
all_disk_files = []
for root, dirs, files in os.walk(base_dir):
    for file in files:
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, base_dir).replace('\\', '/')
        all_disk_files.append((rel_path, full_path))

print(f"Total files on disk in fotokabinet: {len(all_disk_files)}")
to_keep = []
to_delete = []

for rel_path, full_path in all_disk_files:
    if rel_path in keep_relative:
        to_keep.append(full_path)
    else:
        to_delete.append(full_path)

print(f"Matching to keep: {len(to_keep)}")
print(f"To delete: {len(to_delete)}")

missing = keep_relative - {rel for rel, _ in all_disk_files}
if missing:
    print("WARNING: Some referenced images not found on disk:", missing)
