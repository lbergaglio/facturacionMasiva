from tkinter import messagebox
import threading

import pandas as pd
from config.settings import labels_titulos
from gui.components import archivos_cargados, solicitar_credenciales_api
from logic.parse_inputs import cargar_archivos
#from logic.validators.validator_api_zeus import validate_completed_clients
from logic.validators.validator_main import validar_headers_excel
from logic.generators.generator_cross_data import generar_control_interno  # importa el generador

TIPO_MAPEO = {"clients_zeus": "clientes_maestros"}

MANDATORY_COLUMNS = ["CodigoZeus", "Descripcion", "LocalidadId", "ProvinciaId", 
                     "SituaciónIvaId", "CondicionVenta", "ListaPrecioId"]

NEW_HEADERS = {
    "Clientes.Categorias.CodigoZeus": "Clientes.Categorias.CodigoZeus",
    "Clientes.Categorias.Descripcion": "Clientes.Categorias.Descripcion",
    "CodigoZeus": "codigo_cliente",
    "CondicionVenta": "codigo_condicion_venta",
    "NombreCondVta": "NombreCondVta",
    "CuentaId": "CuentaId",
    "CUIT": "cuit",
    "DepositoId": "codigo_deposito",
    "NombreDeposito":"NombreDeposito",
    "Descripcion": "razon_social",
    "DetalleAeronave": "DetalleAeronave",
    "Domicilio": "Domicilio",
    "Fantasía": "nombre_fantasia",
    "IdCliente": "IdCliente",
    "ListaPrecioId": "lista_precio",
    "NombreLista": "NombreLista",
    "LocalidadId": "codigo_localidad",
    "NombreLocalidad": "NombreLocalidad",
    "PaisId":"PaisId",
    "NombrePais": "NombrePais", 
    "ProvinciaId": "codigo_provincia",
    "NombreProvincia":" NombreProvincia",
    "SituaciónIvaId": "codigo_iva",
    "DescripcionIVA": "DescripcionIVA",
    "Email": "email",
    "Activo": "Activo",
}


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


def validate_generate_dataframe(df, columns):
    #df = pd.read_excel(archivo, skiprows=6)
    print("Columnas disponibles:", df.columns)
    missing_columns = validate_completed_columns(df, columns)
    if missing_columns:
        errores = "\n".join(missing_columns)
        messagebox.showerror("Advertencia", f"Se encontraron columnas incompletas en el archivo:\n{errores}")
        dfrenamed = df.rename(columns=NEW_HEADERS)
        print("DF_RENAMED:",dfrenamed)
        return dfrenamed, missing_columns
    else:
        dfrenamed = df.rename(columns=NEW_HEADERS)
        print("DF_RENAMED:",dfrenamed)
        return dfrenamed,missing_columns


def validar_y_generar(tipo_cambio_str, last_invoice_number_str,start_date, end_date, callback_progress=None):
    if not tipo_cambio_str:
        messagebox.showwarning("Campo requerido", "Debe ingresar un tipo de cambio.")
        return

    try:
        tipo_cambio_float = float(tipo_cambio_str)
    except ValueError:
        messagebox.showerror("Valor inválido", "El tipo de cambio debe ser un número.")
        return
    
    if not last_invoice_number_str:
        messagebox.showwarning("Campo requerido", "Debe ingresar el último número de factura.")
        return

    try:
        last_invoice_number_float = float(last_invoice_number_str)
    except ValueError:
        messagebox.showerror("Valor inválido", "El número de factura debe ser un número.")
        return

    # Verificar archivo cargado
    archivo = archivos_cargados.get("clients_zeus")
    if archivo is None:
        messagebox.showwarning("Archivo faltante", "Debe cargar el archivo de Clientes ZEUS.")
        return

    if callback_progress:
        callback_progress("✅ Validando archivo... (10%)")

    valido, mensaje = validar_headers_excel(archivo, "clientes_maestros")
    if not valido:
        messagebox.showerror("Error de validación", f"{labels_titulos['clients_zeus']}: {mensaje}")
        return

    # Leer DataFrame a partir del archivo
    try:
        df = pd.read_excel(archivo, skiprows=6,header=0)
    except Exception as e:
        messagebox.showerror("Error al leer Excel", f"No se pudo leer el archivo Excel:\n{e}")
        return

    df_clientes_zeus, missing_columns = validate_generate_dataframe(df, MANDATORY_COLUMNS)

    #print("DF_CLIENTES_ZEUS_GENERATOR",df_clientes_zeus)

    #if missing_columns:
    #    errores = "\n".join(missing_columns)
    #    messagebox.showerror("Advertencia", f"Se encontraron columnas incompletas en el archivo de clientes:\n{errores}")
    #    return

    # Solicitar credenciales
    if callback_progress:
        callback_progress("✅ Validando credenciales... (20%)")

    """username, password = solicitar_credenciales_api("Autenticación ARMS API")
    if not username or not password:
        messagebox.showerror("Error", "No se ingresaron credenciales. Proceso cancelado.")
        return
"""
    # Generar archivo
    try:
        if callback_progress:
            callback_progress("✅ Generando archivo... (25%)")

        path_salida, _ = generar_control_interno(
            #username,
            #password,
            tipo_cambio_float,
            last_invoice_number_float,
            callback_progress,
            df_clientes_zeus,
            start_date,
            end_date
        )

        messagebox.showinfo("Éxito", f"Archivo de control interno generado:\n{path_salida}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el archivo de control interno:\n{str(e)}")
