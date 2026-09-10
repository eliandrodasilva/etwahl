import asyncio
import re
import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from youtubesearchpython import VideosSearch
import yt_dlp

from config import servidores
from utils.embeds import embed_music_added_to_queue, embed_music_queue_list

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'no_warnings': True,
}

# Dicionário de filas isoladas por servidor (guild_id)
# queues[guild_id] = {
#     'sources': [source, ...],
#     'names': [currently_playing_title, next_title_1, next_title_2, ...]
# }
queues = {}


def check_queue(guild_id, voice_client):
    """Callback invocado automaticamente ao término de cada faixa de áudio."""
    if (
        voice_client
        and voice_client.is_connected()
        and guild_id in queues
        and len(queues[guild_id]['sources']) > 0
    ):
        source = queues[guild_id]['sources'].pop(0)
        queues[guild_id]['names'].pop(0)
        voice_client.play(source, after=lambda error: check_queue(guild_id, voice_client))
    else:
        queues.pop(guild_id, None)


class Musics(commands.Cog):
    """Comandos para reprodução de música em canais de voz."""

    def __init__(self, bot):
        self.bot = bot

    async def _extract_song_info(self, query: str) -> dict:
        """Busca e extrai metadados e URL de áudio do YouTube de forma assíncrona."""
        loop = asyncio.get_running_loop()
        is_url = bool(re.match(r'^(http(s)?://)?(www\.)?youtu', query))

        channel_name = "YouTube"
        duration_str = "N/A"
        thumbnail_url = ""
        video_title = None
        search_query = query

        if not is_url:
            try:
                vsearch = VideosSearch(query, limit=1)
                res_dict = vsearch.result()
                if res_dict and res_dict.get('result'):
                    first_res = res_dict['result'][0]
                    search_query = first_res['link']
                    video_title = first_res.get('title')
                    channel_name = first_res.get('channel', {}).get('name', 'YouTube')
                    duration_str = first_res.get('duration', 'N/A')
                    if first_res.get('thumbnails'):
                        thumbnail_url = first_res['thumbnails'][0]['url']
            except Exception:
                search_query = f"ytsearch1:{query}"

        def _extract():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                return ydl.extract_info(search_query, download=False)

        try:
            data = await loop.run_in_executor(None, _extract)
        except Exception:
            return {}

        if not data:
            return {}

        if 'entries' in data and data['entries']:
            data = data['entries'][0]

        audio_url = data.get('url')
        if not audio_url and 'formats' in data:
            audio_url = data['formats'][0].get('url')

        return {
            'title': video_title or data.get('title', 'Música'),
            'audio_url': audio_url,
            'webpage_url': data.get('webpage_url', search_query),
            'channel': data.get('uploader') or channel_name,
            'duration': data.get('duration_string') or duration_str,
            'thumbnail': data.get('thumbnail') or thumbnail_url
        }

    # ==================== SLASH COMMANDS ====================

    @nextcord.slash_command(name="join", description="Chama o Bot para o seu Canal de Voz.", guild_ids=servidores)
    async def join(self, interaction: Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.send("**Você precisa estar em um Canal de Voz!**")

        channel = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            await channel.connect()
            await interaction.send(f'**Conectada ao Canal** ``{channel}``')
        else:
            await interaction.send(f'**Já estou conectada ao canal **``{interaction.guild.voice_client.channel}``')

    @nextcord.slash_command(name="leave", description="Desconecta o bot do canal de voz.", guild_ids=servidores)
    async def disconnect(self, interaction: Interaction):
        if interaction.guild.voice_client is None:
            return await interaction.send("**Não estou conectada a nenhum canal de voz!**")

        channel = interaction.guild.voice_client.channel
        queues.pop(interaction.guild_id, None)
        if interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.stop()
        await interaction.guild.voice_client.disconnect()
        await interaction.send(f'**Desconectada do Canal** ``{channel}``')

    @nextcord.slash_command(
        name="play",
        description="Toca a música inserida ou adiciona à fila.",
        guild_ids=servidores
    )
    async def tocar(self, interaction: Interaction, url_video: str):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.send("**Você precisa estar em um Canal de Voz!**")

        await interaction.response.defer()

        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await channel.connect()

        song_info = await self._extract_song_info(url_video)
        if not song_info or not song_info.get('audio_url'):
            return await interaction.followup.send("❌ **Não foi possível encontrar ou extrair o áudio dessa música.**")

        try:
            source = await nextcord.FFmpegOpusAudio.from_probe(song_info['audio_url'], **FFMPEG_OPTIONS)
        except Exception as error:
            return await interaction.followup.send(f"❌ **Erro ao processar o áudio com FFmpeg:** `{error}`")

        guild_id = interaction.guild_id
        if guild_id not in queues or not voice_client.is_playing():
            queues[guild_id] = {'sources': [], 'names': [song_info['title']]}
            voice_client.play(source, after=lambda error: check_queue(guild_id, voice_client))
            await interaction.followup.send(f"**Tocando:** 🎶 `{song_info['title']}` 🎶")
        else:
            queues[guild_id]['sources'].append(source)
            queues[guild_id]['names'].append(song_info['title'])
            queue_pos = len(queues[guild_id]['sources'])
            await embed_music_added_to_queue(
                interaction,
                song_info['title'],
                song_info['webpage_url'],
                song_info['channel'],
                song_info['duration'],
                song_info['thumbnail'],
                queue_pos
            )

    @nextcord.slash_command(name="pause", description="Pausa a música que está tocando.", guild_ids=servidores)
    async def pausar(self, interaction: Interaction):
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            return await interaction.send('**Não estou em nenhum canal de voz!**')
        if voice_client.is_playing():
            voice_client.pause()
            await interaction.send('**A música foi pausada. Use `/resume` ou `!resume` para continuar.**')
        elif voice_client.is_paused():
            await interaction.send('**A música já está pausada!**')
        else:
            await interaction.send('**Nenhuma música está tocando no momento.**')

    @nextcord.slash_command(name="resume", description="Retoma a música pausada.", guild_ids=servidores)
    async def retomar(self, interaction: Interaction):
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            return await interaction.send('**Não estou em nenhum canal de voz!**')
        if voice_client.is_paused():
            voice_client.resume()
            await interaction.send('**A música voltou a tocar.**')
        elif voice_client.is_playing():
            await interaction.send('**A música já está tocando!**')
        else:
            await interaction.send('**Nenhuma música pausada no momento.**')

    @nextcord.slash_command(name="skip", description="Pula para a próxima música da fila.", guild_ids=servidores)
    async def pular(self, interaction: Interaction):
        voice_client = interaction.guild.voice_client
        guild_id = interaction.guild_id
        if not voice_client or not voice_client.is_connected() or guild_id not in queues or len(queues[guild_id]['names']) < 1:
            return await interaction.send('**Não há músicas na fila para pular!**')

        voice_client.stop()
        await interaction.send(':fast_forward: **Tocando a próxima música.**')

    # ==================== PREFIX COMMANDS (!) ====================

    @commands.command(aliases=['p'], pass_context=True)
    async def play(self, ctx, *url):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("**Você precisa estar conectado em um Canal de Voz!**")

        search_text = " ".join(url).strip()
        if not search_text:
            return await ctx.send("**Por favor, informe o nome ou o link da música.**")

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
            await ctx.send(f'**Conectada ao Canal** ``{voice_channel}``')

        async with ctx.typing():
            await ctx.send(f'🔎 **Procurando por: ** `{search_text}`')
            song_info = await self._extract_song_info(search_text)
            if not song_info or not song_info.get('audio_url'):
                return await ctx.send("❌ **Não foi possível encontrar ou extrair o áudio dessa música.**")

            try:
                source = await nextcord.FFmpegOpusAudio.from_probe(song_info['audio_url'], **FFMPEG_OPTIONS)
            except Exception as error:
                return await ctx.send(f"❌ **Erro ao processar áudio com FFmpeg:** `{error}`")

            guild_id = ctx.guild.id
            if guild_id not in queues or not ctx.voice_client.is_playing():
                queues[guild_id] = {'sources': [], 'names': [song_info['title']]}
                ctx.voice_client.play(source, after=lambda error: check_queue(guild_id, ctx.voice_client))
                await ctx.send(f"**Tocando:** 🎶 `{song_info['title']}` 🎶")
            else:
                queues[guild_id]['sources'].append(source)
                queues[guild_id]['names'].append(song_info['title'])
                queue_pos = len(queues[guild_id]['sources'])
                await embed_music_added_to_queue(
                    ctx,
                    song_info['title'],
                    song_info['webpage_url'],
                    song_info['channel'],
                    song_info['duration'],
                    song_info['thumbnail'],
                    queue_pos
                )

    @commands.command(aliases=['fila'])
    async def queue(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in queues and len(queues[guild_id]['names']) > 0:
            names = queues[guild_id]['names']
            await embed_music_queue_list(ctx, names[0], names[1:])
        else:
            await ctx.send('**Nenhuma música está tocando no momento.**')

    @commands.command()
    async def clear(self, ctx):
        guild_id = ctx.guild.id
        if guild_id in queues and len(queues[guild_id]['sources']) > 0:
            queues[guild_id]['sources'].clear()
            queues[guild_id]['names'] = queues[guild_id]['names'][:1]
            await ctx.send('**Fila limpa! :)**')
        else:
            await ctx.send('**A fila já tá vazia**')

    @commands.command()
    async def remove(self, ctx, position):
        guild_id = ctx.guild.id
        if guild_id not in queues or len(queues[guild_id]['sources']) == 0:
            return await ctx.send('**A fila está vazia!**')

        if not str(position).isdigit():
            return await ctx.send('**Por favor, informe um número de posição válido.**')

        pos = int(position)
        if pos < 1 or pos > len(queues[guild_id]['sources']):
            return await ctx.send('**Ei, não tem nada nessa posição da fila...**')

        removed_name = queues[guild_id]['names'].pop(pos)
        del queues[guild_id]['sources'][pos - 1]
        await ctx.send(f'**Removendo a música `{removed_name}` da fila.**')

    @commands.command()
    async def skip(self, ctx):
        guild_id = ctx.guild.id
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected() or guild_id not in queues or len(queues[guild_id]['names']) < 1:
            return await ctx.send('**Não foi possível pular a música!**')

        voice_client.stop()
        await ctx.send(':fast_forward: **Tocando a próxima música.**')

    @commands.command()
    async def skipto(self, ctx, position):
        guild_id = ctx.guild.id
        if guild_id not in queues or len(queues[guild_id]['sources']) == 0:
            return await ctx.send('**A fila está vazia!**')

        if not str(position).isdigit():
            return await ctx.send('**Por favor, informe um número de posição válido.**')

        pos = int(position)
        if pos < 1 or pos > len(queues[guild_id]['sources']):
            return await ctx.send('**Ei, não tem nada nessa posição...**')

        target_name = queues[guild_id]['names'][pos]
        queues[guild_id]['sources'] = queues[guild_id]['sources'][pos - 1:]
        queues[guild_id]['names'] = [queues[guild_id]['names'][0]] + queues[guild_id]['names'][pos:]

        await ctx.send(f':fast_forward: **Tocando agora: `{target_name}`.**')
        ctx.voice_client.stop()

    @commands.command()
    async def pause(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send('**Não estou em nenhum canal de voz!**')
        if voice_client.is_playing():
            voice_client.pause()
            await ctx.send('**A música foi pausada. `!resume` para continuar.**')
        elif voice_client.is_paused():
            await ctx.send('**A música já está pausada!**')
        else:
            await ctx.send('**Nenhuma música está tocando no momento.**')

    @commands.command()
    async def resume(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_connected():
            return await ctx.send('**Não estou em nenhum canal de voz!**')
        if voice_client.is_paused():
            voice_client.resume()
            await ctx.send('**A música voltou a tocar.**')
        elif voice_client.is_playing():
            await ctx.send('**A música já está tocando!**')
        else:
            await ctx.send('**Nenhuma música pausada no momento.**')

    @commands.command()
    async def stop(self, ctx):
        guild_id = ctx.guild.id
        queues.pop(guild_id, None)
        if ctx.voice_client:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
            await ctx.send('**Bot desconectado e fila limpa.**')
        else:
            await ctx.send('**Não estou em nenhum canal de voz.**')

    @commands.command(aliases=['joinhere'])
    async def moveto(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send('**Você precisa estar em um Canal de Voz!**')
        if not ctx.voice_client:
            return await ctx.send('**Não estou conectada a nenhum canal no momento.**')

        if ctx.author.voice.channel == ctx.voice_client.channel:
            await ctx.send(f'**Já estou conectada ao canal **``{ctx.voice_client.channel}``')
        else:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
            await ctx.reply(f'**Conectada agora ao Canal** ``{ctx.author.voice.channel}``')


def setup(bot):
    bot.add_cog(Musics(bot))
