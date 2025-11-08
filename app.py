<<<<<<< Updated upstream
=======
from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
   return render_template("index.html")

<<<<<<< Updated upstream
@app.route("/events")
def events():
   return render_template("events.html")

if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> Stashed changes
=======
@app.route("/coming_soon")
def coming_soon():
    return render_template("coming_soon.html")

@app.route("/meloria")
def e_meloria():
    return render_template("e_meloria.html")

@app.errorhandler(404)
def handle_404(error):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
>>>>>>> Stashed changes
