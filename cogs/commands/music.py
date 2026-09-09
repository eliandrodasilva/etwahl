import re
import nextcord
from nextcord import Interaction, VoiceChannel, VoiceClient
from nextcord.ext import commands
from youtubesearchpython import VideosSearch
import youtube_dl

from config import servidores
from utils.embeds import embed_music_added_to_queue, embed_music_queue_list

players = {}
queue = {}


def check_queue(ctx, guild_id):
    if guild_id in queue and len(queue[guild_id]) > 0:
        voice = ctx.voice_client
        source = queue[guild_id].pop(0)
        queue['names'].pop(0)
        player = voice.play(source, after=lambda x=None: check_queue(ctx, guild_id))
    else:
        del players[guild_id]
        del queue['names']


class Musics(commands.Cog):
    """Comandos para reprodução de música em canais de voz."""

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="join", description="Chama o Bot para o seu Canal de Voz.", guild_ids=servidores)
    async def join(self, interaction: Interaction):
        channel = interaction.user.voice.channel
        if interaction.user.voice is None:
            await interaction.send("**Você precisa estar em um Canal de Voz!**")
        if interaction.guild.voice_client is None:
            await channel.connect()
            await interaction.send(f'**Conectada ao Canal** ``{channel}``')
        else:
            await interaction.send(f'**Já estou conectada ao canal **``{interaction.guild.voice_client.channel}``')

    @commands.command(aliases=['joinhere'])  # DESATUALIZADO
    async def moveto(self, ctx):
        if ctx.author.voice.channel == ctx.voice_client.channel:
            await ctx.send(f'**Já estou conectada ao canal **``{ctx.voice_client.channel}``')
        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
            await ctx.reply(f'**Conectada agora ao Canal** ``{ctx.message.author.voice.channel}``')

    @nextcord.slash_command(name="leave", description="Disconecta o bot do canal de voz.", guild_ids=servidores)
    async def disconnect(self, interaction: Interaction):
        channel = interaction.guild.voice_client.channel
        await interaction.guild.voice_client.disconnect()
        await interaction.send(f'**Desconectada do Canal** ``{channel}``')

    @nextcord.slash_command(name="play", description="Toca a música inserida, caso uma já esteja tocando a inserida é "
                                                     "adicionada a fila.", guild_ids=servidores)
    async def tocar(self, interaction: Interaction, url_video):
        channel = interaction.user.voice.channel
        if interaction.user.voice is None:
            await interaction.send("**Você precisa estar em um Canal de Voz!**")
        if interaction.guild.voice_client is None:
            await channel.connect()
            await interaction.send(f'**Conectada ao Canal** ``{channel}``')

        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        ydl_options = {'format': 'bestaudio'}

        template_url = re.compile('(http(s)?://)?(www.)?youtu(.be/)?(be.com)?/')
        videos_search = VideosSearch(url_video, limit=1)
        data = videos_search.result()
        video_link = data['result'][0]['link']
        video_title = data['result'][0]['title']

        if template_url.match(url_video):
            info = youtube_dl.YoutubeDL().extract_info(url_video, download=False)
            url_audio = info['formats'][0]['url']
            await interaction.send(f" 🔎 **Procurando pela URL do vídeo **`{video_title.title()}`")
            source = await nextcord.FFmpegOpusAudio.from_probe(url_audio, **ffmpeg_options)
            voice_cli = VoiceClient(client=interaction.guild.voice_client.client, channel=interaction.user.voice.channel)
            # voice_cha = VoiceChannel(guild=interaction.guild, data=nextcord.VoiceState.channel, state=voice_cli._state)
            await voice_cli.connect(timeout=60.0, reconnect=True)

            voice_cli.play(source)
        else:
            info = youtube_dl.YoutubeDL(ydl_options).extract_info(video_link, download=False)
            url_audio = info['formats'][0]['url']
            source = await nextcord.FFmpegOpusAudio.from_probe(url_audio, **ffmpeg_options)
            await interaction.send(f' 🔎 **Procurando por: ** `{video_title.title()}`')
            voice_cli = VoiceClient(interaction.client, interaction.guild.voice_client.channel)
            voice_cli.play(source)

        guild_id = interaction.guild_id

    @commands.command(aliases=['p'], pass_context=True)
    async def play(self, ctx, *url):
        if ctx.author.voice is None:
            await ctx.send("**Você precisa estar conectado em um Canal de Voz!**")
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
            channel = ctx.message.author.voice.channel
            await ctx.send(f'**Conectada ao Canal** ``{channel}``')

        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': '-vn'}
        YDL_OPTIONS = {'format': 'bestaudio'}

        url1 = ' '.join(url)
        padrao_url = re.compile('(http(s)?://)?(www.)?youtu(.be/)?(be.com)?/')
        videosSearch = VideosSearch(url1, limit=1)
        data = videosSearch.result()
        video_link = data['result'][0]['link']
        video_title = data['result'][0]['title']

        if padrao_url.match(url1):
            video_link = url1
            info = youtube_dl.YoutubeDL(YDL_OPTIONS).extract_info(url1, download=False)
            url2 = info['formats'][0]['url']
            await ctx.send(" 🔎 **Procurando pela URL...**")
            source = await nextcord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        else:
            info = youtube_dl.YoutubeDL(YDL_OPTIONS).extract_info(video_link, download=False)
            url2 = info['formats'][0]['url']
            source = await nextcord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            await ctx.send(f' 🔎 **Procurando por: ** `{url1.title()}`')

        async with ctx.typing():

            guild_id = ctx.message.guild.id

            if guild_id not in players:
                guild_id = ctx.message.guild.id
                player = ctx.voice_client.play(source, after=lambda x=None: check_queue(ctx, guild_id))
                queue['names'] = [video_title]
                players[guild_id] = player
                await ctx.send(f"**Tocando:** 🎶 `{video_title}` 🎶")
            else:
                if guild_id not in queue:
                    queue[guild_id] = [source]
                else:
                    queue[guild_id].append(source)
                queue['names'].append(video_title)
                await embed_music_added_to_queue(ctx, video_title, video_link,
                                                 data['result'][0]['channel']['name'],
                                                 data['result'][0]['duration'],
                                                 data['result'][0]['thumbnails'][0]['url'],
                                                 len(queue[guild_id]))

    @commands.command(aliases=['fila'])  # DESATUALIZADO
    async def queue(self, ctx):
        if 'names' in queue:
            await embed_music_queue_list(ctx, queue['names'][0], queue['names'][1:])
        if 'names' not in queue:
            await ctx.send('**úsica está tocando no momento**')

    @commands.command()  # DESATUALIZADO
    async def clear(self, ctx):
        if ctx.message.guild.id in queue and len(queue[ctx.message.guild.id]) > 0:
            del queue[ctx.message.guild.id], queue['names'][1:]
            await ctx.send('**Fila limpa! :)**')
        else:
            await ctx.send('**A fila já tá vazia**')

    @commands.command()  # DESATUALIZADO
    async def remove(self, ctx, position):
        if ctx.message.guild.id not in queue or len(queue[ctx.message.guild.id]) == 0 or str(position).isalpha() \
                or int(position) > len(queue['names']):
            await ctx.send("**Ei, não tem nada nessa posição...**")
        elif str(position).isdigit():
            if ctx.message.guild.id in queue and int(position) <= len(queue['names']):
                await ctx.send(f'**Removendo a música `{queue["names"][int(position)]}` da fila**')
                del queue[ctx.message.guild.id][int(position) - 1], queue["names"][int(position)]

    @commands.command()  # DESATUALIZADO
    async def skip(self, ctx):
        guild_id = ctx.message.guild.id

        if guild_id not in queue or len(queue[guild_id]) < 1:
            await ctx.send('**Não foi possível pular a música!**')

        elif queue:
            voice = ctx.voice_client
            voice.stop()
            await ctx.send(':fast_forward: **Tocando a próxima música.** ')

    @commands.command()  # DESATUALIZADO
    async def skipto(self, ctx, position):
        if ctx.message.guild.id not in queue or len(queue[ctx.message.guild.id]) == 0 or str(position).isalpha() \
                or int(position) > len(queue['names']):
            await ctx.send("**Ei, não tem nada nessa posição...**")
        else:
            await ctx.send(f':fast_forward: **Tocando agora: `{queue["names"][int(position)]}`.** ')
            del queue[ctx.message.guild.id][:int(position) - 1], queue['names'][:int(position) - 1]
            ctx.voice_client.stop()

    @nextcord.slash_command(name="pause", guild_ids=servidores)  # DESENVOLVIMENTO
    async def pausar(self, interaction: Interaction):
        nextcord.VoiceClient.pause()
        await interaction.send('**A música foi pausada. `!resume` para continuar.**')

    @commands.command()  # DESATUALIZADO
    async def stop(self, ctx):
        ctx.voice_client.stop()
        if ctx.message.guild.id in queue:
            del queue[ctx.message.guild.id]
        if 'names' in queue:
            del queue['names']
        if ctx.message.guild.id in players:
            del players[ctx.message.guild.id]
        await ctx.voice_client.disconnect()

    @commands.command()  # DESATUALIZADO
    async def pause(self, ctx):
        ctx.voice_client.pause()
        await ctx.send('**A música foi pausada. `!resume` para continuar.**')

    @commands.command()  # DESATUALIZADO
    async def resume(self, ctx):
        ctx.voice_client.resume()
        await ctx.send('**A música voltou a tocar.**')


def setup(bot):
    bot.add_cog(Musics(bot))
