import pandas as pd
import os
from datetime import datetime
from gui.components import archivos_cargados
from logic.parse_inputs import cargar_archivos
import tkinter.messagebox as messagebox
from logic.exporter import exportar_control_interno
from logic.generators.generator_total import generar_page_total
from logic.generators.generator_total_per_liq import generar_page_total_per_liq
from logic.validators.validator_arms import validar_y_comparar_con_arms

# Ruta de salida para el archivo generado
PATH_SALIDA = "salida/control_interno.xlsx"

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
     # === Lectura de archivos de entrada ===
    try:
        df_dom, df_int, df_clients, df_arms = cargar_archivos()
    except Exception as e:
        raise RuntimeError(f"Error al leer los archivos: {e}")
    
    # === Generación de la hoja "total" del archivo de control interno ===
    df_total = generar_page_total(df_dom, df_int, COLUMNAS_TOTAL)

    # === Generación de la hoja "total por liquidación" del archivo de control interno ===
    df_total_per_liq = generar_page_total_per_liq(df_total, tipo_cambio)

    # === VALIDACIÓN CONTRA ARCHIVO ARMS ===
    validar_y_comparar_con_arms(df_total_per_liq)
    
    # === Exportar archivo Excel final con ambas hojas ===}
    path_salida = PATH_SALIDA
   
    return exportar_control_interno(df_total, df_total_per_liq,path_salida)
    
    
    
