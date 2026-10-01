from random import choice
import nextcord
from nextcord import Interaction
from nextcord.ext import commands

from config import servidores


class Talks(commands.Cog):
    """Comandos interativos de conversa com usuários."""

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="oi", description="Envia uma saudação.", guild_ids=servidores)
    async def send_hello(self, interaction: Interaction):
        responses = [
            'Olá.',
            'Oi, tudo bem?',
            'Olá, como posso ajudar?',
        ]
        await interaction.send(choice(responses))

    @nextcord.slash_command(name="pv", description="Envia uma mensagem no privado.", guild_ids=servidores)
    async def secret(self, interaction: Interaction):
        await interaction.send("Comando desabilitado no momento.", ephemeral=True)


def setup(bot):
    bot.add_cog(Talks(bot))
