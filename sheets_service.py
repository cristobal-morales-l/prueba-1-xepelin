# sheets_service.py
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# === Configuración global ===
GSHEET_ID = os.getenv("GSHEET_ID")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "service_account.json")

# Si Railway pasa las credenciales por variable de entorno (texto JSON)
if os.getenv("GOOGLE_SHEETS_CREDENTIALS"):
    creds_content = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    with open("service_account.json", "w") as f:
        json.dump(json.loads(creds_content), f)


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
    Devuelve todas las filas del Sheet como una lista de diccionarios:
    [{idOp: 100, tasa: 1.5, email: 'correo@...'}, ...]
    """
    try:
        client = get_client()
        sheet = client.open_by_key(GSHEET_ID).sheet1
        registros = sheet.get_all_records()

        # Asegurar conversión de tipos
        data = []
        for r in registros:
            data.append({
                "idOp": int(r.get("idOp", 0)),
                "tasa": float(r.get("tasa", 0)),
                "email": str(r.get("email", "")).strip()
            })
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
        sheet = client.open_by_key(GSHEET_ID).sheet1
        data = sheet.get_all_records()

        for i, row in enumerate(data, start=2):  # fila 2 porque fila 1 = encabezados
            if int(row["idOp"]) == int(idOp):
                sheet.update_cell(i, 2, nueva_tasa)  # Columna 2 = "tasa"
                print(f"✅ Tasa actualizada para idOp {idOp}")
                return True

        print(f"⚠️ idOp {idOp} no encontrado en el Sheet.")
        return False

    except Exception as e:
        print(f"❌ Error al actualizar Google Sheet: {e}")
        return False
