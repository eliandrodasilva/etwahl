import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from nextcord.ext.commands.errors import CommandNotFound, MissingRequiredArgument


class Manager(commands.Cog):
    """Gerenciamento de eventos do bot e tratamento de erros."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Olá, sou Euterpe. Estou conectado como {self.bot.user}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # if "Euterpe" in message.content:
        #     await message.channel.send(f'Ei {message.author.name}, me chamou?')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send("Argumentos insuficientes. Use /help para ver os parâmetros do comando.")
        elif isinstance(error, CommandNotFound):
            await ctx.send("Comando inexistente. Use /help para ver a lista de comandos.")
        else:
            raise error


def setup(bot):
    bot.add_cog(Manager(bot))
