import json
import re
from collections import defaultdict

STUDENTS_FILE = 'static/data/students.json'
MENTORS_CSV = 'static/data/Kakak pembina.csv'
STUDENTS_OUT = 'static/data/students.json'
MENTORS_OUT = 'static/data/mentors.json'

with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
    students = json.load(f)

# Remove header row
students = [s for s in students if s.get('kelas') not in ('KELAS', '') and s.get('kelas')]
print(f'Read {len(students)} valid students')

def extract_school(student_id):
    if '_MAYOR_' in student_id:
        return 'Mayor'
    elif '_CGC_' in student_id:
        return 'CGC'
    return 'Unknown'

def parse_mentor_csv():
    mentor_map = {}
    col_school = {}
    with open(MENTORS_CSV, 'r', encoding='utf-8') as f:
        lines = [l.rstrip('\n') for l in f if l.strip()]
    for line in lines:
        cells = [c.strip() for c in line.split(',')]
        for col_idx, cell in enumerate(cells):
            cell = cell.strip()
            if not cell:
                continue
            if cell.startswith('Kelompok'):
                m = re.search(r'\((Mayor|CGC)\)', cell)
                if m:
                    col_school[col_idx] = m.group(1)
            elif ':' in cell:
                parts = cell.split(':', 1)
                code_sub = parts[0].strip()
                name = parts[1].strip()
                cm = re.match(r'10\.(\d+)([AB])', code_sub)
                if cm and col_idx in col_school:
                    key = (col_school[col_idx], cm.group(1), cm.group(2))
                    mentor_map[key] = name
    return mentor_map

mentor_map = parse_mentor_csv()
print(f'Parsed {len(mentor_map)} mentor entries')

def class_to_code(kelas):
    m = re.search(r'X\.(\d+)', kelas)
    return m.group(1) if m else None

class_groups = defaultdict(list)
for s in students:
    class_groups[s['kelas']].append(s)

# Create a mapping from student ID to their assigned kelompok (preserving CSV order)
student_kelompok = {}
for kelas, group in class_groups.items():
    half = (len(group) + 1) // 2
    # Extract only the X.N part (e.g. X.1, X.10) from the full class name
    m_cls = re.match(r'(X\.\d+)', kelas)
    kelas_short = m_cls.group(1) if m_cls else kelas
    for i, s in enumerate(group):
        sub = 'A' if i < half else 'B'
        student_kelompok[s['id']] = f"{kelas_short} {sub}"

# Reconstruct new_students preserving original CSV order
new_students = []
for s in students:
    kelompok = student_kelompok[s['id']]
    sekolah = extract_school(s['id'])
    new_students.append({
        'id': s['id'],
        'nama': s['nama'],
        'kelas': s['kelas'],
        'sekolah': sekolah,
        'kelompok': kelompok
    })

with open(STUDENTS_OUT, 'w', encoding='utf-8') as f:
    json.dump(new_students, f, indent=4, ensure_ascii=False)
print(f'Wrote {len(new_students)} students')

mentors_data = {}
for s in new_students:
    kelompok = s['kelompok']
    if kelompok not in mentors_data:
        cls_code = class_to_code(s['kelas'])
        sub = kelompok[-1]
        school = s['sekolah']
        name = 'Belum ditentukan'
        if cls_code:
            key = (school, cls_code, sub)
            if key in mentor_map:
                name = mentor_map[key]
            else:
                # fallback: jika B tidak ada, pakai A (atau sebaliknya)
                fallback_sub = 'A' if sub == 'B' else 'B'
                fallback_key = (school, cls_code, fallback_sub)
                if fallback_key in mentor_map:
                    name = mentor_map[fallback_key]
        mentors_data[kelompok] = {'name': name}

with open(MENTORS_OUT, 'w', encoding='utf-8') as f:
    json.dump(mentors_data, f, indent=4, ensure_ascii=False)
print(f'Wrote {len(mentors_data)} mentors')

# Verify
print('\n=== VERIFICATION ===')
for s in new_students[:8]:
    k = s['kelompok']
    m = mentors_data[k]['name']
    print(f'{s["nama"]:30s} | {s["sekolah"]:6s} | {s["kelas"]:25s} | {k:30s} | {m}')

belum = sum(1 for v in mentors_data.values() if v['name'] == 'Belum ditentukan')
print(f'\nMentors assigned: {len(mentors_data) - belum}/{len(mentors_data)}')

print('\n=== CLASS DISTRIBUTION ===')
class_counts = defaultdict(lambda: {'A': 0, 'B': 0})
for s in new_students:
    sub = s['kelompok'][-1]
    class_counts[s['kelas']][sub] += 1
for cls in sorted(class_counts.keys()):
    info = class_counts[cls]
    print(f'  {cls:30s} A:{info["A"]:2d} B:{info["B"]:2d}')
