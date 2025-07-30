#import getpass
import requests
from config.settings_api_arms import TOKEN_URL, CLIENT_ID, CLIENT_SECRET
from gui.components import solicitar_credenciales_api

# === Función para autenticación OAuth2 ===
def get_token_oauth2():
    username, password = solicitar_credenciales_api("Autenticación ARMS API")
    #username = input("🔑 Ingrese su nombre de usuario: ")
    #password = getpass.getpass("🔑 Ingrese su contraseña: ")
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(TOKEN_URL, data=payload, headers=headers)
        response.raise_for_status()
        token = response.json()["access_token"]
        print(token)
        print("✅ Token OAuth2 obtenido correctamente.")
        return token
    except Exception as e:
        print(f"❌ Error al obtener token OAuth2: {e}")


#get_token_oauth2()