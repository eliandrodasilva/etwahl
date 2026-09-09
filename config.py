from decouple import config

# Configurações do Discord Bot
TOKEN = config("TOKEN", default="")
COMMAND_PREFIX = config("COMMAND_PREFIX", default="!")
TEXT_CHANNEL_ID = config("ID_CANAL_TEXTO", default=0, cast=int)

# IDs dos servidores (Guild IDs) registrados para Slash Commands
SERVIDORES = [
    774359671510532106,
    911425044524187688,
    896899908693553173,
]

# Alias mantido para compatibilidade com o código original
servidores = SERVIDORES
