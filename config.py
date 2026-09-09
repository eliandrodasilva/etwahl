from decouple import config

# Configurações do Discord Bot
TOKEN = config("TOKEN", default="")
COMMAND_PREFIX = config("COMMAND_PREFIX", default="!")
def _cast_int_safe(value):
    val_str = str(value).strip() if value is not None else ""
    return int(val_str) if val_str.isdigit() else 0


TEXT_CHANNEL_ID = config("ID_CANAL_TEXTO", default=0, cast=_cast_int_safe)

# IDs dos servidores (Guild IDs) registrados para Slash Commands
SERVIDORES = [
    774359671510532106,
    911425044524187688,
    896899908693553173,
]

# Alias mantido para compatibilidade com o código original
servidores = SERVIDORES
