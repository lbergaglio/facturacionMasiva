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
        if tipo_archivo == "clientes_maestros":
            df = pd.read_excel(filepath, skiprows=6)
            df.columns = df.columns.str.lower().str.strip()  # normalizás columnas para evitar errores de mayúsculas
        
        headers = list(df.columns)
        esperado = HEADERS_ESPERADOS.get(tipo_archivo)
        if esperado is None:
            return False, "Tipo de archivo desconocido."

        esperado_set = set(normalizar_headers(esperado))
        headers_set = set(normalizar_headers(headers))

        faltantes = esperado_set - headers_set
        extra = headers_set - esperado_set

        if faltantes or extra:
            return True, (
                f"Headers incorrectos para {tipo_archivo.replace('_', ' ').title()}.\n"
                f"Faltantes: {faltantes}\nExtra: {extra}"
            )
        
        return True, "Archivo válido."

    except Exception as e:
        return False, f"No se pudo leer el archivo: {e}"

    