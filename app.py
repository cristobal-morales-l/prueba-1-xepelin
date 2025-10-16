# app.py
import logging
import os
from flask import Flask, request, jsonify, send_from_directory
from sheets_service import update_tasa
from zapier_service import notificar_zapier

# === Configuración del logger ===
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
logger = logging.getLogger(__name__)

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
        logger.info(f"📩 Request recibido: {data}")

        if not data:
            logger.warning("❌ Request vacío o sin JSON válido")
            return jsonify({"error": "sin datos"}), 400

        idOp = data.get("idOp")
        tasa = data.get("tasa")
        email = data.get("email")

        if not all([idOp, tasa, email]):
            logger.warning(f"⚠️ Faltan parámetros: idOp={idOp}, tasa={tasa}, email={email}")
            return jsonify({"error": "faltan parámetros"}), 400

        # 1️⃣ Notificar Zapier
        zapier_ok = notificar_zapier(data)
        logger.info(f"📨 Resultado Zapier: {zapier_ok}")

        # 2️⃣ Actualizar Google Sheet
        sheet_ok = update_tasa(idOp, tasa)
        logger.info(f"📊 Resultado Google Sheet: {sheet_ok}")

        if zapier_ok and sheet_ok:
            logger.info(f"✅ idOp {idOp} actualizado correctamente")
            return jsonify({"ok": True, "msg": "Tasa actualizada y correo enviado"}), 200
        else:
            logger.error(f"❌ Error parcial: Zapier={zapier_ok}, Sheet={sheet_ok}")
            return jsonify({
                "ok": False,
                "zapier_ok": zapier_ok,
                "sheet_ok": sheet_ok,
                "msg": "Alguna de las acciones falló"
            }), 500

    except Exception as e:
        logger.exception(f"💥 Error interno al procesar /api/guardar: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Iniciando servidor Flask en puerto {port}")
    app.run(host="0.0.0.0", port=port)
