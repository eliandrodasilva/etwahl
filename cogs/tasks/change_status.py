from random import choice
import nextcord
from nextcord.ext import commands, tasks


class Status(commands.Cog):
    """Atualização periódica do status/presença do bot."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.change_status.is_running():
            self.change_status.start()

    @tasks.loop(seconds=30)
    async def change_status(self):
        # status = ['e ouvindo musiquinhas', 'joguinhos de hentai >///<']
        status = ['Em atualização 🥱']
        await self.bot.change_presence(activity=nextcord.Game(choice(status)))


def setup(bot):
    bot.add_cog(Status(bot))
