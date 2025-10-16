# app.py
from flask import Flask, request, jsonify, send_from_directory
from sheets_service import update_tasa
from zapier_service import notificar_zapier
import os

app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/dashboard")
def dashboard():
    return send_from_directory("static", "dashboard.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

@app.route("/api/guardar", methods=["POST"])
def guardar_tasa():
    """
    Endpoint que recibe la tasa modificada, la actualiza en Google Sheets
    y notifica vía Zapier.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "sin datos"}), 400

        idOp = data.get("idOp")
        tasa = data.get("tasa")
        email = data.get("email")

        if not all([idOp, tasa, email]):
            return jsonify({"error": "faltan parámetros"}), 400

        zapier_ok = notificar_zapier(data)
        sheet_ok = update_tasa(idOp, tasa)

        if zapier_ok and sheet_ok:
            return jsonify({"ok": True, "msg": "Tasa actualizada y correo enviado"}), 200
        else:
            return jsonify({
                "ok": False,
                "zapier_ok": zapier_ok,
                "sheet_ok": sheet_ok,
                "msg": "Alguna de las acciones falló"
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
