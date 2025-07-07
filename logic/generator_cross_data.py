import pandas as pd
import os
from datetime import datetime
from gui.components import archivos_cargados
from logic.validations.validator_main import normalizar_headers

TIPO_MAPEO = {
    "liq_dom_pbi": "powerbi_domestico",
    "liq_int_pbi": "powerbi_internacional",
    "clients_pbi": "clientes_maestros",
    "liq_arms": "liquidaciones_arms"
}

# Columnas esperadas para la hoja 'total'
COLUMNAS_TOTAL = [
    'nro Liquidacion', 'Fecha de Liquidación', 'Período de Liquidación', 'Cliente', 'Tipo Cliente',
    'Tipo de Factura', 'Concepto Facturado', 'Número', 'Moneda de Liquidación',
    'Tasa', 'Servicios', 'Monto', 'Km', 'id'
]

def generar_control_interno(tipo_cambio):
    try:
        df_dom = pd.read_excel(archivos_cargados['liq_dom_pbi'])
        df_int = pd.read_excel(archivos_cargados['liq_int_pbi'])
        df_arms = pd.read_excel(archivos_cargados['liq_arms']) if archivos_cargados['liq_arms'].endswith(".xlsx") else pd.read_csv(archivos_cargados['liq_arms'])
        df_clients = pd.read_excel(archivos_cargados['clients_pbi'])
    except Exception as e:
        raise RuntimeError(f"Error al leer los archivos: {e}")

    # Unimos las liquidaciones domésticas e internacionales
    df_liq = pd.concat([df_dom, df_int], ignore_index=True)

    # Crear columna 'nro Liquidacion' como duplicado de 'Número'
    df_liq['nro Liquidacion'] = df_liq['Número']

    # Aseguramos que 'id' provenga de df_liq original (no de clientes)
    if 'id' not in df_liq.columns:
        raise RuntimeError("La columna 'id' no está presente en los archivos de liquidaciones PBI.")

    # Normalizar columna Tasa en función de Moneda y Concepto
    def convertir_tasa(row):
        concepto = str(row['Concepto Facturado']).upper().strip()
        moneda = str(row['Moneda de Liquidación']).upper().strip()
        if "APOYO" in concepto:
            return "AAI" if moneda == "USD" else "AAN"
        elif "PROTECCION" in concepto:
            return "PVI" if moneda == "USD" else "PVN"
        elif "SNA" in concepto or "SOBREVUELO" in concepto:
            return "EXTI" if moneda == "USD" else "EXT"
        else:
            return row['Tasa']  # valor original si no hay coincidencia

    df_liq['Tasa'] = df_liq.apply(convertir_tasa, axis=1)

    # Reordenamos y renombramos para hoja 'total'
    columnas_finales = [
        'nro Liquidacion', 'Fecha de Liquidación', 'Período de Liquidación', 'Cliente', 'Tipo Cliente',
        'Tipo de Factura', 'Concepto Facturado', 'Número', 'Moneda de Liquidación',
        'Tasa', 'Servicios', 'Monto', 'Km', 'id'
    ]

    df_total = df_liq[columnas_finales].copy()

    # Ordenar por nro Liquidacion
    df_total.sort_values(by='nro Liquidacion', inplace=True)

    # Generar nombre de archivo y guardar
    fecha_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("salida", exist_ok=True)
    path_salida = f"salida/control_interno_{fecha_str}.xlsx"
    df_total.to_excel(path_salida, index=False, sheet_name="total")

    return path_salida,df_total

