import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from bot import servidores
from embeds import embed_commands_list


class Help(commands.Cog):
    @nextcord.slash_command(description="Descreve todos os comandos do Bot",
                            guild_ids=servidores)
    async def help(self, interaction: Interaction):
        await embed_commands_list(interaction)

    @nextcord.slash_command(description="Te responde dizendo aquilo que você digitou", guild_ids=servidores)
    async def mediga(self, interaction: Interaction, mensagem):
        await interaction.response.send_message(mensagem)


def setup(bot):
    bot.add_cog(Help(bot))
