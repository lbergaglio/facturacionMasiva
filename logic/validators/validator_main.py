import os
import pandas as pd

HEADERS_ESPERADOS = {
    "clientes_maestros": [
        "Clientes.Categorias.CodigoZeus", "Clientes.Categorias.Descripcion", "CodigoZeus", "CondicionVenta", 
        "NombreCondVta", "CuentaId", "CUIT", "DepositoId", "NombreDeposito", "Descripcion", "DetalleAeronave", 
        "Domicilio", "Fantasía", "IdCliente", "ListaPrecioId", "NombreLista", "LocalidadId", "NombreLocalidad", 
        "Notas", "PaisId", "NombrePaís", "ProvinciaId", "NombreProvincia", "SituaciónIvaId", "DescripciónIVA", 
        "Email", "Activo"         
    ]
}

def normalizar_headers(headers):
    return [str(h).strip().lower() for h in headers]

def validar_headers_excel(filepath, tipo_archivo):
    try:
        if tipo_archivo == "liquidaciones_arms" and filepath.lower().endswith(".csv"):
            df = pd.read_csv(filepath)
        else:
            if filepath.lower().endswith(".csv"):
                return False, f"El archivo para {tipo_archivo} debe ser .xls o .xlsx"
            df = pd.read_excel(filepath, header=6)
    except Exception as e:
        return False, f"No se pudo leer el archivo: {e}"

    headers = list(df.columns)
    esperado = HEADERS_ESPERADOS.get(tipo_archivo)
    if esperado is None:
        return False, "Tipo de archivo desconocido."

    esperado_set = set(normalizar_headers(esperado))
    headers_set = set(normalizar_headers(headers))

    faltantes = esperado_set - headers_set
    extra = headers_set - esperado_set

    if faltantes or extra:
        return False, (
            f"Headers incorrectos para {tipo_archivo.replace('_', ' ').title()}.\n"
            f"Faltantes: {faltantes}\nExtra: {extra}"
        )

    if tipo_archivo == "clientes_maestros":
        # Validaciones específicas para clientes maestros
        if not df['id'].apply(lambda x: isinstance(x, int) and x > 0).all():
            return False, "La columna 'id' debe ser numérica y mayor a 0."
        if not df['name'].apply(lambda x: isinstance(x, str) and len(x) > 0).all():
            return False, "La columna 'name' debe contener nombres válidos."

    # Validaciones adicionales
    """if tipo_archivo in ["powerbi_domestico", "powerbi_internacional"]:
        col = "Moneda de Liquidación"
        esperado_valor = "ARS" if tipo_archivo == "powerbi_domestico" else "USD"
        if col not in df.columns:
            return False, f"Falta la columna '{col}'."
        valores = df[col].dropna().astype(str).str.upper().str.strip()
        if not all(valores == esperado_valor):
            valores_distintos = valores[valores != esperado_valor].unique()
            return False, f"La columna '{col}' debe contener solo '{esperado_valor}'. Valores encontrados: {valores_distintos}"

    elif tipo_archivo == "liquidaciones_arms":
        if not pd.api.types.is_numeric_dtype(df['Exchange Rate To USD']):
            return False, "La columna 'Exchange Rate To USD' debe ser numérica."
        fechas = ['Invoice Date', 'Payment Due Date', 'Invoice Date Of Issue']
        for col in fechas:
            if col not in df.columns:
                return False, f"Falta la columna '{col}'"
            try:
                pd.to_datetime(df[col])
            except:
                return False, f"La columna '{col}' contiene valores no reconocidos como fechas."
"""
    return True, "Archivo válido."
