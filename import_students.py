import csv
import json
import random

mayor_csv = 'static/data/SMA MAYOR.csv'
cgc_csv = 'static/data/SMA CGC.csv'
students_json = 'static/data/students.json'

def find_column(headers, keywords):
    for i, h in enumerate(headers):
        h_clean = h.strip().upper().replace('\ufeff', '')
        for kw in keywords:
            if kw in h_clean:
                return i
    return -1

def import_mayor():
    students = []
    with open(mayor_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader, [])
        idx_nama = find_column(headers, ['NAMA'])
        idx_kelas = find_column(headers, ['KELAS'])
        if idx_nama == -1 or idx_kelas == -1:
            idx_nama, idx_kelas = 2, 5  # fallback
        for row in reader:
            if len(row) <= max(idx_nama, idx_kelas):
                continue
            no = row[0].strip()
            nama = row[idx_nama].strip()
            kelas = row[idx_kelas].strip()
            if no and nama and kelas and nama != 'NAMA PESERTA DIDIK':
                student_id = f"STUDENT_MAYOR_{no}_{random.randint(1000, 9999)}"
                students.append({"id": student_id, "nama": nama, "kelas": kelas})
    return students

def import_cgc():
    students = []
    with open(cgc_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader, [])
        idx_nama = find_column(headers, ['NAMA'])
        idx_kelas = find_column(headers, ['KELAS'])
        if idx_nama == -1 or idx_kelas == -1:
            idx_nama, idx_kelas = 2, 7  # fallback
        for row in reader:
            if len(row) <= max(idx_nama, idx_kelas):
                continue
            no = row[0].strip()
            nama = row[idx_nama].strip()
            kelas = row[idx_kelas].strip()
            if no and nama and kelas and nama != 'NAMA PESERTA DIDIK':
                student_id = f"STUDENT_CGC_{no}_{random.randint(1000, 9999)}"
                students.append({"id": student_id, "nama": nama, "kelas": kelas})
    return students

def main():
    print("Importing students data...")
    mayor_students = import_mayor()
    cgc_students = import_cgc()
    all_students = mayor_students + cgc_students
    print(f"Imported {len(mayor_students)} Mayor students")
    print(f"Imported {len(cgc_students)} CGC students")
    print(f"Total students: {len(all_students)}")
    with open(students_json, 'w', encoding='utf-8') as f:
        json.dump(all_students, f, indent=4, ensure_ascii=False)
    print(f"Saved to {students_json}")

if __name__ == "__main__":
    main()
