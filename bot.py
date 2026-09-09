"""Ponto de entrada de compatibilidade retroativa.

Recomenda-se utilizar `python main.py`. A execução via `python bot.py`
permanece suportada através deste script.
"""
from config import servidores
from main import create_bot, load_extensions, main

if __name__ == "__main__":
    main()
