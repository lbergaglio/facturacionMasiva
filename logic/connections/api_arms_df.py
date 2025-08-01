import requests
import pandas as pd
import getpass
from tqdm import tqdm
from gui.components import solicitar_credenciales_api
from logic.connections.tokens.arms_token import get_token_oauth2
from config.settings_api_arms import TOKEN_URL, API_BASE, ENDPOINT_ACCOUNT, ENDPOINT_BILLING_LEDGER, \
    ENDPOINT_FLIGHTMOVEMENT, MAPEO_TASAS, MAPEO_ACCOUNT_TYPES, MAPEO_ACCOUNT_TYPES_REV, MAPEO_INVOICE_CONCEPTS, \
    COLUMNS_ACCOUNT, COLUMNS_BILLING_LEDGER, COLUMNS_FLIGHTMOVEMENTS

# === Configuración de Pandas ===
pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 0)

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
            
            # Verifica si la columna existe en el DataFrame antes de acceder a ella
            if "flightmovement_category.name" in df_billing_ledgers.columns:
                invoice_concept = df_billing_ledgers[df_billing_ledgers["id"] == invoice_id]["flightmovement_category.name"].fillna("DESCONOCIDO").iloc[0]
            else:
                invoice_concept = "DESCONOCIDO"

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
