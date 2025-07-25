import tkinter as tk
from PIL import Image, ImageTk
from config.settings import COLOR_FONDO, COLOR_BOTON, DIMENSION_GRAFICA, TITULO_APP, URL_LOGO, URL_ICONO, DIMENSION_ICONO_ALTO, DIMENSION_ICONO_ANCHO, DIMENSION_LOGO_ALTO, DIMENSION_LOGO_ANCHO
from gui.components import crear_fila, crear_fila_fecha_desde_hasta
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

#Campo fecha desde y hasta
entry_desde,entry_hasta = crear_fila_fecha_desde_hasta(root, "Fecha desde:", "start_date", "end_date", COLOR_FONDO)

# Campo de selección de archivos
crear_fila(root, "Archivo clientes:", "clients_zeus", COLOR_FONDO)

#print("Fecha desde:", entry_desde.get_date())
#print("Fecha hasta:", entry_hasta.get_date())

# Campo tipo de cambio
frame_tc = tk.Frame(root, bg=COLOR_FONDO)
frame_tc.pack(pady=10, padx=20, anchor="w")

tk.Label(frame_tc, text="Tipo de cambio utilizado:", width=25, anchor="w",
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
            validar_y_generar(entry_tipo_cambio.get(), entry_desde.get_date(),entry_hasta.get_date(), callback_progress=update_progress)
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
