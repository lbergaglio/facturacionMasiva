# main.py
import tkinter as tk
from PIL import Image, ImageTk
from config import COLOR_FONDO, COLOR_BOTON
from gui_components import crear_fila
from logic import validar_y_generar

root = tk.Tk()
root.title("App Automatización de Facturas")
root.geometry("800x450")
root.configure(bg=COLOR_FONDO)

# Logo
imagen = Image.open("assets/logo_eana.png").resize((450, 50))
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

root.mainloop()
