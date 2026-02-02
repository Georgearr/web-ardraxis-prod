from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads/valentine'

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "valentine-sheet.json", scope
)
client = gspread.authorize(creds)
sheet = client.open("Valentine_Order").sheet1

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ===============================
# ROUTES HTML
# ===============================
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

@app.route("/coming_soon")
def coming_soon():
    return render_template("coming_soon.html")

@app.errorhandler(404)
def handle_404(error):
    return render_template("404.html"), 404

@app.route("/meloria")
def meloria():
    return render_template("e_meloria.html")

@app.route("/festiora")
def festiora():
    return render_template("e_festiora.html")

@app.route("/cupids-corner", methods=["GET", "POST"])
def cupids_corner():
    if request.method == "POST":
        data = request.get_json()

        # Ambil data
        product = data.get("product")
        color = data.get("forever_flowers_color")
        addon = data.get("add_thought_card")
        notes = data.get("notes")
        name = data.get("recipient_name")
        kelas = data.get("recipient_class")

        # Timestamp & Order ID
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_id = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{random.randint(100,999)}"

        # Harga
        product_prices = {"flowers": 15000, "bundle": 20000, "chocobloom": 18000}
        addon_prices = {"yes": 2000, "no": 0}

        product_price = product_prices.get(product, 0)
        addon_price = addon_prices.get(addon, 0)
        total_price = product_price + addon_price

        # Append ke Sheet
        sheet.append_row([
            waktu, order_id, product, color, addon, notes, name, kelas,
            product_price, addon_price, total_price
        ])

        return jsonify({"status": "success"})

    return render_template("valentine_order.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
