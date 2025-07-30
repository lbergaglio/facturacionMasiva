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
COLUMNS_FLIGHTMOVEMENTS = ["invoice_id", "enroute_charges", "approach_charges", "extended_hours_surcharge", "fpl_crossing_distance","exempt_enroute_charges","exempt_approch_charges","exempt_extended_hours_surcharge"]

CLIENT_ID = "abms_external_client"
CLIENT_SECRET = ""