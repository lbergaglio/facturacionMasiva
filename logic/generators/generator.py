from tkinter import messagebox
import threading
from config.settings import labels_titulos
from gui.components import archivos_cargados, solicitar_credenciales_api
from logic.validators.validator_api_zeus import validate_completed_clients
from logic.validators.validator_main import validar_headers_excel
from logic.generators.generator_cross_data import generar_control_interno  # importa el generador

TIPO_MAPEO = {"clients_zeus": "clientes_maestros"}

MANDATORY_COLUMNS = ["CodigoZeus", "Descripcion", "LocalidadId", "ProvinciaId", 
                     "SituaciónIvaId", "CondicionVenta", "ListaPrecioId"]



def validate_completed_columns(df, columns):
    incomplete = []

    for col in columns:
        if col not in df.columns:
            incomplete.append(f"❌ Columna faltante: {col}")
        else:
            # Verifica que no haya ni NaN ni cadenas vacías o con espacios
            if df[col].isnull().any() or (df[col].astype(str).str.strip() == "").any():
                incomplete.append(f"⚠️ Valores vacíos en columna: {col}")
    return incomplete

def validar_y_generar(tipo_cambio_str, start_date, end_date, callback_progress=None):
    faltantes = [k for k, v in archivos_cargados.items() if v is None]

    if not tipo_cambio_str:
        messagebox.showwarning("Campo requerido", "Debe ingresar un tipo de cambio.")
        return

    try:
        tipo_cambio_float = float(tipo_cambio_str)
    except ValueError:
        messagebox.showerror("Valor inválido", "El tipo de cambio debe ser un número.")
        return

    if faltantes:
        mensaje = "Faltan cargar los siguientes archivos:\n"
        mensaje += "\n".join(f"- {labels_titulos[k]}" for k in faltantes)
        messagebox.showwarning("Archivos faltantes", mensaje)
        return

    # Validación de headers
    for tipo_gui, archivo in archivos_cargados.items():
        if callback_progress:
            callback_progress("✅ Validando archivos... (10%)")
        if archivo:
            tipo_validacion = TIPO_MAPEO.get(tipo_gui, tipo_gui)
            valido, mensaje = validar_headers_excel(archivo, tipo_validacion)
            if not valido:
                messagebox.showerror("Error de validación", f"{labels_titulos[tipo_gui]}: {mensaje}")
                return

    # Validación de columnas obligatorias
    missing_columns = validate_completed_columns(df_clients_zeus, MANDATORY_COLUMNS)
    if missing_columns:
        errores = "\n".join(missing_columns)
        messagebox.showerror("Advertencia", f"Se encontraron columnas incompletas en el archivo de clientes:\n{errores}")
        return

    # Solicitar credenciales
    if callback_progress:
        callback_progress("✅ Validando credenciales... (20%)")

    username, password = solicitar_credenciales_api("Autenticación ARMS API")
    if not username or not password:
        messagebox.showerror("Error", "No se ingresaron credenciales. Proceso cancelado.")
        return

    # Generar archivo
    try:
        if callback_progress:
            callback_progress("✅ Generando archivo... (25%)")

        path_salida, _ = generar_control_interno(
            username,
            password,
            tipo_cambio_float,
            callback_progress,
            start_date,
            end_date
        )

        messagebox.showinfo("Éxito", f"Archivo de control interno generado:\n{path_salida}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el archivo de control interno:\n{str(e)}")
