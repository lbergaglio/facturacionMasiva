import tkinter as tk
import time
from PIL import Image, ImageTk
from config.settings import COLOR_FONDO, COLOR_BOTON, DIMENSION_GRAFICA, TITULO_APP, URL_LOGO, URL_ICONO, DIMENSION_ICONO_ALTO, DIMENSION_ICONO_ANCHO, DIMENSION_LOGO_ALTO, DIMENSION_LOGO_ANCHO
from gui.components import crear_fila
from logic.generators.generator import validar_y_generar

root = tk.Tk()
root.title(TITULO_APP)
root.geometry(DIMENSION_GRAFICA)
root.configure(bg=COLOR_FONDO)

# Logo e icono
root.resizable(False, False)
imagen = Image.open(URL_LOGO).resize((DIMENSION_LOGO_ANCHO, DIMENSION_LOGO_ALTO))
icono = Image.open(URL_ICONO).resize((DIMENSION_ICONO_ANCHO, DIMENSION_ICONO_ALTO))
root.iconphoto(False, ImageTk.PhotoImage(icono))
imagen_tk = ImageTk.PhotoImage(imagen)
tk.Label(root, image=imagen_tk, bg=COLOR_FONDO).pack(pady=10)

# Campos de carga
crear_fila(root, "Liquidaciones domésticas PBI:", "liq_dom_pbi", COLOR_FONDO)
crear_fila(root, "Liquidaciones internacionales PBI:", "liq_int_pbi", COLOR_FONDO)
crear_fila(root, "Clientes Maestros:", "clients_pbi", COLOR_FONDO)
crear_fila(root, "Liquidaciones ARMS:", "liq_arms", COLOR_FONDO)

# Campo tipo de cambio
frame_tc = tk.Frame(root, bg=COLOR_FONDO)
frame_tc.pack(pady=20, padx=30, anchor="w")

tk.Label(frame_tc, text="Tipo de cambio utilizado:", width=30, anchor="w",
         bg=COLOR_FONDO, font=("Arial", 10, "bold"), fg="#ffffff").pack(side="left")
entry_tipo_cambio = tk.Entry(frame_tc, width=20)
entry_tipo_cambio.pack(side="left", padx=5)

# Botón generar
btn_generar = tk.Button(root, text="Generar archivos", font=("Arial", 11, "bold"),
                        bg=COLOR_BOTON, fg="white", command=lambda: validar_y_generar(entry_tipo_cambio.get()))
btn_generar.pack(pady=30)

from tkinter import ttk
import threading

# Label de texto de carga
label_spinner = tk.Label(root, text="Procesando, por favor espere...", fg="white", bg=COLOR_FONDO, font=("Arial", 10, "italic"))
label_spinner.pack()
label_spinner.pack_forget()

# Spinner (barra de progreso indeterminada)
spinner = ttk.Progressbar(root, mode='indeterminate', length=200)
spinner.pack(pady=5)
spinner.stop()
spinner.pack_forget()  # Ocultarlo al inicio

def update_progress(texto):
    label_spinner.config(text=texto)
    label_spinner.update_idletasks()


def ejecutar_con_spinner():
    def tarea():
        try:
            validar_y_generar(entry_tipo_cambio.get(), callback_progress=update_progress)
        finally:
            spinner.stop()
            spinner.pack_forget()
            label_spinner.pack_forget()
            btn_generar.config(state="normal")

    spinner.pack(pady=5)
    label_spinner.pack()
    spinner.start()
    btn_generar.config(state="disabled")
    threading.Thread(target=tarea).start()

# Reemplazar el command del botón
btn_generar.config(command=ejecutar_con_spinner)

root.mainloop()
