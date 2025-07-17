##PARA CONECTARSE AL SERVICIO DE API
import requests
import pandas as pd

from gui.components import solicitar_credenciales_api

def get_dataframe(url, columns, headers):
    print(f"🔸 Consultando {url}")
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, list) and data:
            df = pd.json_normalize(data)
            columns_avaiable = [col for col in columns if col in df.columns]
    
            df = df[columns_avaiable]
            return df
            
    except Exception as e:
        print(f"Error al obtener datos de clientes: {e}")
    

def search_dataframes_masive_import(username, password):
    # Reemplazar mis datos
    auth_url = "https://auth.infosis.tech/authenticate?username={username}&password={password}".format(username=username, password=password)

    # Hago el POST
    auth_response = requests.post(auth_url)

    # Evaluo la respuesta
    if auth_response.status_code == 200:
        access_token = auth_response.json()["access_token"]
        print("✅ Token generado correctamente.")
    else:
        raise Exception("❌ Error al generar token: " + auth_response.text)

    headers = {"Authorization": f"Bearer {access_token}"}
    endpoint_vendedores = "/vendedores"
    endpoint_parametros = "/paraux"
    
    base_url = "https://api.infosis.tech/zeus"
    
    url_vendedores = f"{base_url}{endpoint_vendedores}"
    url_parametros = f"{base_url}{endpoint_parametros}"

    vendedores_columns = ["codigo_vendedor","nombre","sucursal"]
    parametros_columns = ["sucursal","punto_de_venta"]

    df_vendedores_zeus = get_dataframe(url_vendedores, vendedores_columns,headers)
    df_parametros_zeus = get_dataframe(url_parametros, parametros_columns, headers)

    return df_vendedores_zeus, df_parametros_zeus

def get_dataframes_from_zeus(username, password):
    #username, password = solicitar_credenciales_api()
    return search_dataframes_masive_import(username, password)

if __name__ == "__getdataframes_from_zeus__":
    get_dataframes_from_zeus()
    

