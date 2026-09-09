from nextcord.ext import commands, tasks
from config import TEXT_CHANNEL_ID


class Ready(commands.Cog):
    """Notificação de inicialização enviada a um canal pré-configurado."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.say_its_ready.is_running():
            self.say_its_ready.start()

    @tasks.loop(count=1)
    async def say_its_ready(self):
        if TEXT_CHANNEL_ID:
            channel = self.bot.get_channel(TEXT_CHANNEL_ID)
            if channel:
                await channel.send("Olá, estou pronta.")


def setup(bot):
    bot.add_cog(Ready(bot))
