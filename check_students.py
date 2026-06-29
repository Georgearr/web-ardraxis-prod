import json
import sys

# Set UTF-8 encoding for output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Read students.json
with open('static/data/students.json', 'r', encoding='utf-8') as f:
    students = json.load(f)

print(f"Total students: {len(students)}")

# Check for invalid data
invalid_students = []
for i, student in enumerate(students):
    kelas = student.get('kelas', '')
    nama = student.get('nama', '')
    
    # Check if kelas is just "KELAS" or empty
    if kelas == 'KELAS' or not kelas or kelas.strip() == '':
        invalid_students.append({
            'index': i,
            'nama': nama,
            'kelas': kelas,
            'id': student.get('id', '')
        })

print(f"\nInvalid students (kelas = 'KELAS' or empty): {len(invalid_students)}")
for s in invalid_students[:10]:  # Show first 10
    print(f"  - {s['nama']} | Kelas: '{s['kelas']}' | ID: {s['id']}")

# Remove invalid students
if invalid_students:
    print(f"\nRemoving {len(invalid_students)} invalid students...")
    valid_students = [s for s in students if s.get('kelas') not in ['KELAS', '', None]]
    
    # Save cleaned data
    with open('static/data/students.json', 'w', encoding='utf-8') as f:
        json.dump(valid_students, f, indent=4, ensure_ascii=False)
    
    print(f"Saved {len(valid_students)} valid students")
else:
    print("\nNo invalid students found.")
