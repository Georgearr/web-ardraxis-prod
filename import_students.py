import csv
import json
import random

# File paths
mayor_csv = 'static/data/SMA MAYOR.csv'
cgc_csv = 'static/data/SMA CGC.csv'
mentor_csv = 'static/data/Kakak pembina.csv'
students_json = 'static/data/students.json'
mentors_json = 'static/data/mentors.json'

# Read and parse mentor data
def parse_mentors():
    mentors = {}
    with open(mentor_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not any(row):
                continue
            # Parse format like "Kelompok 1 (Mayor),,,Kelompok 7 (Mayor)"
            for cell in row:
                if cell and 'Kelompok' in cell:
                    group_name = cell.strip()
                    if group_name not in mentors:
                        mentors[group_name] = {}
    return mentors

# Read SMA MAYOR data
def import_mayor():
    students = []
    with open(mayor_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 4:
                no, nama, jenis, kelas = row[0], row[1], row[2], row[3]
                if no and nama and kelas:
                    # Assign kelompok based on class (simple logic)
                    # Extract class number for grouping
                    class_num = ''.join(filter(str.isdigit, kelas))
                    kelompok_num = (int(class_num) % 13) + 1 if class_num else 1
                    kelompok = f"Kelompok {kelompok_num}"
                    
                    student_id = f"STUDENT_MAYOR_{no}_{random.randint(1000, 9999)}"
                    students.append({
                        "id": student_id,
                        "nama": nama.strip(),
                        "kelas": kelas.strip(),
                        "kelompok": kelompok,
                        "jenis": "Mayor",
                        "sub_kelompok": "A"
                    })
    return students

# Read SMA CGC data
def import_cgc():
    students = []
    with open(cgc_csv, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 6:
                no, nis, nama, jenis, jenis_reg, kelas = row[0], row[1], row[2], row[3], row[4], row[5]
                if no and nama and kelas:
                    # Assign kelompok based on class
                    class_num = ''.join(filter(str.isdigit, kelas))
                    kelompok_num = (int(class_num) % 13) + 1 if class_num else 1
                    kelompok = f"Kelompok {kelompok_num}"
                    
                    student_id = f"STUDENT_CGC_{no}_{random.randint(1000, 9999)}"
                    students.append({
                        "id": student_id,
                        "nama": nama.strip(),
                        "kelas": kelas.strip(),
                        "kelompok": kelompok,
                        "jenis": "CGC",
                        "sub_kelompok": "A"
                    })
    return students

# Main import
def main():
    print("Importing students data...")
    
    mayor_students = import_mayor()
    cgc_students = import_cgc()
    
    all_students = mayor_students + cgc_students
    
    print(f"Imported {len(mayor_students)} Mayor students")
    print(f"Imported {len(cgc_students)} CGC students")
    print(f"Total students: {len(all_students)}")
    
    # Save to JSON
    with open(students_json, 'w', encoding='utf-8') as f:
        json.dump(all_students, f, indent=4, ensure_ascii=False)
    
    print(f"Saved to {students_json}")
    
    # Parse and save mentors
    mentors = parse_mentors()
    with open(mentors_json, 'w', encoding='utf-8') as f:
        json.dump(mentors, f, indent=4, ensure_ascii=False)
    
    print(f"Saved mentors to {mentors_json}")

if __name__ == "__main__":
    main()
