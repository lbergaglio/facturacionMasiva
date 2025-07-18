from logic.generators.generator_mails_sent import generar_mails_enviados
from gui.components import solicitar_credenciales_api
from logic.validators.validator_api_zeus import validate_completed_clients

COLUMNS_PORTAL = ["nro_liquidaccion", "fecha_liquidacion", "fecha_vencimiento", "estado"]


def generate_mails_sent():
    """
    Genera el archivo de mails enviados.
    """

