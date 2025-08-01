import pyodbc
import pandas as pd
from gui.components import solicitar_credenciales_api

TITULO = "Credenciales para Portal Clientes"

def get_connection(username,password):
    return pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=CPW-ARSAT-VDB02;'
        'DATABASE=eana;'
        f'UID={username};'
        f'PWD={password};'
        'TrustServerCertificate=yes;'
    )

def get_billing_and_due_date(invoice_number_list):
    print("LLEGUE")
    username, password = solicitar_credenciales_api(TITULO)
    conn = get_connection(username,password)
    cursor = conn.cursor()
    missing_invoice_number = []
    df_billing_and_due_date = pd.DataFrame(columns=['numero de liquidacion', 'fecha de emision', 'fecha de vencimiento'])
    for invoice_number in invoice_number_list:
        cursor.execute("SELECT nro_liquidacion, fecha_liquidacion ,fecha_vencimiento FROM dbo.liquidacion WHERE nro_liquidacion = ?", invoice_number)
        row = cursor.fetchone()
        if row:
            df_billing_and_due_date.loc[len(df_billing_and_due_date)] = [row[0], row[1],row[2]]
        else:
            print(f"No se encontró la factura {invoice_number}")
            missing_invoice_number.append(invoice_number)
        
    # Cerrar conexión
    #print(missing_invoice_number)
    #print(df_billing_and_due_date)
    cursor.close()
    conn.close()
    return df_billing_and_due_date, missing_invoice_number



