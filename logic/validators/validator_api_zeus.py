##PARA CONECTARSE AL SERVICIO DE API
import requests
import pandas as pd

# Columnas mandatorias necesarias para la validación del maetro de clientes ZEUS ERP
MANDATORY_COLUMNS = ["codigo_cliente", "razon_social", "codigo_localidad", "codigo_provincia", 
                     "codigo_iva", "codigo_condicion_venta", "lista_precio"]

# Columnas necesarias para la posterior importación masiva en ZEUS ERP
DATAFRAME_CLIENTS_COLUMNS = ["codigo_cliente","codigo_deposito","codigo_condicion_venta","lista_precio"]

# Función para obtener los datos de clientes de ZEUS ERP
def validate_completed_columns(df, columns):
    incomplete = []

    for col in columns:
        if col not in df.columns:
            incomplete.append(f"❌ Columna faltante: {col}")
        else:
            # Verifica que no haya ni NaN ni cadenas vacías o con espacios
            if df[col].isnull().any() or (df[col].astype(str).str.strip() == "").any():
                incomplete.append(f"⚠️ Valores vacíos en columna: {col}")
    return incomplete

# Consulta al endpoint /cliente
def validate_completed_clients(username, password):
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
    
    # Datos necesarios para consulta api
    headers = {"Authorization": f"Bearer {access_token}"}
    endpoint = "/cliente"
    base_url = "https://api.infosis.tech/zeus"
    url = f"{base_url}{endpoint}"

    # Hago la petición GET
    print(f"🔸 Consultando {url}")
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        # Verifico que la respuesta tenga los datos esperados
        if isinstance(data, list) and data:
            df_clients_zeus = pd.json_normalize(data)
            missing_columns = validate_completed_columns(df_clients_zeus, MANDATORY_COLUMNS)
            # Si no hay columnas faltantes, procedo a obtener los datos de clientes
            if missing_columns:
                print("⚠️ Faltan columnas obligatorias en el DataFrame de clientes:")
                df_clients_zeus = df_clients_zeus[DATAFRAME_CLIENTS_COLUMNS] #ESTE HAY QUE BORRARLO PARA EL FINAL
                for msg in missing_columns:
                    print(msg)
            # Si no hay columnas faltantes, procedo a obtener los datos de clientes
            else:
                print("✅ Todas las columnas obligatorias están presentes en el DataFrame de clientes.")
                df_clients_zeus = df_clients_zeus[DATAFRAME_CLIENTS_COLUMNS]
            return not bool(missing_columns),df_clients_zeus      
        else:
            print(f"⚠️ No hay datos en {endpoint}, o la respuesta no es una lista.")

    except Exception as e:
        print(f"❌ Error al consultar {endpoint}: {e}")

