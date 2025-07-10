import os
import pandas as pd
import openpyxl
from datetime import datetime

def exportar_control_interno(df_total, df_total_per_liq, df_balance, df_diff_arms, path_salida):
    os.makedirs("salida", exist_ok=True)

    # Intentar borrar el archivo si ya existe
    if os.path.exists(path_salida):
        try:
            os.remove(path_salida)
        except PermissionError:
            raise PermissionError(f"No se puede sobrescribir el archivo: {path_salida}. Cerralo si está abierto.")

    # Exportar diferencias con ARMS si hay
    if not df_diff_arms.empty:
        df_diff_arms.to_excel("salida/diferencias_con_arms.xlsx", index=False)

    # --- LIMPIEZA GENERAL DE df_balance ---
    df_balance_export = df_balance.reset_index()
    df_balance_export.columns = [str(c).strip() for c in df_balance_export.columns]
    df_balance_export = df_balance_export.applymap(lambda x: x if pd.api.types.is_numeric_dtype(type(x)) else str(x))

    with pd.ExcelWriter(path_salida, engine='openpyxl', datetime_format='DD/MM/YYYY') as writer:
        # Hoja 1
        df_total.to_excel(writer, index=False, sheet_name="total")
        # Hoja 2
        df_total_per_liq.to_excel(writer, index=False, sheet_name="total agrupado por liquidacion")
        # Hoja 3
        df_balance_export.to_excel(writer, index=False, sheet_name="TD LIQ - por Moneda y Tipo Cliente")

        # --- FORMATO FECHA: total ---
        ws_total = writer.sheets["total"]
        for col in ['Fecha de Liquidación', 'Período de Liquidación']:
            if col in df_total.columns:
                col_idx = df_total.columns.get_loc(col) + 1
                for row in range(2, len(df_total) + 2):
                    ws_total.cell(row=row, column=col_idx).number_format = 'DD/MM/YYYY'

        # --- FORMATO FECHA: agrupado ---
        ws_agrupado = writer.sheets["total agrupado por liquidacion"]
        for col in ['Fecha de Factura', 'Vencimiento de Pago', 'Fecha de Emisión']:
            if col in df_total_per_liq.columns:
                col_idx = df_total_per_liq.columns.get_loc(col) + 1
                for row in range(2, len(df_total_per_liq) + 2):
                    ws_agrupado.cell(row=row, column=col_idx).number_format = 'DD/MM/YYYY'
        
        

    return path_salida, df_total
