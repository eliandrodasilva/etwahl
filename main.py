import os
import nextcord
from nextcord.ext import commands

from config import COMMAND_PREFIX, TOKEN


def create_bot() -> commands.Bot:
    """Cria e configura a instância do bot."""
    intents = nextcord.Intents.all()
    bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
    bot.remove_command("help")
    return bot


def load_extensions(bot: commands.Bot) -> None:
    """Carrega dinamicamente todas as extensões presentes na pasta cogs/."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cogs_dir = os.path.join(base_dir, "cogs")

    for root, _, files in os.walk(cogs_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                extension_name = rel_path[:-3].replace(os.path.sep, ".")
                try:
                    bot.load_extension(extension_name)
                    print(f"✓ Extensão carregada: {extension_name}")
                except Exception as error:
                    print(f"✗ Erro ao carregar extensão {extension_name}: {error}")


def main():
    """Ponto de entrada principal da aplicação."""
    if not TOKEN:
        print("[AVISO] TOKEN não definido. Crie um arquivo .env com a variável TOKEN=...")
    bot = create_bot()
    load_extensions(bot)
    if TOKEN:
        bot.run(TOKEN)


if __name__ == "__main__":
    main()
