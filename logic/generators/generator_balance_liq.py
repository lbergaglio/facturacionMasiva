import pandas as pd

def generate_page_balance_liq(df_total):
    # Verificar columnas necesarias
    required_cols = ['Moneda de Liquidación', 'Tipo Cliente', 'Monto']
    for col in required_cols:
        if col not in df_total.columns:
            raise ValueError(f"Falta la columna requerida: {col}")

    # Crear tabla dinámica con totales
    df_balance = pd.pivot_table(
        df_total,
        values='Monto',
        index='Tipo Cliente',
        columns='Moneda de Liquidación',
        aggfunc='sum',
        fill_value=0
    )

    # Reordenar columnas si existen ambas monedas
    money_col = ['ARS', 'USD']
    ordered_cols = [i for i in money_col if i in df_balance.columns] + [i for i in df_balance.columns if i not in money_col]
    df_balance = df_balance[ordered_cols]

    # Resetear el índice para evitar problemas en Excel
    df_balance = df_balance.reset_index()

    # Asegurar que los nombres de columnas sean strings
    df_balance.columns = df_balance.columns.astype(str)

    # Redondear montos a 2 decimales si son float
    for col in df_balance.select_dtypes(include='number').columns:
        df_balance[col] = df_balance[col].round(2)

    return df_balance
