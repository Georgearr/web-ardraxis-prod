from flask import Flask, render_template, request, redirect, jsonify
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

@app.route("/meloria")
def meloria():
    return render_template("e_meloria.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
