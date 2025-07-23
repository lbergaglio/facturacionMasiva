import requests
import getpass
import pandas as pd
from tqdm import tqdm
#from gui.components import solicitar_credenciales_api
#from logic.api_access.tokens.arms_token import get_token_oauth2
"""from config.settings_api_arms import (
    API_BASE,
    ENDPOINT_ACCOUNT, ENDPOINT_BILLING_LEDGER, ENDPOINT_FLIGHTMOVEMENT,
    MAPEO_TASAS, MAPEO_ACCOUNT_TYPES, MAPEO_ACCOUNT_TYPES_REV, MAPEO_INVOICE_CONCEPTS,
    COLUMNS_ACCOUNT, COLUMNS_BILLING_LEDGER, COLUMNS_FLIGHTMOVEMENTS,
    CLIENT_ID, CLIENT_SECRET,TOKEN_URL
)
"""
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
    "invoice_period_or_date", "invoice_date_of_issue", "account.name", "account.id","invoice_type", "flightmovement_category.name",
    "invoice_number", "invoice_currency.currency_code", "invoice_amount",
    "invoice_state_type", "billing_center.name", "id"
]
COLUMNS_FLIGHTMOVEMENTS = ["associated_account_id","invoice_id", "enroute_charges", "approach_charges", "extended_hours_surcharge", "fpl_crossing_distance", "enroute_result_currency.currency_code"]

CLIENT_ID = "abms_external_client"
CLIENT_SECRET = ""

pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 0)

def get_token_oauth2():
    #username, password = solicitar_credenciales_api("Autenticación ARMS API")
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

def generate_total_and_clients(start_date, end_date, tasa_de_cambio):
    token = get_token_oauth2()
    if not token:
        raise RuntimeError("No se pudo obtener el token OAuth2.")

    headers = {"Authorization": f"Bearer {token}"}

    print("🔹 Paso 1: Extrayendo billing-ledgers...")
    df_billing_ledgers = get_dataframe_paginado(
        f"{API_BASE}{ENDPOINT_BILLING_LEDGER}?startDate={start_date}&endDate={end_date}",
        COLUMNS_BILLING_LEDGER,
        headers
    )

    print("🔹 Paso 2: Extrayendo accounts...")
    df_accounts = get_dataframe_paginado(
        API_BASE + ENDPOINT_ACCOUNT,
        COLUMNS_ACCOUNT,
        headers
    )

    df_billing_ledgers = df_billing_ledgers.merge(
        df_accounts[["name", "alias", "account_type.name", "id"]],
        how="left",
        left_on="account.name",
        right_on="name",
        suffixes=("", "_account")
    )
    df_billing_ledgers.rename(columns={"id_account": "account.id"}, inplace=True)

    print("🔹 Paso 3: Extrayendo todos los flightmovements por fecha...")
    df_flightmovements_all = get_dataframe_paginado(
        f"{API_BASE}{ENDPOINT_FLIGHTMOVEMENT}/filters?start={start_date}&end={end_date}",
        COLUMNS_FLIGHTMOVEMENTS,
        headers
    )

    if "enroute_result_currency.currency_code" in df_flightmovements_all.columns:
        df_flightmovements_all["currency_col"] = df_flightmovements_all["enroute_result_currency.currency_code"]
    elif "enroute_invoice_currency.currency_code" in df_flightmovements_all.columns:
        df_flightmovements_all["currency_col"] = df_flightmovements_all["enroute_invoice_currency.currency_code"]
    else:
        raise KeyError("No se encontró ninguna columna de moneda en los flightmovements")

    resultados = []

    for _, factura in tqdm(df_billing_ledgers.iterrows(), total=len(df_billing_ledgers), desc="Procesando facturas"):
        invoice_id = factura["id"]
        account_id = factura["account.id"]
        moneda = factura["invoice_currency.currency_code"]

        df_fm = df_flightmovements_all[
            (df_flightmovements_all["associated_account_id"].values == account_id) &
            (df_flightmovements_all["currency_col"].values == moneda)
        ]

        invoice_date = pd.to_datetime(factura["invoice_date_of_issue"]).strftime("%d/%m/%Y")
        period_date = pd.to_datetime(factura["invoice_period_or_date"]).strftime("%d/%m/%Y")
        account_type = factura["account_type.name"]
        invoice_type = factura["invoice_type"]
        invoice_concept = factura["flightmovement_category.name"]

        approach_qty = df_fm["approach_charges"].gt(0).sum()
        approach_amount = df_fm["approach_charges"].sum()
        approach_distance = 0

        protection_qty = df_fm["enroute_charges"].gt(0).sum()
        protection_amount = df_fm["enroute_charges"].sum()
        protection_distance = df_fm["fpl_crossing_distance"].sum() if "fpl_crossing_distance" in df_fm.columns else 0

        sna_qty = df_fm["extended_hours_surcharge"].gt(0).sum()
        sna_amount = df_fm["extended_hours_surcharge"].sum()
        sna_distance = 0

        resultados.extend([
            {
                "Número de Liquidacion": factura["invoice_number"],
                "Fecha de Liquidación": invoice_date,
                "Período de Liquidación": period_date,
                "Cliente": factura["account.name"],
                "Tipo Cliente": MAPEO_ACCOUNT_TYPES.get(account_type, "DESCONOCIDO"),
                "Tipo de Factura": invoice_type,
                "Concepto Facturado": MAPEO_INVOICE_CONCEPTS.get(invoice_concept, "DESCONOCIDO"),
                "Moneda de Liquidación": moneda,
                "Tasa": MAPEO_TASAS.get(("APOYO", moneda), "DESCONOCIDO"),
                "Servicios": approach_qty,
                "Monto": approach_amount,
                "Km": approach_distance,
                "id": invoice_id,
                "Tasa de cambio": tasa_de_cambio
            },
            {
                "Número de Liquidacion": factura["invoice_number"],
                "Fecha de Liquidación": invoice_date,
                "Período de Liquidación": period_date,
                "Cliente": factura["account.name"],
                "Tipo Cliente": MAPEO_ACCOUNT_TYPES.get(account_type, "DESCONOCIDO"),
                "Tipo de Factura": invoice_type,
                "Concepto Facturado": MAPEO_INVOICE_CONCEPTS.get(invoice_concept, "DESCONOCIDO"),
                "Moneda de Liquidación": moneda,
                "Tasa": MAPEO_TASAS.get(("PROTECCION", moneda), "DESCONOCIDO"),
                "Servicios": protection_qty,
                "Monto": protection_amount,
                "Km": protection_distance,
                "id": invoice_id,
                "Tasa de cambio": tasa_de_cambio
            },
            {
                "Número de Liquidacion": factura["invoice_number"],
                "Fecha de Liquidación": invoice_date,
                "Período de Liquidación": period_date,
                "Cliente": factura["account.name"],
                "Tipo Cliente": MAPEO_ACCOUNT_TYPES.get(account_type, "DESCONOCIDO"),
                "Tipo de Factura": invoice_type,
                "Concepto Facturado": MAPEO_INVOICE_CONCEPTS.get(invoice_concept, "DESCONOCIDO"),
                "Moneda de Liquidación": moneda,
                "Tasa": MAPEO_TASAS.get(("SNA", moneda), "DESCONOCIDO"),
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




#if __name__ == "__main__":
generate_total_and_clients(start_date="2025-02-01", end_date="2025-02-18", tasa_de_cambio=1270)
