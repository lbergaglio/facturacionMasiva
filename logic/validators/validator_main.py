import os
import pandas as pd

HEADERS_ESPERADOS = {
    "powerbi_domestico": [
        "Fecha de Liquidación", "Período de Liquidación", "Cliente", "Tipo Cliente", "Tipo de Factura",
        "Concepto Facturado", "Número", "Moneda de Liquidación", "Tasa", "Servicios", "Monto", "Km", "id"
    ],
    "powerbi_internacional": [
        "Fecha de Liquidación", "Período de Liquidación", "Cliente", "Tipo Cliente", "Tipo de Factura",
        "Concepto Facturado", "Número", "Moneda de Liquidación", "Tasa", "Servicios", "Monto", "Km", "id"
    ],
    "clientes_maestros": [
        "name", "icao_code", "iata_code", "alias", "aviation_billing_contact_person_name",
        "aviation_billing_phone_number", "aviation_billing_mailing_address", "aviation_billing_email_address",
        "account_type", "nationality", "aircraft_parking_exemption", "active", "approved_flight_school_indicator",
        "aviation_billing_sms_number", "black_listed_indicator", "black_listed_override", "cash_account",
        "created_at", "created_by", "credit_limit", "discount_structure", "iata_member", "id",
        "invoice_currency", "invoice_delivery_format", "invoice_delivery_method", "is_self_care",
        "monthly_overdue_penalty_rate", "non_aviation_billing_contact_person_name",
        "non_aviation_billing_email_address", "non_aviation_billing_mailing_address",
        "non_aviation_billing_phone_number", "non_aviation_billing_sms_number", "notes", "opr_identifier",
        "payment_terms", "percentage_of_passenger_fee_payable", "separate_pax_invoice", "tax_profile",
        "updated_at", "updated_by", "version"
    ],
    "liquidaciones_arms": [
        "Account", "Invoice Number", "Invoice Date", "Invoice Type", "Status", "Payment Due Date",
        "Created By", "Invoice Amount", "Invoice Currency", "Exchange Rate To USD", "Invoice Date Of Issue",
        "Proforma", "Exported", "Billing Centre"
    ]
}

def normalizar_headers(headers):
    return [str(h).strip().lower() for h in headers]

def validar_headers_excel(filepath, tipo_archivo):
    try:
        if tipo_archivo == "liquidaciones_arms" and filepath.lower().endswith(".csv"):
            df = pd.read_csv(filepath)
        else:
            if filepath.lower().endswith(".csv"):
                return False, f"El archivo para {tipo_archivo} debe ser .xls o .xlsx"
            df = pd.read_excel(filepath)
    except Exception as e:
        return False, f"No se pudo leer el archivo: {e}"

    headers = list(df.columns)
    esperado = HEADERS_ESPERADOS.get(tipo_archivo)
    if esperado is None:
        return False, "Tipo de archivo desconocido."

    esperado_set = set(normalizar_headers(esperado))
    headers_set = set(normalizar_headers(headers))

    faltantes = esperado_set - headers_set
    extra = headers_set - esperado_set

    if faltantes or extra:
        return False, (
            f"Headers incorrectos para {tipo_archivo.replace('_', ' ').title()}.\n"
            f"Faltantes: {faltantes}\nExtra: {extra}"
        )

    # Validaciones adicionales
    if tipo_archivo in ["powerbi_domestico", "powerbi_internacional"]:
        col = "Moneda de Liquidación"
        esperado_valor = "ARS" if tipo_archivo == "powerbi_domestico" else "USD"
        if col not in df.columns:
            return False, f"Falta la columna '{col}'."
        valores = df[col].dropna().astype(str).str.upper().str.strip()
        if not all(valores == esperado_valor):
            valores_distintos = valores[valores != esperado_valor].unique()
            return False, f"La columna '{col}' debe contener solo '{esperado_valor}'. Valores encontrados: {valores_distintos}"

    elif tipo_archivo == "liquidaciones_arms":
        if not pd.api.types.is_numeric_dtype(df['Exchange Rate To USD']):
            return False, "La columna 'Exchange Rate To USD' debe ser numérica."
        fechas = ['Invoice Date', 'Payment Due Date', 'Invoice Date Of Issue']
        for col in fechas:
            if col not in df.columns:
                return False, f"Falta la columna '{col}'"
            try:
                pd.to_datetime(df[col])
            except:
                return False, f"La columna '{col}' contiene valores no reconocidos como fechas."

    return True, "Archivo válido."
