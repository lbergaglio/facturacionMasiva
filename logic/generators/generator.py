from tkinter import messagebox
from config.settings import labels_titulos
from gui.components import archivos_cargados
from logic.validators.validator_main import validar_headers_excel
from logic.generators.generator_cross_data import generar_control_interno  # importa el generador

TIPO_MAPEO = {
    "liq_dom_pbi": "powerbi_domestico",
    "liq_int_pbi": "powerbi_internacional",
    "clients_pbi": "clientes_maestros",
    "liq_arms": "liquidaciones_arms"
}

def validar_y_generar(tipo_cambio_str):
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
        if archivo:
            tipo_validacion = TIPO_MAPEO.get(tipo_gui, tipo_gui)
            valido, mensaje = validar_headers_excel(archivo, tipo_validacion)
            if not valido:
                messagebox.showerror("Error de validación", f"{labels_titulos[tipo_gui]}: {mensaje}")
                return
    
    # Generación del archivo de control interno
    try:
        path_salida, _ = generar_control_interno(tipo_cambio_float)
        messagebox.showinfo("Éxito", f"Archivo de control interno generado:\n{path_salida}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el archivo de control interno:\n{str(e)}")
