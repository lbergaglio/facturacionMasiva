import pandas as pd
import os
from datetime import datetime
from gui.components import archivos_cargados
#from parse_inputs import cargar_archivos
from logic.validators.validator_main import normalizar_headers
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
        # === Lectura de archivos de entrada ===
        df_dom = pd.read_excel(archivos_cargados['liq_dom_pbi'])
        df_int = pd.read_excel(archivos_cargados['liq_int_pbi'])
        df_arms = pd.read_excel(archivos_cargados['liq_arms']) if archivos_cargados['liq_arms'].endswith(".xlsx") else pd.read_csv(archivos_cargados['liq_arms'])
        df_clients = pd.read_excel(archivos_cargados['clients_pbi'])
    except Exception as e:
        raise RuntimeError(f"Error al leer los archivos: {e}")

    # === Unificación de doméstico e internacional ===
    df_liq = pd.concat([df_dom, df_int], ignore_index=True)
    df_liq['Número de Liquidacion'] = df_liq['Número']

    if 'id' not in df_liq.columns:
        raise RuntimeError("La columna 'id' no está presente en los archivos de liquidaciones PBI.")

    # === Normalizar campo "Tasa" según moneda ===
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

    # === Generar hoja "total" ===
    df_total = df_liq[COLUMNAS_TOTAL].copy()
    df_total['Fecha de Liquidación'] = pd.to_datetime(df_total['Fecha de Liquidación'], errors='coerce').dt.normalize()
    df_total['Período de Liquidación'] = pd.to_datetime(df_total['Período de Liquidación'], errors='coerce').dt.normalize()
    df_total.dropna(subset=['Fecha de Liquidación', 'Período de Liquidación'], inplace=True)
    df_total.sort_values(by='Número de Liquidacion', inplace=True)

    # === Agrupación por número de liquidación ===
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

    df_final = df_agrupado[columnas_finales_es].copy()

    # === VALIDACIÓN CONTRA ARCHIVO ARMS ===
    try:
        df_arms_original = pd.read_csv(archivos_cargados['liq_arms'])

        # === Renombrar columnas del archivo generado para coincidir con ARMS ===
        df_final_comparacion = df_final.copy()
        df_final_comparacion.columns = [
            'Account', 'Invoice Number', 'Invoice Date', 'Invoice Type', 'Status', 'Payment Due Date',
            'Created By', 'Invoice Amount', 'Invoice Currency', 'Exchange Rate To USD',
            'Invoice Date Of Issue', 'Proforma', 'Exported', 'Billing Centre'
        ]
        
        # === Eliminar columna "Created By" para la comparación ===
        df_final_comparacion.drop(columns=['Created By'], inplace=True)
        if 'Created By' in df_arms_original.columns:
            df_arms_original.drop(columns=['Created By'], inplace=True)

        # === Convertir fechas a datetime.date para ambos ===
        fecha_cols = ['Invoice Date', 'Payment Due Date', 'Invoice Date Of Issue']
        for col in fecha_cols:
            if col in df_arms_original.columns:
                df_arms_original[col] = pd.to_datetime(df_arms_original[col], errors='coerce').dt.date
            if col in df_final_comparacion.columns:
                df_final_comparacion[col] = pd.to_datetime(df_final_comparacion[col], errors='coerce').dt.date

        # === Normalizar strings ===
        for col in df_final_comparacion.columns:
            if df_final_comparacion[col].dtype == 'object':
                df_final_comparacion[col] = df_final_comparacion[col].astype(str).str.strip().str.upper()
        for col in df_arms_original.columns:
            if df_arms_original[col].dtype == 'object':
                df_arms_original[col] = df_arms_original[col].astype(str).str.strip().str.upper()
        
        # === Forzar que Proforma y Exportado sean string en minúsculas y sin espacios ===
        for col in ['Proforma', 'Exported']:
            if col in df_final_comparacion.columns:
                df_final_comparacion[col] = df_final_comparacion[col].astype(str).str.strip().str.lower()
            if col in df_arms_original.columns:
                df_arms_original[col] = df_arms_original[col].astype(str).str.strip().str.lower()


        # === Normalizar valores numéricos ===
        for col in ['Invoice Amount', 'Exchange Rate To USD']:
            if col in df_final_comparacion.columns:
                df_final_comparacion[col] = pd.to_numeric(df_final_comparacion[col], errors='coerce').round(2)
            if col in df_arms_original.columns:
                df_arms_original[col] = pd.to_numeric(df_arms_original[col], errors='coerce').round(2)

        # === Ordenar y comparar ===
        df_final_comparacion.sort_values(by="Invoice Number", inplace=True)
        df_arms_original.sort_values(by="Invoice Number", inplace=True)
        df_final_comparacion.reset_index(drop=True, inplace=True)
        df_arms_original.reset_index(drop=True, inplace=True)

        # Comparar fila a fila
        diferencias = df_final_comparacion.ne(df_arms_original[df_final_comparacion.columns])
        filas_con_diferencias = diferencias.any(axis=1)

        if filas_con_diferencias.any():
            df_diff = pd.DataFrame({
                'Número de Liquidación': df_final_comparacion.loc[filas_con_diferencias, 'Invoice Number'],
                'Diferencias': [
                    ", ".join(df_final_comparacion.columns[diferencias.iloc[i]])
                    for i in df_final_comparacion.index[filas_con_diferencias]
                ]
            })
            diff_path = f"salida/diferencias_con_arms.xlsx"
            df_diff.to_excel(diff_path, index=False)
            messagebox.showwarning("Advertencia", f"❌ El archivo generado no coincide con el archivo ARMS. Revisar diferencias: {diff_path}")
        else:
            messagebox.showinfo("Validación exitosa", "✅ El archivo generado coincide exactamente con el archivo ARMS.")

    except Exception as e:
        messagebox.showwarning("Advertencia", f"No se pudo comparar con el archivo ARMS: {e}")


    # === Exportar archivo Excel final con ambas hojas ===
    fecha_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("salida", exist_ok=True)
    path_salida = f"salida/control_interno_{fecha_str}.xlsx"

    with pd.ExcelWriter(path_salida, engine='openpyxl', datetime_format='DD/MM/YYYY') as writer:
        df_total.to_excel(writer, index=False, sheet_name="total")
        df_final.to_excel(writer, index=False, sheet_name="total agrupado por liquidacion")

        # Aplicar formato de fecha a las columnas de df_total
        workbook = writer.book
        ws_total = writer.sheets["total"]
        columnas_fecha_total = ['Fecha de Liquidación', 'Período de Liquidación']
        for col_name in columnas_fecha_total:
            col_idx = df_total.columns.get_loc(col_name) + 1
            for row in range(2, len(df_total) + 2):  # +2 porque Excel empieza en 1 y hay header
                ws_total.cell(row=row, column=col_idx).number_format = 'DD/MM/YYYY'

        # Aplicar formato de fecha a las columnas de df_final
        ws_final = writer.sheets["total agrupado por liquidacion"]
        columnas_fecha_final = ['Fecha de Factura', 'Vencimiento de Pago', 'Fecha de Emisión']
        for col_name in columnas_fecha_final:
            col_idx = df_final.columns.get_loc(col_name) + 1
            for row in range(2, len(df_final) + 2):
                ws_final.cell(row=row, column=col_idx).number_format = 'DD/MM/YYYY'

    return path_salida, df_total
