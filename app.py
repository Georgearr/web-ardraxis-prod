from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
@app.route("/Home")
def home():
   return render_template("index.html")

@app.route("/Events")
def events():
   return render_template("events.html")

@app.route("/About_Us")
def about_us():
   return render_template("about_us.html")

if __name__ == "__main__":
    app.run()