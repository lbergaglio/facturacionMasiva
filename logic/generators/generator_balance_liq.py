import pandas as pd

def generate_balance_liq(df_total):
    # Verificar que las columnas necesarias existan
    required_cols = ['Moneda de Liquidación', 'Tipo Cliente', 'Monto']
    for col in required_cols:
        if col not in df_total.columns:
            raise ValueError(f"Falta la columna requerida: {col}")

    # Crear tabla dinámica
    df_balance = pd.pivot_table(
        df_total,
        values='Monto',
        index='Tipo Cliente',
        columns='Moneda de Liquidación',
        aggfunc='sum',
        fill_value=0,
        margins=True,
        margins_name='Total general'
    )

    # Reordenar columnas
    cols = ['ARS', 'USD'] if 'ARS' in df_balance.columns and 'USD' in df_balance.columns else df_balance.columns
    df_balance = df_balance[cols]

    return df_balance


    