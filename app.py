# app.py
import sys
import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from sheets_service import update_tasa, leer_tasas
from zapier_service import notificar_zapier

# === Configuración de logs visibles en Railway ===
sys.stdout.reconfigure(line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)
logger.info("🚀 Flask inicializado en Railway")

# === Variables de entorno ===
gsheet_id = os.getenv("GSHEET_ID")
creds = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
logger.info(f"GSHEET_ID: {gsheet_id if gsheet_id else '❌ No definido'}")
logger.info(f"GOOGLE_SHEETS_CREDENTIALS presente: {'✅ Sí' if creds else '❌ No'}")

# === Flask App ===
app = Flask(__name__, static_folder="static")
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/dashboard")
def dashboard():
    return send_from_directory("static", "dashboard.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

# === API para actualizar tasas ===
@app.route("/api/guardar", methods=["POST"])
def guardar_tasa():
    try:
        data = request.get_json(force=True, silent=True)
        logger.info(f"📩 POST /api/guardar recibido → {data}")

        if not data:
            return jsonify({"error": "sin datos"}), 400

        idOp = data.get("idOp")
        tasa = data.get("tasa")
        email = data.get("email")

        if not all([idOp, tasa, email]):
            logger.warning(f"⚠️ Parámetros incompletos: idOp={idOp}, tasa={tasa}, email={email}")
            return jsonify({"error": "faltan parámetros"}), 400

        zapier_ok = notificar_zapier(data)
        sheet_ok = update_tasa(idOp, tasa)

        logger.info(f"Zapier: {zapier_ok} | Sheet: {sheet_ok}")

        if zapier_ok and sheet_ok:
            return jsonify({"ok": True, "msg": "✅ Tasa actualizada"}), 200
        else:
            return jsonify({
                "ok": False,
                "zapier_ok": zapier_ok,
                "sheet_ok": sheet_ok
            }), 500

    except Exception as e:
        logger.exception(f"💥 Error en /api/guardar: {e}")
        return jsonify({"error": str(e)}), 500

# === Nuevo endpoint para leer datos privados ===
@app.route("/api/data", methods=["GET"])
def get_data():
    try:
        data = leer_tasas()
        return jsonify(data), 200
    except Exception as e:
        logger.exception(f"💥 Error en /api/data: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🏃 Ejecutando Flask en puerto {port}")
    app.run(host="0.0.0.0", port=port)
