# app.py
import sys
import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from sheets_service import update_tasa
from zapier_service import notificar_zapier

# === Forzar logs en tiempo real (Railway muestra stdout/stderr) ===
sys.stdout.reconfigure(line_buffering=True)
os.environ["PYTHONUNBUFFERED"] = "1"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("🚀 Iniciando aplicación Flask en Railway...")

# === Comprobación de variables de entorno ===
gsheet_id = os.getenv("GSHEET_ID")
creds = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
logger.info(f"GSHEET_ID detectado: {gsheet_id if gsheet_id else '❌ No definido'}")
logger.info(f"GOOGLE_SHEETS_CREDENTIALS presente: {'✅ Sí' if creds else '❌ No'}")

# === Inicialización de Flask ===
app = Flask(__name__, static_folder="static")


# -------------------------------
# Rutas Frontend
# -------------------------------
@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/dashboard")
def dashboard():
    return send_from_directory("static", "dashboard.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)


# -------------------------------
# API principal
# -------------------------------
@app.route("/api/guardar", methods=["POST"])
def guardar_tasa():
    """
    Endpoint que recibe la tasa modificada, la actualiza en Google Sheets
    y notifica vía Zapier.
    """
    try:
        data = request.get_json(force=True, silent=True)
        logger.info(f"📩 Request recibido en /api/guardar: {data}")

        if not data:
            logger.error("❌ No se recibió JSON válido en el request")
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

        # 3️⃣ Respuesta final
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


# -------------------------------
# Lanzar servidor Flask
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Servidor Flask iniciado en puerto {port}")
    app.run(host="0.0.0.0", port=port)
