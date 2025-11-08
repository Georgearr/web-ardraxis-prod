from flask import Flask, render_template
app = Flask(__name__)

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

@app.route("/meloria/bahasa_mandarin")
def bahasa_mandarin():
    return render_template("meloria/bahasa_mandarin.html")

@app.route("/meloria/bahasa_jepang")
def bahasa_jepang():
    return render_template("meloria/bahasa_jepang.html")

@app.route("/meloria/bahasa_jerman")
def bahasa_jerman():
    return render_template("meloria/bahasa_jerman.html")

@app.route("/meloria/bahasa_prancis")
def bahasa_prancis():
    return render_template("meloria/bahasa_prancis.html")

@app.route("/meloria/bahasa_korea")
def bahasa_korea():
    return render_template("meloria/bahasa_korea.html")

@app.route("/meloria/bahasa_arab")
def bahasa_arab():
    return render_template("meloria/bahasa_arab.html")

@app.route("/meloria/web_cloning")
def web_cloning():
    return render_template("meloria/web_cloning.html")

@app.route("/meloria/membaca_puisi")
def membaca_puisi():
    return render_template("meloria/membaca_puisi.html")

@app.route("/meloria/menghias_totebag")
def menghias_totebag():
    return render_template("meloria/menghias_totebag.html")

@app.route("/meloria/debat_bahasa_indonesia")
def debat_bahasa_indonesia():
    return render_template("meloria/debat_bahasa_indonesia.html")

@app.route("/meloria/debat_bahasa_inggris")
def debat_bahasa_inggris():
    return render_template("meloria/debat_bahasa_inggris.html")

@app.route("/meloria/competitive_programming")
def competitive_programming():
    return render_template("meloria/competitive_programming.html")

@app.route("/meloria/desain_infografis")
def desain_infografis():
    return render_template("meloria/desain_infografis.html")

@app.route("/meloria/cosplay")
def cosplay():
    return render_template("meloria/cosplay.html")

@app.route("/meloria/cerdas_cermat")
def cerdas_cermat():
    return render_template("meloria/cerdas_cermat.html")

@app.route("/meloria/igs_got_talent")
def igs_got_talent():
    return render_template("meloria/igs_got_talent.html")

@app.route("/meloria/boardgames")
def boardgames():
    return render_template("meloria/boardgames.html")

@app.route("/meloria/noraebang")
def noraebang():
    return render_template("meloria/noraebang.html")

@app.route("/meloria/wordchain")
def wordchain():
    return render_template("meloria/wordchain.html")

@app.route("/meloria/mystery_color")
def mystery_color():
    return render_template("meloria/mystery_color.html")

@app.route("/meloria/workshop_daur_ulang")
def workshop_daur_ulang():
    return render_template("meloria/workshop_daur_ulang.html")

@app.route("/meloria/workshop_calligraphy")
def workshop_calligraphy():
    return render_template("meloria/workshop_calligraphy.html")


# Workshop Calligraphy not added yet due to poster issues

if __name__ == "__main__":
    app.run()