from tkinter import messagebox

def validate_last_invoice_number(df,last_number):
    first_invoice_number_str = df['Número de Liquidacion'].min()
    first_invoice_number_str=first_invoice_number_str.replace("Liq", "00", case=False, regex=True)
    first_invoice_number_float = float(first_invoice_number_str)
    if last_number == first_invoice_number_float-1: 
        messagebox.showinfo("Valido","Numeración validada")
        return True
    else:
        messagebox.showerror("Error", "El último número de liquidación no es el esperado")
        return False