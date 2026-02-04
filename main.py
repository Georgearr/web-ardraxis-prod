from flask import Flask, render_template, request, jsonify
import os
import random
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# ===============================
# CONFIG
# ===============================
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload
app.config['UPLOAD_FOLDER'] = 'static/uploads/valentine'
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "pdf"}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ===============================
# GOOGLE SHEETS
# ===============================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "valentine-sheet.json", scope
)
client = gspread.authorize(creds)
sheet = client.open("Valentine_Order").sheet1

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

@app.route("/meloria")
def meloria():
    return render_template("e_meloria.html")

@app.route("/festiora")
def festiora():
    return render_template("e_festiora.html")

@app.errorhandler(404)
def handle_404(error):
    return render_template("404.html"), 404

# ===============================
# CUPID'S CORNER
# ===============================
@app.route("/cupids-corner", methods=["GET", "POST"])
def cupids_corner():
    if request.method == "POST":
        try:
            # ===== AMBIL DATA FORM =====
            product = request.form.get("product")
            quantity_map = {
                "Flowers": request.form.get("qty_flowers", 1),
                "Bundle": request.form.get("qty_bundle", 1),
                "Chocobloom": request.form.get("qty_chocobloom", 1),
            }
            quantity = int(quantity_map.get(product, 1))

            # Only ask color for Flowers
            color = request.form.get("forever_flowers_color") if product == "Flowers" else ""

            # Addon checkbox
            addon = request.form.get("add_thought_card")
            addon = "yes" if addon == "yes" else "no"
            notes = request.form.get("notes", "")
            name = request.form.get("recipient_name")
            kelas = request.form.get("recipient_class")
            file = request.files.get("payment_proof")

            # ===== VALIDASI =====
            if not product or not name or not kelas or not file:
                raise ValueError("Data belum lengkap")
            if quantity < 1 or quantity > 20:
                raise ValueError("Jumlah tidak valid (1-20)")
            if product == "Flowers" and not color:
                raise ValueError("Warna untuk Flowers harus dipilih")
            if not allowed_file(file.filename):
                raise ValueError("Format file tidak didukung")

            # ===== HITUNG HARGA =====
            product_prices = {"Flowers": 15000, "Bundle": 20000, "Chocobloom": 18000}
            addon_prices = {"yes": 2000, "no": 0}

            total_price = product_prices.get(product, 0) * quantity + addon_prices[addon]

            # ===== SIMPAN FILE =====
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = os.path.splitext(file.filename)[1]
            safe_filename = f"{timestamp}_{random.randint(100,999)}{ext}"

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            file.save(filepath)

            # ===== SIMPAN KE SHEETS =====
            base_url = "https://osissmaigs.com"
            file_url = f"{base_url}/static/uploads/valentine/{safe_filename}"
            link_bukti = f'=HYPERLINK("{file_url}"; "Lihat Bukti")'

            sheet.append_row(
                [
                    waktu,
                    product,
                    quantity,
                    color,
                    "Yes" if addon == "yes" else "No",
                    name,
                    kelas,
                    notes,
                    link_bukti,
                    total_price
                ],
                value_input_option="USER_ENTERED"
)



            # ===== RESPONSE SUCCESS =====# RESPONSE SUCCESS
            return jsonify({"status": "success", "total_price": total_price}), 200

        except ValueError as ve:
            # Validasi error → TIDAK masuk ke sheet
            return jsonify({"status": "error", "message": str(ve)}), 400
        except Exception as e:
            # Error server lainnya → TIDAK masuk ke sheet
            return jsonify({"status": "error", "message": f"Terjadi kesalahan: {str(e)}"}), 500

    return render_template("valentine_order.html")

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
