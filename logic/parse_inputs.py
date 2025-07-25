import pandas as pd
from gui.components import archivos_cargados

def cargar_archivos():
    """
    Carga los archivos necesarios para el procesamiento.
    Retorna cuatro DataFrames: df_dom, df_int, df_clients, df_arms.
    """
    try:
        df_clients = pd.read_excel(archivos_cargados['clients_zeus'],skiprows=6)

        return df_clients

    except Exception as e:
        raise RuntimeError(f"Error al leer los archivos: {e}")
