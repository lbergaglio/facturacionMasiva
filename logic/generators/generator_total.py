import pandas as pd

# === Normalizar campo "Tasa" según moneda ===
def transform_rate(row):
        tasa = str(row['Tasa']).upper().strip()
        moneda = str(row['Moneda de Liquidación']).upper().strip()
        if "APOYO" in tasa:
            return "AAI" if moneda == "USD" else "AAN"
        elif "PROTECCION" in tasa:
            return "PVI" if moneda == "USD" else "PVN"
        elif "SNA" in tasa or "SOBREVUELO" in tasa:
            return "EXTI" if moneda == "USD" else "EXT"
        else:
            return row['Tasa']

# === Unificación de doméstico e internacional ===
def generate_page_total(df_dom, df_int, COLUMNAS_TOTAL):
    df_liq = pd.concat([df_dom, df_int], ignore_index=True)
    df_liq.columns = df_liq.columns.str.strip()
    df_liq['Número de Liquidacion'] = df_liq['Número']

    if 'id' not in df_liq.columns:
        print(df_liq.columns)
        raise RuntimeError("La columna 'id' no está presente en los archivos de liquidaciones PBI.")
    
    df_liq['Tasa'] = df_liq.apply(transform_rate, axis=1)

    # === Generar hoja "total" ===
    df_total = df_liq[COLUMNAS_TOTAL].copy()
    df_total = df_total[df_total["Tipo Cliente"] != "8"]
    df_total = df_total[~df_total["Tipo de Factura"].isin(["non-aviation", "unified-tax"])]
    df_total['Fecha de Liquidación'] = pd.to_datetime(df_total['Fecha de Liquidación'], errors='coerce').dt.strftime('%d/%m/%Y')
    df_total['Período de Liquidación'] = pd.to_datetime(df_total['Período de Liquidación'], errors='coerce').dt.strftime('%d/%m/%Y')
    df_total.dropna(subset=['Fecha de Liquidación', 'Período de Liquidación'], inplace=True)
    df_total.sort_values(by='Número de Liquidacion', inplace=True)
    

    return df_total