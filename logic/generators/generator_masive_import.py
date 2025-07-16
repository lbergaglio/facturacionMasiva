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

    # Normalizar nombres de columnas
    for df in [df_total, df_total_per_liq, df_clients, df_clientes_zeus, df_vendedores_zeus, df_parametros_zeus]:
        df.columns = df.columns.str.strip().str.lower()
    
    # Validación de columnas necesarias
    required_columns_per_liq = {"número de factura", "centro de facturación"}
    missing = required_columns_per_liq - set(df_total_per_liq.columns)
    if missing:
        raise ValueError(f"Faltan columnas necesarias en df_total_per_liq: {missing}")

    # Asignar tasa de cambio
    df_total["tasa de cambio"] = tasa_cambio
    if df_total[df_total["moneda de liquidacion"] == "USD"]["tasa de cambio"].isnull().any():
        raise ValueError("Hay valores nulos en 'tasa de cambio' para filas en USD.")

    df_total["id"] = df_total["id"].astype(str).str.strip()
    df_clientes_zeus["codigo_cliente"] = df_clientes_zeus["codigo_cliente"].astype(str).str.strip()

    # Renombrar columnas de df_total_per_liq
    df_total_per_liq = df_total_per_liq.rename(columns={
        "número de factura": "numero de liquidacion",
        "centro de facturación": "centro de facturacion"
    })

    # Merge con alias cliente (relacionar nombre con alias)
    df_total = df_total.merge(df_clients[["name", "alias"]], how="left", left_on="cliente", right_on="name")

    # Merge con datos del cliente ZEUS
    df_total = df_total.merge(df_clientes_zeus, how="left", left_on="id", right_on="codigo_cliente")

    # Merge con centro de facturación
    df_total = df_total.merge(
        df_total_per_liq[["numero de liquidacion", "centro de facturacion"]],
        on="numero de liquidacion",
        how="left"
    )

    # Normalizar para merge con vendedores
    df_total["centro de facturacion"] = df_total["centro de facturacion"].str.strip().str.lower()
    df_vendedores_zeus["nombre"] = df_vendedores_zeus["nombre"].str.strip().str.lower()

    # Merge con vendedores
    df_total = df_total.merge(
        df_vendedores_zeus[["nombre", "sucursal", "codigo_vendedor"]],
        how="left",
        left_on="centro de facturacion",
        right_on="nombre"
    )

    # Merge con parámetros (punto de venta, depósito, condición de venta, lista de precios)
    df_total = df_total.merge(df_parametros_zeus, how="left", on="sucursal")

    # ⚠️ ELIMINAR DUPLICADOS por cliente y sucursal, dejando un punto de venta
    df_total = (
        df_total.drop_duplicates(subset=["alias", "sucursal","tasa"], keep="first")
    )

    # Cálculo de campos
    df_total["codigo_moneda"] = df_total["moneda de liquidacion"].map({"ARS": ARS_CODE, "USD": USD_CODE})
    df_total["valor_moneda_item"] = df_total.apply(
        lambda x: 1 if x["moneda de liquidacion"] == "ARS" else x["tasa de cambio"], axis=1
    )
    df_total["monto_pesificado"] = df_total.apply(
        lambda x: x["monto"] if x["moneda de liquidacion"] == "ARS" else x["monto"] * x["tasa de cambio"],
        axis=1
    )

    print("Columnas finales en df_total:", df_total.columns.tolist())
    print("Nulos por columna:\n", df_total[[
        "alias", "sucursal", "punto_de_venta", "codigo_deposito",
        "codigo_condicion_venta", "codigo_vendedor", "lista_precio"
    ]].isnull().sum())

    fecha_actual_clarion = fecha_a_clarion(datetime.today())

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
        "Pedidos.Observaciones 1": df_total["numero de liquidacion"].astype(str) + " - TC: " + df_total["tasa de cambio"].astype(str),
        "Pedidos.Precio total del item": df_total["monto_pesificado"],
        "Pedidos.Código de artículo del item": df_total["tasa"],
        "Pedidos.Cantidad del item": 1,
        "Pedidos.Código de depósito del item": df_total["codigo_deposito"],
        "Pedidos.Codigo de moneda del item": df_total["codigo_moneda"],
        "Pedidos.Valor de moneda del item": df_total["valor_moneda_item"],
        "Pedidos.Fecha del comprobante": fecha_actual_clarion
    })

    return df_masive_import
