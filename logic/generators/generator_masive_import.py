# Generador de Archivo de importación masiva
import pandas as pd
from datetime import datetime
from logic.api_access.api_zeus_df import get_dataframes_from_zeus

MASIVE_IMPORT_MADATORY_COLUMNS = [
    "Pedidos.Código de cliente", "Pedidos.Sucursal", "Pedidos.Punto de venta", "Pedidos.Letra",
    "Pedidos.Código de moneda del comprobante", "Pedidos.Valor de moneda del comprobante", 
    "Pedidos.Códgio de depósito del comprobante", "Pedidos.Código de condición de venta del comprobante",
    "Pedidos.Código de vendedor", "Pedidos.Lista de precios del comprobante", 
    "Pedidos.Exento del comprobante", "Pedidos.Neto gravado del comprobante",
    "pedidos, Total IVA del comprobante", "Pedidos.Porcentaje de IVA en comprobante",
    "Pedidos.Observaciones 1", "Pedidos.Precio total del item", "Pedidos.Código de artículo del item",
    "Pedidos.Cantidad del item", "Pedidos.Código de depósito del item", "Pedidos.Codigo de moneda del item",
    "Pedidos.Valor de moneda del item", "Pedidos.Fecha del comprobante"
]

ARS_CODE = 0
USD_CODE = 2

def fecha_a_clarion(fecha: datetime) -> int:
    base = datetime(1800, 12, 28)
    return (fecha - base).days

def generate_masive_import(df_total, df_total_per_liq, df_clients, tasa_cambio):
    df_clientes_zeus, df_vendedores_zeus, df_parametros_zeus = get_dataframes_from_zeus()

    # Normalizar columnas para evitar errores por espacios o mayúsculas
    for df in [df_total, df_total_per_liq, df_clients, df_clientes_zeus, df_vendedores_zeus, df_parametros_zeus]:
        df.columns = df.columns.str.strip().str.lower()
        print(df.columns)
    


    # Validación de columnas necesarias
    required_columns = {"número de factura", "centro de facturación"}
    missing = required_columns - set(df_total_per_liq.columns)
    if missing:
        raise ValueError(f"Faltan columnas necesarias en df_total_per_liq: {missing}")
    
    # Asignamos la tasa de cambio recibida a cada fila
    df_total["tasa de cambio"] = tasa_cambio
    
    if df_total[df_total["moneda de liquidacion"] == "USD"]["tasa de cambio"].isnull().any():
        raise ValueError("Hay valores nulos en 'tasa de cambio' para filas en USD.")

    # Asegurar tipo string en columnas clave para merge
    df_total["id"] = df_total["id"].astype(str)
    df_clientes_zeus["codigo_cliente"] = df_clientes_zeus["codigo_cliente"].astype(str)

    # Renombrar columnas de df_total_per_liq para el merge correcto
    df_total_per_liq = df_total_per_liq.rename(columns={
        "número de factura": "numero de liquidacion",
        "centro de facturación": "centro de facturacion"
    })

    # Enlaces cruzados
    df_total = df_total.merge(df_clients[["alias"]], how="left", left_on="cliente", right_on="alias")
    df_total = df_total.merge(df_clientes_zeus, how="left", left_on="id", right_on="codigo_cliente")
    df_total = df_total.merge(
    df_total_per_liq[["numero de liquidacion", "centro de facturacion"]],
    on="numero de liquidacion",
    how="left"
    )
    df_total = df_total.merge(df_vendedores_zeus, how="left", left_on="centro de facturacion", right_on="nombre")
    df_total = df_total.merge(df_parametros_zeus, how="left", on="sucursal")

    # Cálculo de campos
    df_total["codigo_moneda"] = df_total["moneda de liquidacion"].map({"ARS": ARS_CODE, "USD": USD_CODE})
    df_total["valor_moneda_item"] = df_total.apply(
        lambda x: 1 if x["moneda de liquidacion"] == "ARS" else x["tasa de cambio"], axis=1
    )
    df_total["monto_pesificado"] = df_total.apply(
        lambda x: x["monto"] if x["moneda de liquidacion"] == "ARS" else x["monto"] * x["tasa de cambio"], axis=1
    )

    fecha_actual_clarion = fecha_a_clarion(datetime.today())

    # Construcción final del DataFrame de importación masiva
    df_masive_import = pd.DataFrame({
        "Pedidos.Código de cliente": df_total["alias"],
        "Pedidos.Sucursal": df_total["sucursal"],
        "Pedidos.Punto de venta": df_total["punto_de_venta"],
        "Pedidos.Letra": "B",
        "Pedidos.Código de moneda del comprobante": df_total["codigo_moneda"],
        "Pedidos.Valor de moneda del comprobante": 1,
        "Pedidos.Códgio de depósito del comprobante": df_total["codigo_deposito"],
        "Pedidos.Código de condición de venta del comprobante": df_total["codigo_condicion_venta"],
        "Pedidos.Código de vendedor": df_total["codigo_vendedor"],
        "Pedidos.Lista de precios del comprobante": df_total["lista_precio"],
        "Pedidos.Exento del comprobante": df_total["monto_pesificado"],
        "Pedidos.Neto gravado del comprobante": 0,
        "pedidos, Total IVA del comprobante": 0,
        "Pedidos.Porcentaje de IVA en comprobante": 0,
        "Pedidos.Observaciones 1": df_total["numero de liquidacion"].astype(str) + " - " + df_total["tasa de cambio"].astype(str),
        "Pedidos.Precio total del item": df_total["monto_pesificado"],
        "Pedidos.Código de artículo del item": df_total["tasa"],
        "Pedidos.Cantidad del item": 1,
        "Pedidos.Código de depósito del item": df_total["codigo_deposito"],
        "Pedidos.Codigo de moneda del item": df_total["codigo_moneda"],
        "Pedidos.Valor de moneda del item": df_total["valor_moneda_item"],
        "Pedidos.Fecha del comprobante": fecha_actual_clarion
    })

    return df_masive_import
