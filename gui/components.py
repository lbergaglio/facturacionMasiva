import tkinter as tk
from tkinter import filedialog
from config.settings import labels_titulos

archivos_cargados = {k: None for k in labels_titulos.keys()}

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
