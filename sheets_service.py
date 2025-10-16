# sheets_service.py
import os
import json
import time
import gspread
from google.oauth2.service_account import Credentials

# === Configuración global ===
GSHEET_ID = os.getenv("GSHEET_ID")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "service_account.json")
SHEET_NAME = os.getenv("SHEET_NAME", "Sheet1")  


# Si Railway pasa las credenciales como JSON embebido en variable de entorno
if os.getenv("GOOGLE_SHEETS_CREDENTIALS"):
    try:
        creds_content = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        with open("service_account.json", "w") as f:
            json.dump(json.loads(creds_content), f)
        print("✅ Archivo de credenciales generado correctamente.")
    except Exception as e:
        print(f"⚠️ Error al escribir credenciales: {e}")


# -------------------------------
# Autenticación con Google Sheets
# -------------------------------
def get_client():
    """Devuelve un cliente autenticado de gspread."""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)
    client = gspread.authorize(creds)
    return client


# -------------------------------
# Leer datos actuales del Sheet
# -------------------------------
def leer_tasas():
    """
    Devuelve todas las filas del Sheet como lista de diccionarios:
    [{idOp: 100, tasa: 1.5, email: 'correo@...'}, ...]
    """
    try:
        client = get_client()
        sheet = client.open_by_key(GSHEET_ID).worksheet(SHEET_NAME)
        registros = sheet.get_all_records()

        print(f"📄 Leyendo hoja '{SHEET_NAME}' ({len(registros)} filas obtenidas)")

        data = []
        for r in registros:
            # Soporte para distintas capitalizaciones
            id_op = r.get("idOp") or r.get("IDOP") or r.get("IdOp") or 0
            tasa = r.get("tasa") or r.get("Tasa") or r.get("TASA") or 0
            email = r.get("email") or r.get("Email") or r.get("EMAIL") or ""

            try:
                id_op = int(id_op)
                tasa = float(tasa)
                email = str(email).strip()
                data.append({"idOp": id_op, "tasa": tasa, "email": email})
            except Exception as conv_err:
                print(f"⚠️ Error procesando fila {r}: {conv_err}")

        print(f"✅ Datos cargados correctamente: {len(data)} filas")
        return data

    except Exception as e:
        print(f"❌ Error al leer Google Sheet: {e}")
        return []



# -------------------------------
# Actualizar una tasa específica
# -------------------------------
def update_tasa(idOp, nueva_tasa):
    """
    Busca el idOp en el Google Sheet y actualiza su tasa.
    Retorna True si se actualiza correctamente, False en caso contrario.
    """
    try:
        client = get_client()
        sheet = client.open_by_key(GSHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_records()

        fila_actualizada = None
        for i, row in enumerate(data, start=2):  # fila 2 = primera fila de datos
            if str(row.get("idOp")).strip() == str(idOp):
                sheet.update_cell(i, 2, nueva_tasa)  # Columna 2 = "tasa"
                fila_actualizada = i
                print(f"✅ Tasa actualizada para idOp {idOp} (fila {i})")
                break

        if not fila_actualizada:
            print(f"⚠️ idOp {idOp} no encontrado en el Sheet.")
            return False

        # 🕐 esperar a que se propague antes de siguiente lectura
        time.sleep(1.5)
        return True

    except Exception as e:
        print(f"❌ Error al actualizar Google Sheet: {e}")
        return False
