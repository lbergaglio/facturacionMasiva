import pandas as pd

# === Agrupación por número de liquidación ===
def generate_page_total_per_liq(df_total, tipo_cambio):
    
    df_agrupado = df_total.groupby("Número de Liquidacion").agg({
        'Monto': 'sum',
        'Moneda de Liquidación': 'first',
        'Fecha de Liquidación': 'first',
        'id': 'first',
        'Tipo de Factura': 'first',
    }).reset_index()

    # === Construcción hoja "total agrupado por liquidacion" ===
    mapa_id_a_cliente = df_total.set_index('id')['Cliente'].to_dict()

    df_agrupado['Cuenta'] = df_agrupado['id'].map(mapa_id_a_cliente)
    df_agrupado['Número de Factura'] = df_agrupado['Número de Liquidacion']
    df_agrupado['Fecha de Factura'] = pd.to_datetime(df_agrupado['Fecha de Liquidación'], errors='coerce')
    df_agrupado['Estado'] = "Published"
    df_agrupado['Vencimiento de Pago'] = df_agrupado['Fecha de Factura'] + pd.Timedelta(days=10)
    df_agrupado['Creado Por'] = "Auto"
    df_agrupado['Monto de la Factura'] = df_agrupado['Monto']
    df_agrupado['Moneda'] = df_agrupado['Moneda de Liquidación']
    df_agrupado['Tasa de Cambio a USD'] = tipo_cambio
    df_agrupado['Fecha de Emisión'] = df_agrupado['Fecha de Liquidación']
    df_agrupado['Proforma'] = "false"
    df_agrupado['Exported'] = "false"
    df_agrupado['Centro de Facturación'] = "EANA CENTRAL"


    columnas_finales_es = [
        'Cuenta', 'Número de Factura', 'Fecha de Factura', 'Tipo de Factura', 'Estado', 'Vencimiento de Pago',
        'Creado Por', 'Monto de la Factura', 'Moneda', 'Tasa de Cambio a USD',
        'Fecha de Emisión', 'Proforma', 'Exported', 'Centro de Facturación'
    ]

    return df_agrupado[columnas_finales_es].copy()