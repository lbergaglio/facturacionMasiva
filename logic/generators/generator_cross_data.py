import pandas as pd
import os
from datetime import datetime
from gui.components import archivos_cargados
from logic.parse_inputs import cargar_archivos
import tkinter.messagebox as messagebox
from logic.exporter import exportar_control_interno
from logic.generators.generator_total import generate_page_total
from logic.generators.generator_total_per_liq import generate_page_total_per_liq
from logic.validators.validator_arms import validar_y_comparar_con_arms
from logic.generators.generator_balance_liq import generate_page_balance_liq
from logic.generators.generator_summary import generate_page_summary
from logic.generators.generator_tesoreria import generate_page_tesoreria
from logic.generators.generator_masive_import import generate_masive_import


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

def generar_control_interno(tipo_cambio,callback_progress):
     # === Lectura de archivos de entrada ===
    try:
        df_dom, df_int, df_clients, df_arms = cargar_archivos()
        # === Generación de la hoja "total" del archivo de control interno ===
        df_total = generate_page_total(df_dom, df_int, COLUMNAS_TOTAL)
        callback_progress("✅ Cruzando archivos... (45%)")

        # === Generación de la hoja "total por liquidación" del archivo de control interno ===
        df_total_per_liq = generate_page_total_per_liq(df_total, tipo_cambio)
        callback_progress("✅ Cruzando archivos... (50%)")

        # === VALIDACIÓN CONTRA ARCHIVO ARMS ===
        df_diff_arms = validar_y_comparar_con_arms(df_total_per_liq,df_arms)
        callback_progress("✅ Cruzando archivos... (55%)")

        # === Generación de Balance de Liquidaciones por Moneda y Tipo de Cliente ===
        df_balance = generate_page_balance_liq(df_total)
        callback_progress("✅ Cruzando archivos... (65%)")

        # === Generación de Resumen de Facturación ===
        df_summary = generate_page_summary(df_total)
        callback_progress("✅ Cruzando archivos... (75%)")

        # === Generación de Tesorería ===
        df_tesoreria = generate_page_tesoreria(df_total,df_clients)
        callback_progress("✅ Cruzando archivos... (90%)")

        # === Generación de Importación Masiva ===
        df_masive_import = generate_masive_import(df_total, df_total_per_liq, df_clients, tipo_cambio)
        callback_progress("✅ Cruzando archivos... (95%)")
        
        # === Exportar archivo Excel final con ambas hojas ===}
        return exportar_control_interno(df_total, df_total_per_liq,df_balance,df_summary,df_tesoreria,df_diff_arms,df_masive_import,PATH_SALIDA)

    except Exception as e:
        raise RuntimeError(f"Error al leer los archivos: {e}")
    
    
   
    
    
    
    
