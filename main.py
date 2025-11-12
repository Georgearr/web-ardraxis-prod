from flask import Flask, render_template, request, redirect
import openpyxl
import os

app = Flask(__name__)

# General Pages
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/coming_soon")
def coming_soon():
    return render_template("coming_soon.html")

@app.errorhandler(404)
def handle_404(error):
    return render_template("404.html"), 404

# Meloria Event Pages
@app.route("/meloria")
def meloria():
    return render_template("e_meloria.html")

if __name__ == "__main__":
    app.run()









# MELORIA EVENT PAGES

# Pastikan folder data ada
# if not os.path.exists("data"):
#     os.makedirs("data")

# def simpan_ke_excel(nama_file, data):
#     path = f"data/{nama_file}.xlsx"

#     # Jika file belum ada, buat header
#     if not os.path.exists(path):
#         wb = openpyxl.Workbook()
#         ws = wb.active
#         ws.append(list(data.keys()))  # header column
#         wb.save(path)

#     # Tambahkan baris data baru
#     wb = openpyxl.load_workbook(path)
#     ws = wb.active
#     ws.append(list(data.values()))
#     wb.save(path)

# @app.route("/meloria/bahasa_mandarin", methods=["GET", "POST"])
# def bahasa_mandarin():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("bahasa_mandarin", data)

#     return render_template("meloria/bahasa_mandarin.html")


# @app.route("/meloria/bahasa_prancis", methods=["GET", "POST"])
# def bahasa_prancis():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("bahasa_prancis", data)

#     return render_template("meloria/bahasa_prancis.html")

# @app.route("/meloria/bahasa_jerman", methods=["GET", "POST"])
# def bahasa_jerman():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("bahasa_jerman", data)

#     return render_template("meloria/bahasa_jerman.html")


# @app.route("/meloria/bahasa_jepang", methods=["GET", "POST"])
# def bahasa_jepang():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("bahasa_jepang", data)

#     return render_template("meloria/bahasa_jepang.html")



# @app.route("/meloria/bahasa_korea", methods=["GET", "POST"])
# def bahasa_korea():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("bahasa_korea", data)

#     return render_template("meloria/bahasa_korea.html")


# @app.route("/meloria/bahasa_arab", methods=["GET", "POST"])
# def bahasa_arab():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("bahasa_arab", data)

#     return render_template("meloria/bahasa_arab.html")


# @app.route("/meloria/web_cloning", methods=["GET", "POST"])
# def web_cloning():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("web_cloning", data)

#     return render_template("meloria/web_cloning.html")

# @app.route("/meloria/membaca_puisi", methods=["GET", "POST"])
# def membaca_puisi():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("membaca_puisi", data)

#     return render_template("meloria/membaca_puisi.html")


# @app.route("/meloria/menghias_totebag", methods=["GET", "POST"])
# def menghias_totebag():
#     if request.method == "POST":
#         data = {
#             "Nama Tim": request.form["nama_tim"],
#             "Nama1": request.form["nama1"],
#             "Kelas1": request.form["kelas1"],
#             "ID Line1": request.form["idline1"],
#             "Nama2": request.form["nama2"],
#             "Kelas2": request.form["kelas2"],
#             "ID Line2": request.form["idline2"]
#         }
#         simpan_ke_excel("menghias_totebag", data)

#     return render_template("meloria/menghias_totebag.html")


# @app.route("/meloria/debat_bahasa_indonesia", methods=["GET", "POST"])
# def debat_bahasa_indonesia():
#     if request.method == "POST":
#         data = {
#             "Nama1": request.form["nama1"],
#             "Kelas1": request.form["kelas1"],
#             "ID Line1": request.form["idline1"],
#             "Nama2": request.form["nama2"],
#             "Kelas2": request.form["kelas2"],
#             "ID Line2": request.form["idline2"],
#             "Nama3": request.form["nama3"],
#             "Kelas3": request.form["kelas3"],
#             "ID Line3": request.form["idline3"]
#         }
#         simpan_ke_excel("debat_bahasa_indonesia", data)

#     return render_template("meloria/debat_bahasa_indonesia.html")


# @app.route("/meloria/debat_bahasa_inggris", methods=["GET", "POST"])
# def debat_bahasa_inggris():
#     if request.method == "POST":
#         data = {
#             "Nama1": request.form["nama1"],
#             "Kelas1": request.form["kelas1"],
#             "ID Line1": request.form["idline1"],
#             "Nama2": request.form["nama2"],
#             "Kelas2": request.form["kelas2"],
#             "ID Line2": request.form["idline2"],
#             "Nama3": request.form["nama3"],
#             "Kelas3": request.form["kelas3"],
#             "ID Line3": request.form["idline3"]
#         }
#         simpan_ke_excel("debat_bahasa_inggris", data)

#     return render_template("meloria/debat_bahasa_inggris.html")


# @app.route("/meloria/competitive_programming", methods=["GET", "POST"])
# def competitive_programming():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("competitive_programming", data)

#     return render_template("meloria/competitive_programming.html")


# @app.route("/meloria/desain_infografis", methods=["GET", "POST"])
# def desain_infografis():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("desain_infografis", data)

#     return render_template("meloria/desain_infografis.html")


# @app.route("/meloria/cosplay", methods=["GET", "POST"])
# def cosplay():
#     if request.method == "POST":
#         data = {
#             "Nama1": request.form["nama1"],
#             "Kelas1": request.form["kelas1"],
#             "Karakter1": request.form["karakter1"],
#             "ID Line1": request.form["idline1"],
#             "Nama2": request.form["nama2"],
#             "Kelas2": request.form["kelas2"],
#             "Karakter2": request.form["karakter2"],
#             "ID Line2": request.form["idline2"],
#             "Nama3": request.form["nama3"],
#             "Kelas3": request.form["kelas3"],
#             "Karakter3": request.form["karakter3"],
#             "ID Line3": request.form["idline3"],
#             "Nama4": request.form["nama4"],
#             "Kelas4": request.form["kelas4"],
#             "Karakter4": request.form["karakter4"],
#             "ID Line4": request.form["idline4"]
#         }
#         simpan_ke_excel("cosplay", data)

#     return render_template("meloria/cosplay.html")

# @app.route("/meloria/cerdas_cermat", methods=["GET", "POST"])
# def cerdas_cermat():
#     if request.method == "POST":
#         data = {
#             "Nama Kapten": request.form["nama1"],
#             "ID Line": request.form["idline1"],
#             "Nama Anggota 1": request.form["nama2"],
#             "ID Line 1": request.form["idline2"],
#             "Nama Anggota 2": request.form["nama3"],
#             "ID Line 2": request.form["idline3"],
#             "Kelas": request.form["kelas"]
#         }
#         simpan_ke_excel("cerdas_cermat", data)

#     return render_template("meloria/cerdas_cermat.html")

# @app.route("/meloria/igs_got_talent", methods=["GET", "POST"])
# def igs_got_talent():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"],
#             "Jenis Talent": request.form["jenis_talent"],
#             "Nama Anggota": request.form["nama_anggota"]
#         }
#         simpan_ke_excel("igs_got_talent", data)

#     return render_template("meloria/igs_got_talent.html")

# @app.route("/meloria/workshop_daur_ulang", methods=["GET", "POST"])
# def workshop_daur_ulang():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"]
#         }
#         simpan_ke_excel("workshop_daur_ulang", data)

#     return render_template("meloria/workshop_daur_ulang.html")

# @app.route("/meloria/workshop_calligraphy", methods=["GET", "POST"])
# def workshop_calligraphy():
#     if request.method == "POST":
#         data = {
#             "Nama": request.form["nama"],
#             "Kelas": request.form["kelas"],
#             "ID Line": request.form["idline"],
#             "Sesi": request.form["sesi"]
#         }
#         simpan_ke_excel("workshop_calligraphy", data)

#     return render_template("meloria/workshop_calligraphy.html")


# @app.route("/meloria/boardgames")
# def boardgames():
#     return render_template("meloria/boardgames.html")

# @app.route("/meloria/noraebang")
# def noraebang():
#     return render_template("meloria/noraebang.html")

# @app.route("/meloria/wordchain")
# def wordchain():
#     return render_template("meloria/wordchain.html")

# @app.route("/meloria/mystery_color")
# def mystery_color():
#     return render_template("meloria/mystery_color.html")