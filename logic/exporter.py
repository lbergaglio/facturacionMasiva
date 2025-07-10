import os
import pandas as pd
import openpyxl
from datetime import datetime

def exportar_control_interno(df_total, df_final,path_salida):
    fecha_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("salida", exist_ok=True)

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