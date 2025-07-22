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

MAPEO_TASAS = {
    ("APOYO", "ARS"): "AAN",
    ("APOYO", "USD"): "AAI",
    ("PROTECCION", "ARS"): "PVN",
    ("PROTECCION", "USD"): "PVI",
    ("SNA", "ARS"): "EXT",
    ("SNA", "USD"): "EXTI",
}

MAPEO_ACCOUNT_TYPES = {
    "Airline": "AEROLINEAS",
    "GeneralAviation": "AVIACION GENERAL",
}

MAPEO_ACCOUNT_TYPES_REV = {
    "Airline": 1,
    "GeneralAviation": 8,
}

MAPEO_INVOICE_CONCEPTS = {
    "INTERNATIONAL/FOREIGN" : "INTERNACIONAL/EXTRANJERO",
    "INTERNATIONAL/NATIONAL" : "INTERNACIONAL/NACIONAL",
    "OVERFLIGHT/FOREIGN" : "SOBREVUELO/EXTRANJERO",
    "OVERFLIGHT/NATIONAL" : "SOBREVUELO/NACIONAL",
    "DOMESTIC/FOREIGN" : "NACIONAL/EXTRANJERO",
    "DOMESTIC/NATIONAL" : "NACIONAL/NACIONAL",
}

COLUMNS_ACCOUNT = [
    "name", "icao_code","iata_code", "alias","aviation_billing_contact_person_name", "aviation_billing_email_address",
    "account_type.name","nationality","aircraft_parking_exemption","active","approved_flight_school_indicator",
    "aviation_billing_sms_number","black_listed_indicator","black_listed_override", "cash_account", "created_at",
    "created_by","credit_limit","discount_structure","iata_member","id", "invoice_currency","invoice_delivery_format",
    "invoice_delivery_method", "is_self_care", "monthly_overdue_penalty_rate", "non_aviation_billing_contact_person_name",
    "non_aviation_billing_email_address", "non_aviation_billing_mailing_address", "non_aviation_billing_phone_number",
    "non_aviation_billing_sms_number", "notes", "opr_identifier", "payment_terms", "percentage_of_passenger_fee_payable",
    "separate_pax_invoice", "tax_profile", "updated_at", "updated_by", "version"]
COLUMNS_BILLING_LEDGER = [
    "invoice_period_or_date", "invoice_date_of_issue", "account.name", "invoice_type", "flightmovement_category.name",
    "invoice_number", "invoice_currency.currency_code", "invoice_amount",
    "invoice_state_type", "billing_center.name", "id"
]
COLUMNS_FLIGHTMOVEMENTS = ["invoice_id", "enroute_charges", "approach_charges", "extended_hours_surcharge", "fpl_crossing_distance"]

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
def generate_total_and_clients(start_date, end_date, tasa_de_cambio):
    token = get_token_oauth2()
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        print("🔹 Paso 1: Extrayendo billing-ledgers...")
        df_billing_ledgers = get_dataframe_paginado(
            f"{API_BASE}{ENDPOINT_BILLING_LEDGER}?startDate={start_date}&endDate={end_date}",
            COLUMNS_BILLING_LEDGER,
            headers
        )

        print("🔹 Paso 2: Extrayendo accounts...")
        df_accounts = get_dataframe_paginado(API_BASE + ENDPOINT_ACCOUNT, COLUMNS_ACCOUNT, headers)
        df_billing_ledgers = df_billing_ledgers.merge(df_accounts[["name", "alias","account_type.name"]], how="left", left_on="account.name", right_on="name")

        resultados = []
        print("🔹 Paso 3: Extrayendo flightmovements por id...")
        for invoice_id in tqdm(df_billing_ledgers["id"].dropna().unique(), desc="Procesando invoices"):
            url_flightmovements = f"{API_BASE}flightmovements/list/invoices/{invoice_id}"
            df_flightmovements = get_dataframe_paginado(url_flightmovements, COLUMNS_FLIGHTMOVEMENTS, headers)

            invoice_date = pd.to_datetime(
                df_billing_ledgers.loc[df_billing_ledgers["id"] == invoice_id, "invoice_date_of_issue"].iloc[0]
            ).strftime("%d/%m/%Y")

            period_date = pd.to_datetime(
                df_billing_ledgers.loc[df_billing_ledgers["id"] == invoice_id, "invoice_period_or_date"].iloc[0]
            ).strftime("%d/%m/%Y")

            account_type = df_billing_ledgers[df_billing_ledgers["id"] == invoice_id]["account_type.name"].iloc[0]

            invoice_type = df_billing_ledgers[df_billing_ledgers["id"] == invoice_id]["invoice_type"].iloc[0]
            invoice_concept = df_billing_ledgers[df_billing_ledgers["id"] == invoice_id]["flightmovement_category.name"].iloc[0]

            approach_qty = df_flightmovements["approach_charges"].gt(0).sum()
            approach_amount = df_flightmovements["approach_charges"].sum()
            approach_distance = 0

            protection_qty = df_flightmovements["enroute_charges"].gt(0).sum()
            protection_amount = df_flightmovements["enroute_charges"].sum()
            protection_distance = df_flightmovements["fpl_crossing_distance"].sum() if "fpl_crossing_distance" in df_flightmovements.columns else 0

            sna_qty = df_flightmovements["extended_hours_surcharge"].gt(0).sum()
            sna_amount = df_flightmovements["extended_hours_surcharge"].sum()
            sna_distance = 0

            datos_factura = df_billing_ledgers[df_billing_ledgers["id"] == invoice_id].iloc[0]

            moneda = datos_factura["invoice_currency.currency_code"]

            df_accounts["account_type"] = df_accounts["account_type.name"].apply(lambda x: MAPEO_ACCOUNT_TYPES_REV.get(x, "DESCONOCIDO"))

            # Agregar una fila por tipo de Tasa
            resultados.extend([
                {
                    "Número de Liquidacion": datos_factura["invoice_number"],
                    "Fecha de Liquidación": invoice_date,
                    "Período de Liquidación": period_date,
                    "Cliente": datos_factura["account.name"],
                    #"alias": datos_factura["alias"],
                    "Tipo Cliente": MAPEO_ACCOUNT_TYPES[account_type],
                    "Tipo de Factura": invoice_type,
                    "Concepto Facturado": MAPEO_INVOICE_CONCEPTS.get(invoice_concept, "DESCONOCIDO"),
                    "Moneda de Liquidación": moneda,
                    "Tasa": MAPEO_TASAS[("APOYO", moneda)],
                    "Servicios": approach_qty,
                    "Monto": approach_amount,
                    "Km": approach_distance,
                    "id": invoice_id,
                    "Tasa de cambio": tasa_de_cambio
                },
                {
                    "Número de Liquidacion": datos_factura["invoice_number"],
                    "Fecha de Liquidación": invoice_date,
                    "Período de Liquidación": period_date,
                    "Cliente": datos_factura["account.name"],
                    #"alias": datos_factura["alias"],
                    "Tipo Cliente": MAPEO_ACCOUNT_TYPES[account_type],
                    "Tipo de Factura": invoice_type,
                    "Concepto Facturado": MAPEO_INVOICE_CONCEPTS.get(invoice_concept, "DESCONOCIDO"),
                    "Moneda de Liquidación": moneda,
                    "Tasa": MAPEO_TASAS[("PROTECCION", moneda)],
                    "Servicios": protection_qty,
                    "Monto": protection_amount,
                    "Km": protection_distance,
                    "id": invoice_id,
                    "Tasa de cambio": tasa_de_cambio
                },
                {
                    "Número de Liquidacion": datos_factura["invoice_number"],
                    "Fecha de Liquidación": invoice_date,
                    "Período de Liquidación": period_date,
                    "Cliente": datos_factura["account.name"],
                    #"alias": datos_factura["alias"],
                    "Tipo Cliente": MAPEO_ACCOUNT_TYPES[account_type],
                    "Tipo de Factura": invoice_type,
                    "Concepto Facturado": MAPEO_INVOICE_CONCEPTS.get(invoice_concept, "DESCONOCIDO"),
                    "Moneda de Liquidación": moneda,
                    "Tasa": MAPEO_TASAS[("SNA", moneda)],
                    "Servicios": sna_qty,
                    "Monto": sna_amount,
                    "Km": sna_distance,
                    "id": invoice_id,
                    "Tasa de cambio": tasa_de_cambio
                },
            ])

        df_final = pd.DataFrame(resultados)
        df_final.to_excel("reporte_facturas_servicios.xlsx", index=False)
        df_accounts.to_excel("reporte_clientes.xlsx", index=False)
        return df_final, df_accounts
    else:
        raise RuntimeError("No se pudo obtener el token OAuth2.")

# === Ejecución ===
if __name__ == "__main__":
    generate_total_and_clients()
