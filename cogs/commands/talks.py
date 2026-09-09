from random import choice
import nextcord
from nextcord.ext import commands


class Talks(commands.Cog):
    """Comandos interativos de conversa com usuários."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="oi", help="Este comando retorna uma mensagem aleatória")
    async def send_hello(self, ctx):
        responses = [
            '***resmunga*** Me chamando pq?',
            'Oi',
            'Oie, como vai?',
            'Oiii <3',
            '**oi meu bombom**',
        ]
        await ctx.send(choice(responses))

    @commands.command(name="pv", help="Lhe envia mensagens no privado.")
    async def secret(self, ctx):
        await ctx.send("Opps, esse comando está desabilitado no momento. Dixculpa :(")
        # try:
        #     await ctx.author.send("Oi docinho <3")
        #     await ctx.author.send("Só passando aqui pra dar um oi")
        #     await ctx.author.send("Precisa de ajuda? digite !help ou !comandos ;)")
        # except nextcord.errors.Forbidden:
        #     await ctx.send("O comando só funciona com o PV liberado rsrsrs")
        #     await ctx.send("(obs: para liberar o pv vá em "
        #                    "[Privacidade e Segurança] e habilite [permitir DMs de membros do servidor])")


def setup(bot):
    bot.add_cog(Talks(bot))
