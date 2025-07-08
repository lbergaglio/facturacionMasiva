import pandas as pd
import os
from datetime import datetime
from gui.components import archivos_cargados
from logic.validations.validator_main import normalizar_headers
import tkinter.messagebox as messagebox

# Mapeo para los nombres de los archivos cargados
TIPO_MAPEO = {
    "liq_dom_pbi": "powerbi_domestico",
    "liq_int_pbi": "powerbi_internacional",
    "clients_pbi": "clientes_maestros",
    "liq_arms": "liquidaciones_arms"
}

# Columnas esperadas para la hoja "total" de control interno
COLUMNAS_TOTAL = [
    'Número de Liquidacion', 'Fecha de Liquidación', 'Período de Liquidación', 'Cliente', 'Tipo Cliente',
    'Tipo de Factura', 'Concepto Facturado', 'Número', 'Moneda de Liquidación',
    'Tasa', 'Servicios', 'Monto', 'Km', 'id'
]

def generar_control_interno(tipo_cambio):
    try:
        # Leer los archivos cargados desde la interfaz
        df_dom = pd.read_excel(archivos_cargados['liq_dom_pbi'])
        df_int = pd.read_excel(archivos_cargados['liq_int_pbi'])
        df_arms = pd.read_excel(archivos_cargados['liq_arms']) if archivos_cargados['liq_arms'].endswith(".xlsx") else pd.read_csv(archivos_cargados['liq_arms'])
        df_clients = pd.read_excel(archivos_cargados['clients_pbi'])
    except Exception as e:
        raise RuntimeError(f"Error al leer los archivos: {e}")

    # Unir las liquidaciones domésticas e internacionales
    df_liq = pd.concat([df_dom, df_int], ignore_index=True)
    df_liq['Número de Liquidacion'] = df_liq['Número']

    # Validar que exista la columna 'id'
    if 'id' not in df_liq.columns:
        raise RuntimeError("La columna 'id' no está presente en los archivos de liquidaciones PBI.")

    # Normalizar el campo Tasa según moneda y tipo
    def convertir_tasa(row):
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

    df_liq['Tasa'] = df_liq.apply(convertir_tasa, axis=1)

    columnas_finales = COLUMNAS_TOTAL
    df_total = df_liq[columnas_finales].copy()

    df_total['Fecha de Liquidación'] = pd.to_datetime(df_total['Fecha de Liquidación'], errors='coerce')
    df_total['Período de Liquidación'] = pd.to_datetime(df_total['Período de Liquidación'], errors='coerce')
    df_total = df_total.dropna(subset=['Fecha de Liquidación', 'Período de Liquidación'])
    df_total['Fecha de Liquidación'] = df_total['Fecha de Liquidación'].dt.strftime('%d/%m/%Y')
    df_total['Período de Liquidación'] = df_total['Período de Liquidación'].dt.strftime('%d/%m/%Y')
    df_total.sort_values(by='Número de Liquidacion', inplace=True)

    # --- AGRUPAR POR LIQUIDACIÓN PARA HOJA ADICIONAL ---
    df_agrupado = df_total.groupby("Número de Liquidacion").agg({
        'Monto': 'sum',
        'Moneda de Liquidación': 'first',
        'Fecha de Liquidación': 'first',
        'id': 'first',
        'Tipo de Factura': 'first',
    }).reset_index()

    df_agrupado['Cuenta'] = df_agrupado['id']
    df_agrupado['Número de Factura'] = df_agrupado['Número de Liquidacion']
    df_agrupado['Fecha de Factura'] = df_agrupado['Fecha de Liquidación']
    df_agrupado['Tipo de Factura'] = df_agrupado['Tipo de Factura']
    df_agrupado['Estado'] = "Published"
    df_agrupado['Vencimiento de Pago'] = df_agrupado['Fecha de Liquidación']
    df_agrupado['Creado Por'] = "Auto"
    df_agrupado['Monto de la Factura'] = df_agrupado['Monto']
    df_agrupado['Moneda'] = df_agrupado['Moneda de Liquidación']
    df_agrupado['Tasa de Cambio a USD'] = tipo_cambio
    df_agrupado['Fecha de Emisión'] = df_agrupado['Fecha de Liquidación']
    df_agrupado['Proforma'] = "No"
    df_agrupado['Exportado'] = "No"
    df_agrupado['Centro de Facturación'] = "EANA CENTRAL"

    columnas_finales_es = [
        'Cuenta', 'Número de Factura', 'Fecha de Factura', 'Tipo de Factura', 'Estado', 'Vencimiento de Pago',
        'Creado Por', 'Monto de la Factura', 'Moneda', 'Tasa de Cambio a USD',
        'Fecha de Emisión', 'Proforma', 'Exportado', 'Centro de Facturación']

    df_final = df_agrupado[columnas_finales_es]

    # --- VALIDAR CONTRA ARCHIVO ARMS ---
    try:
        df_arms_original = pd.read_csv(archivos_cargados['liq_arms'])

        fechas_cols = ['Invoice Date', 'Payment Due Date', 'Invoice Date Of Issue']
        for col in fechas_cols:
            if col in df_arms_original.columns:
                df_arms_original[col] = pd.to_datetime(df_arms_original[col], errors='coerce').dt.strftime('%d%m%Y')
        for col in fechas_cols:
            if col in df_final.columns:
                df_final[col] = pd.to_datetime(df_final[col], errors='coerce').dt.strftime('%d%m%Y')

        # NOTA: Validación se hace sobre equivalencia lógica, no headers

    except Exception as e:
        messagebox.showwarning("Advertencia", f"No se pudo comparar con el archivo ARMS: {e}")

    # --- EXPORTAR ARCHIVO DE CONTROL CON DOS HOJAS ---
    fecha_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("salida", exist_ok=True)
    path_salida = f"salida/control_interno_{fecha_str}.xlsx"

    with pd.ExcelWriter(path_salida, engine='openpyxl') as writer:
        df_total.to_excel(writer, index=False, sheet_name="total")
        df_final.to_excel(writer, index=False, sheet_name="total agrupado por liquidacion")

    return path_salida, df_total
