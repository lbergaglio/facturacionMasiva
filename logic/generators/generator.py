from tkinter import messagebox
import threading
from config.settings import labels_titulos
from gui.components import archivos_cargados, solicitar_credenciales_api
from logic.validators.validator_api_zeus import validate_completed_clients
from logic.generators.generator_cross_data import generar_control_interno

def validate_exchange_rate(exchange_rate):
    # Si no hay un tipo de cambio cargado, se solicita ingreso del mismo.
    if not exchange_rate:
        messagebox.showwarning("Campo requerido", "Debe ingresar un tipo de cambio.")
        return
    
    # Valdación del tipo de cambio ingresado
    try:
        tipo_cambio_float = float(exchange_rate)
        return tipo_cambio_float
    except ValueError:
        messagebox.showerror("Valor inválido", "El tipo de cambio debe ser un número.")
        return



# Validador y generador de datos
def validar_y_generar(tipo_cambio_str, start_date, end_date, callback_progress=None):
    faltantes = [k for k, v in archivos_cargados.items() if v is None]
    
    # Valido el tipo de cambio y se transforma de "string" a "float"
    if validate_exchange_rate(tipo_cambio_str):
        tipo_cambio_float = validate_exchange_rate(tipo_cambio_str)
    else: return 

    # Generación del archivo de control interno
    try:
        # Solcito credenciales de API Zeus
        username, password = solicitar_credenciales_api("Autenticacíon ZEUS API")
        
        if not username or not password:
            messagebox.showerror("Error", "No se ingresaron credenciales. Proceso cancelado.")
            return
        
        callback_progress("✅ Validando credenciales... (20%)")

        # Validación de clientes completos
        is_clients_zeus_completed, df_clientes_zeus = validate_completed_clients(username, password)

        if is_clients_zeus_completed:
            messagebox.showerror("Advertencia", "Se encontraron clientes incompletos. El archivo de control interno no se generó.")
            return
        else:
            callback_progress("✅ Credenciales validadas... (25%)")
            path_salida, _ = generar_control_interno(username,password,tipo_cambio_float,callback_progress,df_clientes_zeus,start_date, end_date)
            messagebox.showinfo("Éxito", f"Archivo de control interno generado:\n{path_salida}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el archivo de control interno:\n{str(e)}")

