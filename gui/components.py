import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkcalendar import DateEntry
from config.settings import labels_titulos, COLOR_FONDO, COLOR_BOTON
from datetime import datetime

archivos_cargados = {k: None for k in labels_titulos.keys()}

def solicitar_credenciales_api(texto):
    ventana = tk.Toplevel()
    ventana.title(texto)
    ventana.geometry("300x170")
    ventana.configure(bg=COLOR_FONDO)
    ventana.resizable(False, False)
    ventana.grab_set()  # bloquea interacción con la ventana principal

    tk.Label(ventana, font=("Arial", 10, "bold"),bg=COLOR_FONDO, fg="#ffffff", text="Usuario:").pack(pady=(10, 0))
    entry_user = tk.Entry(ventana, width=30)
    entry_user.pack()

    tk.Label(ventana, font=("Arial", 10, "bold"),bg=COLOR_FONDO, fg="#ffffff", text="Contraseña:").pack(pady=5)
    entry_pass = tk.Entry(ventana, width=30, show="*")
    entry_pass.pack()

    resultado = {"usuario": None, "contraseña": None}

    def confirmar():
        username = entry_user.get().strip()
        password = entry_pass.get().strip()
        if not username or not password:
            messagebox.showwarning("Faltan datos", "Debe ingresar usuario y contraseña.")
        else:
            resultado["usuario"] = username
            resultado["contraseña"] = password
            ventana.destroy()

    tk.Button(ventana, text="Aceptar", bg=COLOR_BOTON, fg="white", font=("Arial", 11, "bold"), command=confirmar).pack(pady=10)
    ventana.wait_window()  # espera a que la ventana se cierre

    return resultado["usuario"], resultado["contraseña"]

def crear_fila_fecha_desde_hasta(root, texto_titulo, clave_desde, clave_hasta, bg_color):
    frame = tk.Frame(root, bg=bg_color)
    frame.pack(pady=10, padx=30, anchor="w")

    titulo = tk.Label(frame, text=texto_titulo, width=30, anchor="w", bg=bg_color, font=("Arial", 10, "bold"), fg="#ffffff")
    titulo.pack(side="left")

    entry_desde = DateEntry(
        frame,
        width=12,
        background='darkblue',
        foreground='white',
        borderwidth=2,
        date_pattern='yyyy-mm-dd'
    )
    entry_desde.pack(side="left", padx=(5, 0))

    entry_hasta = DateEntry(
        frame,
        width=12,
        background='darkblue',
        foreground='white',
        borderwidth=2,
        date_pattern='yyyy-mm-dd'
    )
    entry_hasta.pack(side="left", padx=(5, 10))

    archivos_cargados[clave_desde] = entry_desde.get_date().strftime("%Y-%m-%d")
    archivos_cargados[clave_hasta] = entry_hasta.get_date().strftime("%Y-%m-%d")

    def guardar_fechas(_=None):
        fecha_desde = entry_desde.get_date().strftime("%Y-%m-%d")
        fecha_hasta = entry_hasta.get_date().strftime("%Y-%m-%d")
        archivos_cargados[clave_desde] = fecha_desde
        archivos_cargados[clave_hasta] = fecha_hasta

    entry_desde.bind("<<DateEntrySelected>>", guardar_fechas)
    entry_hasta.bind("<<DateEntrySelected>>", guardar_fechas)

    return entry_desde, entry_hasta



def cargar_archivo(label_destino, clave):
    ruta = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xls *.xlsx"),("Archivos CSV", "*.csv")])
    if ruta and ruta.lower().endswith((".xls", ".xlsx", ".csv")):
        label_destino.config(text=ruta)
        archivos_cargados[clave] = ruta
    else:
        from tkinter import messagebox
        messagebox.showerror("Formato inválido", "Debe seleccionar un archivo .xls o .xlsx")

def crear_fila(root, texto_titulo, clave, bg_color):
    frame = tk.Frame(root, bg=bg_color)
    frame.pack(pady=10, padx=30, anchor="w")

    titulo = tk.Label(frame, text=texto_titulo, width=30, anchor="w", bg=bg_color, font=("Arial", 10,"bold"), fg="#ffffff")
    titulo.pack(side="left")

    label_ruta = tk.Label(frame, text="No se seleccionó archivo", bg="#ffffff", width=50, anchor="w", relief="sunken")
    label_ruta.pack(side="left", padx=5)

    boton = tk.Button(frame, text="Cargar archivo", command=lambda: cargar_archivo(label_ruta, clave))
    boton.pack(side="left", padx=5)

    return label_ruta
