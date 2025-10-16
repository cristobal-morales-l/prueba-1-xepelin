import os
import json
import gspread
from google.oauth2.service_account import Credentials

GSHEET_ID = os.getenv("GSHEET_ID")
CREDENTIALS_PATH = os.getenv("CREDENTIALS_PATH", "service_account.json")
SHEET_NAME = os.getenv("SHEET_NAME", "Sheet1")

# Si Railway pasa las credenciales por variable de entorno
if os.getenv("GOOGLE_SHEETS_CREDENTIALS"):
    creds_content = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    with open("service_account.json", "w") as f:
        json.dump(json.loads(creds_content), f)


def get_client():
    """Devuelve un cliente autenticado de gspread."""
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)
    return gspread.authorize(creds)


def leer_tasas():
    """Lee los datos del sheet con credenciales y devuelve lista de diccionarios."""
    try:
        client = get_client()
        sheet = client.open_by_key(GSHEET_ID).worksheet(SHEET_NAME)
        valores = sheet.get_all_values()

        if not valores or len(valores) < 2:
            print("⚠️ No hay datos suficientes en el Sheet.")
            return []

        encabezados = [h.strip() for h in valores[0]]
        filas = valores[1:]

        data = []
        for fila in filas:
            if not any(fila):
                continue
            fila_dict = dict(zip(encabezados, fila))
            id_op = int(fila_dict.get("idOp", "0") or 0)
            tasa = float(fila_dict.get("Tasa", fila_dict.get("tasa", "0")) or 0)
            email = fila_dict.get("Email", fila_dict.get("email", "")).strip()
            data.append({"idOp": id_op, "tasa": tasa, "email": email})

        print(f"✅ {len(data)} filas leídas desde Google Sheet.")
        return data

    except Exception as e:
        print(f"❌ Error al leer Google Sheet: {e}")
        return []


def update_tasa(idOp, nueva_tasa):
    """Busca el idOp en el Google Sheet y actualiza su tasa."""
    try:
        client = get_client()
        sheet = client.open_by_key(GSHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_records()

        for i, row in enumerate(data, start=2):
            if str(row.get("idOp")) == str(idOp):
                sheet.update_cell(i, 2, nueva_tasa)
                print(f"✅ Tasa actualizada para idOp {idOp}")
                return True

        print(f"⚠️ idOp {idOp} no encontrado en el Sheet.")
        return False

    except Exception as e:
        print(f"❌ Error al actualizar Google Sheet: {e}")
        return False
