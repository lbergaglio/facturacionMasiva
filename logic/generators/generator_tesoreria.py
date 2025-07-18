import pandas as pd
import unicodedata

def limpiar_columna(col):
    col = col.strip()
    col = unicodedata.normalize('NFKD', col).encode('ascii', 'ignore').decode('utf-8')
    col = col.lower()
    return col

def generate_page_tesoreria(df_total, df_clients):
    # Normalizar nombres de columnas
    df_total.columns = [limpiar_columna(c) for c in df_total.columns]
    df_clients.columns = [limpiar_columna(c) for c in df_clients.columns]

    # Validar columnas necesarias
    columnas_necesarias = ['numero de liquidacion', 'cliente', 'moneda de liquidacion', 'monto', 'tasa', 'fecha de liquidacion']
    for col in columnas_necesarias:
        if col not in df_total.columns:
            raise KeyError(f"Falta la columna '{col}' en df_total. Columnas actuales: {df_total.columns.tolist()}")

    alias_map = dict(zip(df_clients['name'], df_clients['alias']))
    rows = []

    for (num_liq, cliente), grupo in df_total.groupby(['numero de liquidacion', 'cliente']):
        fila = {
            'Alias': alias_map.get(cliente, ''),
            'Razon Social': cliente,
            'Número de Liquidación': num_liq,
            'TOTAL ARS': grupo.loc[grupo['moneda de liquidacion'] == 'ARS', 'monto'].sum(),
            'TOTAL USD': grupo.loc[grupo['moneda de liquidacion'] == 'USD', 'monto'].sum(),
            'AA DOM': grupo.loc[grupo['tasa'] == 'AAN', 'monto'].sum(),
            'AA INT': grupo.loc[grupo['tasa'] == 'AAI', 'monto'].sum(),
            'PV DOM': grupo.loc[grupo['tasa'] == 'PVN', 'monto'].sum(),
            'PV INT': grupo.loc[grupo['tasa'] == 'PVI', 'monto'].sum(),
            'SNA DOM': grupo.loc[grupo['tasa'] == 'EXT', 'monto'].sum(),
            'SNA INT': grupo.loc[grupo['tasa'] == 'EXTI', 'monto'].sum(),
            'EMISIÓN': grupo['fecha de liquidacion'].iloc[0],
            'SERVICIO': grupo['fecha de liquidacion'].iloc[0],
            'ENVIO MAIL': '',
            'FECHA DE VENCIMIENTO':''
        }
        rows.append(fila)

    df_resultado = pd.DataFrame(rows)
    columnas = [
        'Alias', 'Razon Social', 'Número de Liquidación',
        'TOTAL ARS', 'TOTAL USD',
        'AA DOM', 'AA INT',
        'PV DOM', 'PV INT',
        'SNA DOM', 'SNA INT',
        'EMISIÓN', 'SERVICIO', 
        'ENVIO MAIL', 'FECHA DE VENCIMIENTO'
    ]
    df_resultado = df_resultado[columnas]

    return df_resultado
