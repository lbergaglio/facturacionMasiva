##PARA CONECTARSE AL SERVICIO DE API
import requests
import getpass

usuario = input("Ingrese su usuario: ")
contrasena = input("Ingrese su contraseña: ")

# Reemplazar mis datos
auth_url = "https://auth.infosis.tech/authenticate?username={usuario}&password={password}".format(usuario=usuario, password=contrasena)

# Hago el POST
auth_response = requests.post(auth_url)

# Evaluo la respuesta
if auth_response.status_code == 200:
    access_token = auth_response.json()["access_token"]
    print("✅ Token generado correctamente.")
else:
    raise Exception("❌ Error al generar token: " + auth_response.text)


##PARA CONSULTAR CLIENTES Y CONVERTIRLO A UN CSV (Incluye tmb lo de arriba, pueden correr esta parte sola):

import requests
import pandas as pd

# === Paso 1: Autenticación (ACA PONER LOS DATOS CORRECTOS)===
auth_url = "https://auth.infosis.tech/authenticate?{usuario}&password={password}".format(usuario=usuario, password=contrasena)
auth_response = requests.post(auth_url)

if auth_response.status_code == 200:
    access_token = auth_response.json()["access_token"]
    print("✅ Token generado correctamente.")
else:
    raise Exception("❌ Error al generar token: " + auth_response.text)

# === Paso 2: Consulta al endpoint /cliente ===
headers = {"Authorization": f"Bearer {access_token}"}
endpoint = "/cliente"
base_url = "https://api.infosis.tech/zeus"
url = f"{base_url}{endpoint}"

print(f"🔸 Consultando {url}")
try:
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    if isinstance(data, list) and data:
        df = pd.json_normalize(data)
        df.to_excel("clientes_zeus_data.xlsx", index=False)
        print("✅ Archivo 'cliente_zeus_data.xlsx' creado correctamente.")
    else:
        print(f"⚠️ No hay datos en {endpoint}, o la respuesta no es una lista.")

except Exception as e:
    print(f"❌ Error al consultar {endpoint}: {e}")

