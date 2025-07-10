import pandas as pd
from gui.components import archivos_cargados

def cargar_archivos(archivos):
    """
    Carga los archivos necesarios para el procesamiento.
    Retorna cuatro DataFrames: df_dom, df_int, df_clients, df_arms.
    """
    try:
        df_dom = pd.read_excel(archivos['liq_dom_pbi'])
        df_int = pd.read_excel(archivos['liq_int_pbi'])
        df_clients = pd.read_excel(archivos['clients_pbi'])

        if archivos['liq_arms'].endswith(".xlsx"):
            df_arms = pd.read_excel(archivos['liq_arms'])
        else:
            df_arms = pd.read_csv(archivos['liq_arms'])

        return df_dom, df_int, df_clients, df_arms

    except Exception as e:
        raise RuntimeError(f"Error al leer los archivos: {e}")
