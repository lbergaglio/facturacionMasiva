import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# Diccionario para guardar rutas
archivos_cargados = {
    "liq_dom_pbi": None,
    "liq_int_pbi": None,
    "clients_pbi": None,
    "liq_arms": None
}

# Diccionario para mostrar nombres legibles
labels_titulos = {
    "liq_dom_pbi": "Liquidaciones domésticas PBI",
    "liq_int_pbi": "Liquidaciones internacionales PBI",
    "clients_pbi": "Clientes Maestros",
    "liq_arms": "Liquidaciones ARMS"
}

# ---------- Funciones ----------
def cargar_archivo(label_destino, clave):
    ruta = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xls *.xlsx")])
    if ruta:
        extension = os.path.splitext(ruta)[1].lower()
        if extension not in [".xls", ".xlsx"]:
            messagebox.showerror("Formato inválido", "El archivo debe ser .xls o .xlsx")
            return
        label_destino.config(text=ruta)
        archivos_cargados[clave] = ruta

def generar_archivo():
    faltantes = [k for k, v in archivos_cargados.items() if v is None]

    tipo_cambio = entry_tipo_cambio.get().strip()
    if not tipo_cambio:
        messagebox.showwarning("Campo requerido", "Debe ingresar un tipo de cambio.")
        return

    try:
        tipo_cambio_float = float(tipo_cambio)
    except ValueError:
        messagebox.showerror("Valor inválido", "El tipo de cambio debe ser un número.")
        return

    if faltantes:
        mensaje = "Faltan cargar los siguientes archivos:\n"
        mensaje += "\n".join(f"- {labels_titulos[k]}" for k in faltantes)
        messagebox.showwarning("Archivos faltantes", mensaje)
    else:
        # Acá iría tu lógica real de generación
        messagebox.showinfo("Éxito", f"¡Todo cargado correctamente!\nTipo de cambio: {tipo_cambio_float}")
        # Por ejemplo, podrías pasar los archivos_cargados y tipo_cambio_float a una función que procese los archivos

def crear_fila(root, texto_titulo, clave):
    frame = tk.Frame(root, bg="#242c50")
    frame.pack(pady=10, padx=30, anchor="w")

    titulo = tk.Label(frame, text=texto_titulo, width=30, anchor="w", bg="#242c50", font=("Arial", 10,"bold"), fg="#ffffff")
    titulo.pack(side="left")

    label_ruta = tk.Label(frame, text="No se seleccionó archivo", bg="#ffffff", width=50, anchor="w", relief="sunken")
    label_ruta.pack(side="left", padx=5)

    boton = tk.Button(frame, text="Cargar archivo", command=lambda: cargar_archivo(label_ruta, clave))
    boton.pack(side="left", padx=5)

    return label_ruta

# ---------- Ventana principal ----------
root = tk.Tk()
root.title("App Automatización de Facturas")
root.geometry("800x450")
root.configure(bg="#242c50")

# ------------------ Logo ------------------
imagen_original = Image.open("logo_eana.png")
imagen_redimensionada = imagen_original.resize((450, 50))
imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)
label_imagen = tk.Label(root, image=imagen_tk, bg="#242c50")
label_imagen.pack(pady=10)

# ---------- Crear filas de carga ----------
crear_fila(root, "Liquidaciones domésticas PBI:", "liq_dom_pbi")
crear_fila(root, "Liquidaciones internacionales PBI:", "liq_int_pbi")
crear_fila(root, "Clientes Maestros:", "clients_pbi")
crear_fila(root, "Liquidaciones ARMS:", "liq_arms")

# ---------- Tipo de cambio ----------
frame_tipo_cambio = tk.Frame(root, bg="#242c50")
frame_tipo_cambio.pack(pady=20, padx=30, anchor="w")

label_tipo_cambio = tk.Label(frame_tipo_cambio, text="Tipo de cambio utilizado:", width=30, anchor="w", bg="#242c50", font=("Arial", 10, "bold"), fg="#ffffff")
label_tipo_cambio.pack(side="left")

entry_tipo_cambio = tk.Entry(frame_tipo_cambio, width=20)
entry_tipo_cambio.pack(side="left", padx=5)

# ---------- Botón para generar ----------
btn_generar = tk.Button(root, text="Generar archivos", font=("Arial", 11, "bold"), bg="#27ae60", fg="white", command=generar_archivo)
btn_generar.pack(pady=30)

root.mainloop()
