import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk

def cargar_archivo(label_destino):
    ruta = filedialog.askopenfilename()
    if ruta:
        label_destino.config(text=ruta)

def generar_archivo():
    # Lógica de generación (a completar)
    messagebox.showinfo("Éxito", "¡Archivo generado!")

# ---------- Función para crear filas ----------
def crear_fila(root, texto_titulo):
    frame = tk.Frame(root, bg="#242c50")
    frame.pack(pady=10, padx=30, anchor="w")
    
    titulo = tk.Label(frame, text=texto_titulo, width=30, anchor="w", bg="#242c50", font=("Arial", 10,"bold"), fg="#ffffff")
    titulo.pack(side="left")
    
    label_ruta = tk.Label(frame, text="No se seleccionó archivo", bg="#ffffff", width=50, anchor="w", relief="sunken")
    label_ruta.pack(side="left", padx=5)
    
    boton = tk.Button(frame, text="Cargar archivo", command=lambda: cargar_archivo(label_ruta))
    boton.pack(side="left", padx=5)
    
    return label_ruta

root = tk.Tk()
root.title("App Automatización de Facturas")
root.geometry("800x350")
root.configure(bg="#242c50")

# ------------------ Logo ------------------
imagen_original = Image.open("logo_eana.png")
imagen_redimensionada = imagen_original.resize((450, 50))
imagen_tk = ImageTk.PhotoImage(imagen_redimensionada)

label_imagen = tk.Label(root, image=imagen_tk, bg="#242c50")
label_imagen.pack(pady=10)

# ---------- Crear filas de carga ----------
label_liq_dom_pbi = crear_fila(root, "Liquidaciones domésticas PBI:")
label_liq_int_pbi = crear_fila(root, "Liquidaciones internacionales PBI:")
label_clients_pbi = crear_fila(root, "Clientes Maestros:")
label_liq_arms     = crear_fila(root, "Liquidaciones ARMS:")

# ---------- Botón para generar ----------
btn_generar = tk.Button(root, text="Generar archivos", font=("Arial", 11, "bold"), bg="#27ae60", fg="white", command=generar_archivo)
btn_generar.pack(pady=30)

root.mainloop()
