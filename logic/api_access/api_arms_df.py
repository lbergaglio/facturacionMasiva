import requests
import pandas as pd
import getpass
#from gui.components import solicitar_credenciales_api


# Mostrar todo el contenido de las celdas de texto
pd.set_option("display.max_colwidth", None)

# Mostrar todas las columnas del DataFrame sin truncado horizontal
pd.set_option("display.max_columns", None)

# Evitar que corte el ancho de la tabla
pd.set_option("display.width", 0)

# === URLs y endpoints base ===
BASE_URL = "http://armsqastag2"
TOKEN_URL = f"{BASE_URL}/abms/oauth/token"
API_BASE = f"{BASE_URL}/abms/api/"

ENDPOINT_ACCOUNT = "accounts"
ENDPOINT_BILLING_LEDGER = "billing-ledgers"
ENDPOINT_FLIGHTMOVEMENT = "flightmovements"

COLUMNS_ACCOUNT = ["id","name", "alias", "active", "account_type.id"]
COLUMNS_BILLING_LEDGER = ["invoice_period_or_date","account.name", "invoice_type","flightmovement_category.name" ,"invoice_number","invoice_currency.currency_code" ,"invoice_amount", "invoice_state_type","billing_center.name","id"]
COLUMNS_FLIGHTMOVEMENTS = ["invoice_id", "enroute_charges", "approach_charges", "extended_hours_surcharge"]

# === Credenciales OAuth2 (completá los que falten) ===
CLIENT_ID = "abms_external_client"
CLIENT_SECRET = ""

def get_token_oauth2():
    username = input|("🔑 Ingrese su nombre de usuario: ")
    password = getpass.getpass("🔑 Ingrese su contraseña: ")
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(TOKEN_URL, data=payload, headers=headers)
        response.raise_for_status()
        token = response.json()["access_token"]
        print("✅ Token OAuth2 obtenido correctamente.")
        return token
    except Exception as e:
        print(f"❌ Error al obtener token OAuth2: {e}")

def get_dataframe_paginado(base_url, columns, headers):
    page = 0
    size = 100  # o lo que permita el backend
    all_data = []

    while True:
        sep = "&" if "?" in base_url else "?"
        url = f"{base_url}{sep}page={page}&size={size}"

        print(f"🔸 Consultando {url}")
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            if "content" in data and isinstance(data["content"], list):
                all_data.extend(data["content"])
                if data.get("last", True):  # si es la última página, cortar
                    break
                page += 1
            elif isinstance(data, list):
                all_data.extend(data)
                break
            else:
                print("⚠️ No se encontró 'content' o no es una lista.")
                break
        except Exception as e:
            print(f"❌ Error en página {page}: {e}")
            break

    if all_data:
        df = pd.json_normalize(all_data)
        return df[[col for col in columns if col in df.columns]]
    else:
        return pd.DataFrame(columns=columns)

# === Ejecución principal ===
token = get_token_oauth2()
if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    start_date = "2025-01-01"
    end_date = "2025-01-31"
    invoice_id = 49085


    url_billing_ledgers=f"{API_BASE}billing-ledgers?startDate={start_date}&endDate={end_date}"
    url_flightmovements = f"{API_BASE}flightmovements/list/invoices/{invoice_id}"

    #df_billing_ledgers = get_dataframe_paginado(url_billing_ledgers,COLUMNS_BILLING_LEDGER, headers)
    #df_accounts = get_dataframe_paginado(API_BASE + ENDPOINT_ACCOUNT, COLUMNS_ACCOUNT, headers)
    df_flightmovements = get_dataframe_paginado(url_flightmovements, COLUMNS_FLIGHTMOVEMENTS, headers)
    #print(df_accounts)
    #print(df_billing_ledgers)
    print(df_flightmovements)
    #df_accounts.to_excel("accounts.xlsx", index=False)
    #df_billing_ledgers.to_excel("billing_ledgers.xlsx", index=False)
    df_flightmovements.to_excel("flightmovements.xlsx", index=False)
