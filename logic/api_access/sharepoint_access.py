from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
import pandas as pd
import getpass

# === CONFIGURACIÓN ===
URL = "https://eanase1.sharepoint.com/sites/test-aplicacionesadministrativas"
LIST = "AutomatizacionTU"
username = input("Ingrese email: ")
password = getpass.getpass("Ingrese contraseña: ")

# === AUTENTICACIÓN ===
ctx_auth = AuthenticationContext(URL)
if ctx_auth.acquire_token_for_user(username, password):
    print("✅ Autenticación exitosa.")
    ctx = ClientContext(URL, ctx_auth)

    # === ACCESO A LA LISTA ===
    lista = ctx.web.lists.get_by_title(LIST)
    items = lista.items.top(10).get().execute_query()

    # === PROCESAMIENTO DE DATOS ===
    datos = []
    for item in items:
        fecha_envio = item.properties.get("HoraCorreoEnviado")
        fecha_venc = item.properties.get("FechaVencimiento")

        # Formatear fechas (si no son None)
        fecha_envio = pd.to_datetime(fecha_envio).date() if fecha_envio else None
        fecha_venc = pd.to_datetime(fecha_venc).date() if fecha_venc else None

        datos.append({
            "Liquidacion": item.properties.get("Liquidacion"),
            "Fecha de Envio": fecha_envio,
            "Fecha de Vencimiento": fecha_venc
        })

    # === CONVERTIR A DATAFRAME Y MOSTRAR ===
    df = pd.DataFrame(datos)
    print("📄 Fechas:")
    print(df)

else:
    print("❌ Error de autenticación")
