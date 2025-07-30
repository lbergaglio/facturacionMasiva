import pandas as pd
import os
from datetime import datetime
from gui.components import archivos_cargados
import tkinter.messagebox as messagebox
from logic.parse_inputs import cargar_archivos
from logic.exporter import exportar_control_interno
from logic.api_access.api_arms_df import generate_total_and_clients

from logic.validators.validator_invoice_number import validate_last_invoice_number
#from logic.validators.validator_arms import validar_y_comparar_con_armss
#from logic.validators.validator_api_zeus import validate_completed_columns

from logic.generators.generator_total_per_liq import generate_page_total_per_liq
from logic.generators.generator_balance_liq import generate_page_balance_liq
from logic.generators.generator_summary import generate_page_summary
from logic.generators.generator_tesoreria import generate_page_tesoreria
from logic.generators.generator_masive_import import generate_masive_import


# Ruta de salida para el archivo generado
PATH_SALIDA = "salida/control_interno.xlsx"

TIPO_MAPEO = {"clients_zeus": "clientes_maestros"}

def validar_dataframe(archivo):
    df = pd.read_excel(archivo,skiprows=6)


def generar_control_interno(tipo_cambio,last_invoice_number,callback_progress,df_clientes_zeus,start_date,end_date):
     # === Lectura de archivos de entrada ===
    try:
        callback_progress("✅ Cargando archivos... (30%)")

        #df_clientes_zeus = cargar_archivos()
        #missing_columns = validate_completed_columns(df_clients_zeus, MANDATORY_COLUMNS)
    
        callback_progress("✅ Cruzando archivos... (35%)")

        # === Generación de la hoja "total" del archivo de control interno ===
        df_total,df_clients = generate_total_and_clients(start_date,end_date, tipo_cambio)
        callback_progress("✅ Cruzando archivos... (45%)")

        # === Validar Numeración de Facturas ===
        """if not validate_last_invoice_number(df_total,last_invoice_number):
            callback_progress("❌ Error en la numeración de facturas")
            return False        """

        # === Generación de la hoja "total por liquidación" del archivo de control interno ===
        df_total_per_liq = generate_page_total_per_liq(df_total, tipo_cambio)
        callback_progress("✅ Cruzando archivos... (50%)")

        # === VALIDACIÓN CONTRA ARCHIVO ARMS ===
        #df_diff_arms = validar_y_comparar_con_arms(df_total_per_liq,df_arms)
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
        df_masive_import = generate_masive_import(df_total, df_total_per_liq, df_clients, tipo_cambio, df_clientes_zeus)
        callback_progress("✅ Cruzando archivos... (95%)")
        
        # === Exportar archivo Excel final con ambas hojas ===}
        return exportar_control_interno(df_total, df_total_per_liq,df_balance,df_summary,df_tesoreria,df_masive_import,PATH_SALIDA,callback_progress)

    except Exception as e:
        raise RuntimeError(f"Error al leer los archivos: {e}")
    
    
   
    
    
    
    
