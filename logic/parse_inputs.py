import pandas as pd
from gui.components import archivos_cargados

def cargar_archivos():
    """
    Carga los archivos necesarios para el procesamiento.
    Retorna cuatro DataFrames: df_dom, df_int, df_clients, df_arms.
    """
    try:
        df_dom = pd.read_excel(archivos_cargados['liq_dom_pbi'])
        df_int = pd.read_excel(archivos_cargados['liq_int_pbi'])
        df_clients = pd.read_excel(archivos_cargados['clients_pbi'])

        if archivos_cargados['liq_arms'].endswith(".xlsx"):
            df_arms = pd.read_excel(archivos_cargados['liq_arms'])
        else:
            df_arms = pd.read_csv(archivos_cargados['liq_arms'])

        return df_dom, df_int, df_clients, df_arms

    except Exception as e:
        raise RuntimeError(f"Error al leer los archivos: {e}")
