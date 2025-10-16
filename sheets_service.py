# sheets_service.py
import os
import json
import gspread
from google.oauth2.service_account import Credentials

GSHEET_ID = os.getenv("GSHEET_ID")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "service_account.json")

# Si Railway pasa las credenciales por variable de entorno
if os.getenv("GOOGLE_SHEETS_CREDENTIALS"):
    creds_content = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    with open("service_account.json", "w") as f:
        json.dump(json.loads(creds_content), f)


def get_client():
    """Devuelve un cliente autenticado de gspread."""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)
    client = gspread.authorize(creds)
    return client


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
                sheet.update_cell(i, 2, nueva_tasa)  # columna 2 = tasa
                print(f"✅ Tasa actualizada para idOp {idOp}")
                return True
        print(f"⚠️ idOp {idOp} no encontrado en el sheet.")
        return False
    except Exception as e:
        print(f"❌ Error al actualizar Google Sheet: {e}")
        return False
