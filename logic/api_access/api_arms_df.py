#CONEXIÓN A SERVICIO DE API ARMS
import requests
import pandas as pd
from gui.components import solicitar_credenciales_api

URL_ARMS = "http://armsqastag2/abms/api/"

ENDPOINT_ACCOUNT = "accounts"
ENDPOINT_BILLING_LEDGER = "billing-ledgers"
ENDPOINT_FLIGHT_MOVEMENT = "flightmovements"




def get_dataframe(url, columns, headers):
    print(f"🔸 Consultando {url}")
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list) and data:
            df = pd.json_normalize(data)
            columns_available = [col for col in columns if col in df.columns]
    
            df = df[columns_available]
            return df
            
    except Exception as e:
        print(f"Error al obtener datos de ARMS: {e}")