import pandas as pd
import tkinter.messagebox as messagebox
from gui.components import archivos_cargados

def validar_y_comparar_con_arms(df_total_per_liq):
    try:
        df_arms_original = pd.read_csv(archivos_cargados['liq_arms'])

        # === Renombrar columnas del archivo generado para coincidir con ARMS ===
        df_total_per_liq_comparacion = df_total_per_liq.copy()
        df_total_per_liq_comparacion.columns = [
            'Account', 'Invoice Number', 'Invoice Date', 'Invoice Type', 'Status', 'Payment Due Date',
            'Created By', 'Invoice Amount', 'Invoice Currency', 'Exchange Rate To USD',
            'Invoice Date Of Issue', 'Proforma', 'Exported', 'Billing Centre'
        ]
        
        # === Excluir de la validación los registros Non-Aviation ===
        df_total_per_liq_comparacion = df_total_per_liq_comparacion[df_total_per_liq_comparacion['Invoice Type'].str.upper() != 'NON-AVIATION']

        # === Eliminar columna "Created By" para la comparación ===
        df_total_per_liq_comparacion.drop(columns=['Created By'], inplace=True)
        if 'Created By' in df_arms_original.columns:
            df_arms_original.drop(columns=['Created By'], inplace=True)
        
        df_total_per_liq_comparacion.drop(columns=['Exchange Rate To USD'], inplace=True)
        if 'Exchange Rate To USD' in df_arms_original.columns:
            df_arms_original.drop(columns=['Exchange Rate To USD'], inplace=True)

        # === Convertir fechas a datetime.date para ambos ===
        fecha_cols = ['Invoice Date', 'Payment Due Date', 'Invoice Date Of Issue']
        for col in fecha_cols:
            if col in df_arms_original.columns:
                df_arms_original[col] = pd.to_datetime(df_arms_original[col], errors='coerce').dt.date
            if col in df_total_per_liq_comparacion.columns:
                df_total_per_liq_comparacion[col] = pd.to_datetime(df_total_per_liq_comparacion[col], errors='coerce').dt.date

        # === Normalizar strings ===
        for col in df_total_per_liq_comparacion.columns:
            if df_total_per_liq_comparacion[col].dtype == 'object':
                df_total_per_liq_comparacion[col] = df_total_per_liq_comparacion[col].astype(str).str.strip().str.upper()
        for col in df_arms_original.columns:
            if df_arms_original[col].dtype == 'object':
                df_arms_original[col] = df_arms_original[col].astype(str).str.strip().str.upper()
        
        # === Forzar que Proforma y Exportado sean string en minúsculas y sin espacios ===
        for col in ['Proforma', 'Exported']:
            if col in df_total_per_liq_comparacion.columns:
                df_total_per_liq_comparacion[col] = df_total_per_liq_comparacion[col].astype(str).str.strip().str.lower()
            if col in df_arms_original.columns:
                df_arms_original[col] = df_arms_original[col].astype(str).str.strip().str.lower()


        # === Normalizar valores numéricos ===
        for col in ['Invoice Amount', 'Exchange Rate To USD']:
            if col in df_total_per_liq_comparacion.columns:
                df_total_per_liq_comparacion[col] = pd.to_numeric(df_total_per_liq_comparacion[col], errors='coerce').round(2)
            if col in df_arms_original.columns:
                df_arms_original[col] = pd.to_numeric(df_arms_original[col], errors='coerce').round(2)

        # === Ordenar y comparar ===
        df_total_per_liq_comparacion.sort_values(by="Invoice Number", inplace=True)
        df_arms_original.sort_values(by="Invoice Number", inplace=True)
        df_total_per_liq_comparacion.reset_index(drop=True, inplace=True)
        df_arms_original.reset_index(drop=True, inplace=True)

        # Comparar fila a fila
        diferencias = df_total_per_liq_comparacion.ne(df_arms_original[df_total_per_liq_comparacion.columns])
        filas_con_diferencias = diferencias.any(axis=1)

        if filas_con_diferencias.any():
            df_diff = pd.DataFrame({
                'Número de Liquidación': df_total_per_liq_comparacion.loc[filas_con_diferencias, 'Invoice Number'],
                'Diferencias': [
                    ", ".join(df_total_per_liq_comparacion.columns[diferencias.iloc[i]])
                    for i in df_total_per_liq_comparacion.index[filas_con_diferencias]
                ]
            })
            diff_path = f"salida/diferencias_con_arms.xlsx"
            df_diff.to_excel(diff_path, index=False)
            messagebox.showwarning("Advertencia", f"❌ El archivo generado no coincide con el archivo ARMS. Revisar diferencias: {diff_path}")
        else:
            messagebox.showinfo("Validación exitosa", "✅ El archivo generado coincide exactamente con el archivo ARMS.")

    except Exception as e:
        messagebox.showwarning("Advertencia", f"No se pudo comparar con el archivo ARMS: {e}")

    return 