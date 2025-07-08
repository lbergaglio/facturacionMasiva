import requests
import pandas as pd
import getpass

# === Paso 1: Autenticación correcta ===
def obtener_token_zeus(usuario: str, password: str) -> str:
    url = "https://auth.infosis.tech/authenticate"
    payload = {"username": usuario, "password": password}
    headers = {"Content-Type": "application/json"}

    print("🔐 Enviando solicitud de autenticación...")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Error de conexión al autenticarse: {e}")

    json_resp = response.json()
    if "access_token" in json_resp:
        print("✅ Token generado correctamente.")
        return json_resp["access_token"]
    else:
        raise Exception(f"❌ Error en respuesta: {json_resp.get('message', 'Sin mensaje')}")

# === Paso 2: Consulta de clientes ===
def consultar_clientes_zeus(token: str) -> pd.DataFrame:
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.infosis.tech/zeus/cliente"

    print(f"🔸 Consultando endpoint: {url}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"❌ Error al consultar clientes: {e}")

    data = response.json()
    if isinstance(data, list) and data:
        df = pd.json_normalize(data)
        print(f"✅ {len(df)} clientes obtenidos correctamente.")
        return df
    else:
        print("⚠️ Respuesta vacía o malformada.")
        return pd.DataFrame()

# === Ejemplo de uso ===
if __name__ == "__main__":
    usuario = input("Ingrese usuario: ") 
    password = getpass.getpass("Ingrese contraseña: ")
    try:
        token = obtener_token_zeus(usuario, password)
        df_clientes = consultar_clientes_zeus(token)
        df_clientes.to_excel("clientes_zeus_data.xlsx", index=False)
        print("📁 Archivo exportado: clientes_zeus_data.xlsx")
    except Exception as e:
        print(e)
