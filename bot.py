import os

import nextcord
from nextcord import Interaction
from nextcord.ext import commands, tasks
from decouple import config

intents = nextcord.Intents().all()
# intents = nextcord.Intents.default()
# intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')
servidores = [774359671510532106, 911425044524187688, 896899908693553173]


def load_cogs(bot):
    bot.load_extension("manager")
    bot.load_extension("tasks.ready")
    bot.load_extension("tasks.change_status")

    for file in os.listdir("commands"):
        if file.endswith(".py"):
            cog = file[:-3]
            bot.load_extension(f"commands.{cog}")


load_cogs(bot)

TOKEN = config("TOKEN")
bot.run(TOKEN)
