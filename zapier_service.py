# zapier_service.py
import requests

ZAPIER_URL = "https://hooks.zapier.com/hooks/catch/13232884/oahrt5g/"

def notificar_zapier(data):
    """
    Envía un POST a Zapier con los datos de la tasa modificada.
    Retorna True si el request fue exitoso.
    """
    try:
        res = requests.post(ZAPIER_URL, json=data)
        if res.status_code == 200:
            print(f"📨 Notificación enviada a Zapier (idOp={data.get('idOp')})")
            return True
        print(f"⚠️ Error enviando a Zapier: {res.status_code}")
        return False
    except Exception as e:
        print(f"❌ Error en notificación Zapier: {e}")
        return False
