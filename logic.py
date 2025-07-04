# logic.py
from tkinter import messagebox
from config import labels_titulos
from gui_components import archivos_cargados

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
    else:
        # Lógica de generación real
        messagebox.showinfo("Éxito", f"¡Generando archivo!\nTipo de cambio: {tipo_cambio_float}")
