import requests
import pandas as pd
import getpass
from tqdm import tqdm

# === Configuración de Pandas ===
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 0)

# === URLs y endpoints base ===
BASE_URL = "http://armsqastag2"
TOKEN_URL = f"{BASE_URL}/abms/oauth/token"
API_BASE = f"{BASE_URL}/abms/api/"

ENDPOINT_ACCOUNT = "accounts"
ENDPOINT_BILLING_LEDGER = "billing-ledgers"
ENDPOINT_FLIGHTMOVEMENT = "flightmovements"

COLUMNS_ACCOUNT = ["id", "name", "alias", "active", "account_type.id"]
COLUMNS_BILLING_LEDGER = [
    "invoice_period_or_date", "account.name", "invoice_type", "flightmovement_category.name",
    "invoice_number", "invoice_currency.currency_code", "invoice_amount",
    "invoice_state_type", "billing_center.name", "id"
]
COLUMNS_FLIGHTMOVEMENTS = ["invoice_id", "enroute_charges", "approach_charges", "extended_hours_surcharge"]

CLIENT_ID = "abms_external_client"
CLIENT_SECRET = ""  # <--- Completá esto si aplica

# === Función para autenticación OAuth2 ===
def get_token_oauth2():
    username = input("🔑 Ingrese su nombre de usuario: ")
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

# === Función para obtener DataFrame paginado ===
def get_dataframe_paginado(base_url, columns, headers):
    page = 0
    size = 100
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
                if data.get("last", True):
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

# === Pipeline principal ===
def construir_df_final(start_date, end_date, headers):
    print("🔹 Paso 1: Extrayendo billing-ledgers...")
    df_billing = get_dataframe_paginado(
        f"{API_BASE}{ENDPOINT_BILLING_LEDGER}?startDate={start_date}&endDate={end_date}",
        COLUMNS_BILLING_LEDGER,
        headers
    )

    print("🔹 Paso 2: Extrayendo accounts...")
    df_accounts = get_dataframe_paginado(API_BASE + ENDPOINT_ACCOUNT, COLUMNS_ACCOUNT, headers)
    df_billing = df_billing.merge(df_accounts[["name", "alias"]], how="left", left_on="account.name", right_on="name")

    resultados = []
    print("🔹 Paso 3: Extrayendo flightmovements por invoice_id...")

    for invoice_id in tqdm(df_billing["id"].dropna().unique(), desc="Procesando invoices"):
        url_fm = f"{API_BASE}flightmovements/list/invoices/{invoice_id}"
        df_fm = get_dataframe_paginado(url_fm, COLUMNS_FLIGHTMOVEMENTS, headers)

        cantidad_apoyo = df_fm["approach_charges"].gt(0).sum()
        monto_apoyo = df_fm["approach_charges"].sum()

        cantidad_proteccion = df_fm["enroute_charges"].gt(0).sum()
        monto_proteccion = df_fm["enroute_charges"].sum()

        cantidad_sna = df_fm["extended_hours_surcharge"].gt(0).sum()
        monto_sna = df_fm["extended_hours_surcharge"].sum()

        datos_factura = df_billing[df_billing["id"] == invoice_id].iloc[0]

        resultados.append({
            "id": invoice_id,
            "account_name": datos_factura["account.name"],
            "alias": datos_factura["alias"],
            "invoice_number": datos_factura["invoice_number"],
            "fecha_factura": datos_factura["invoice_period_or_date"],
            "moneda": datos_factura["invoice_currency.currency_code"],
            "monto_factura": datos_factura["invoice_amount"],
            "cantidad_apoyo": cantidad_apoyo,
            "monto_apoyo": monto_apoyo,
            "cantidad_proteccion": cantidad_proteccion,
            "monto_proteccion": monto_proteccion,
            "cantidad_sna": cantidad_sna,
            "monto_sna": monto_sna
        })

    df_final = pd.DataFrame(resultados)
    return df_final

# === Ejecución ===
if __name__ == "__main__":
    token = get_token_oauth2()
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        start_date = "2025-01-01"
        end_date = "2025-01-31"

        df_final = construir_df_final(start_date, end_date, headers)
        df_final.to_excel("reporte_facturas_servicios.xlsx", index=False)
        print("✅ Exportado como 'reporte_facturas_servicios.xlsx'")
