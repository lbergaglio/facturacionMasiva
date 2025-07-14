import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from config.settings import labels_titulos

archivos_cargados = {k: None for k in labels_titulos.keys()}

def solicitar_credenciales_api():
    ventana = tk.Toplevel()
    ventana.title("Autenticación Zeus API")
    ventana.geometry("300x170")
    ventana.resizable(False, False)
    ventana.grab_set()  # bloquea interacción con la ventana principal

    tk.Label(ventana, text="Usuario:").pack(pady=(10, 0))
    entry_user = tk.Entry(ventana, width=30)
    entry_user.pack()

    tk.Label(ventana, text="Contraseña:").pack(pady=5)
    entry_pass = tk.Entry(ventana, width=30, show="*")
    entry_pass.pack()

    resultado = {"usuario": None, "contraseña": None}

    def confirmar():
        user = entry_user.get().strip()
        pw = entry_pass.get().strip()
        if not user or not pw:
            messagebox.showwarning("Faltan datos", "Debe ingresar usuario y contraseña.")
        else:
            resultado["usuario"] = user
            resultado["contraseña"] = pw
            ventana.destroy()

    tk.Button(ventana, text="Aceptar", command=confirmar).pack(pady=10)
    ventana.wait_window()  # espera a que la ventana se cierre

    return resultado["usuario"], resultado["contraseña"]


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
