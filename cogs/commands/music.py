import asyncio
import re
import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from youtubesearchpython import VideosSearch
import yt_dlp

from config import servidores
from utils.embeds import embed_music_added_to_queue, embed_music_queue_list, embed_now_playing
from utils.views import MusicPlayerView

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

queues = {}
disconnect_timers = {}
last_text_channels = {}


def cancel_disconnect_timer(guild_id: int):
    task = disconnect_timers.pop(guild_id, None)
    if task and not task.done():
        task.cancel()


def schedule_disconnect(guild, delay: int = 180, reason: str = "inatividade"):
    guild_id = guild.id
    cancel_disconnect_timer(guild_id)

    async def _disconnect_task():
        try:
            await asyncio.sleep(delay)
            voice_client = guild.voice_client
            if voice_client and voice_client.is_connected() and voice_client.channel:
                channel = voice_client.channel
                humans = [m for m in channel.members if not m.bot]
                is_idle = not voice_client.is_playing() and not voice_client.is_paused()
                is_alone = len(humans) == 0

                if is_alone or is_idle:
                    queues.pop(guild_id, None)
                    if voice_client.is_playing() or voice_client.is_paused():
                        voice_client.stop()
                    await voice_client.disconnect()

                    text_channel = last_text_channels.pop(guild_id, None)
                    if text_channel:
                        try:
                            if reason == "canal_vazio":
                                await text_channel.send("Desconectado do canal de voz: canal vazio.")
                            else:
                                await text_channel.send("Desconectado do canal de voz por inatividade.")
                        except Exception:
                            pass
        except asyncio.CancelledError:
            pass
        finally:
            disconnect_timers.pop(guild_id, None)

    disconnect_timers[guild_id] = asyncio.create_task(_disconnect_task())


def check_queue(guild_id, voice_client):
    if (
        voice_client
        and voice_client.is_connected()
        and guild_id in queues
        and len(queues[guild_id]['sources']) > 0
    ):
        source = queues[guild_id]['sources'].pop(0)
        queues[guild_id]['names'].pop(0)
        next_info = queues[guild_id]['infos'].pop(0) if 'infos' in queues[guild_id] and len(queues[guild_id]['infos']) > 0 else None
        voice_client.play(source, after=lambda error: check_queue(guild_id, voice_client))

        text_channel = last_text_channels.get(guild_id)
        if text_channel and next_info:
            embed = embed_now_playing(
                next_info['title'],
                next_info['webpage_url'],
                next_info['channel'],
                next_info['duration'],
                next_info['thumbnail'],
                next_info.get('requester')
            )
            view = MusicPlayerView(guild_id, queues, cancel_disconnect_timer, last_text_channels)
            asyncio.run_coroutine_threadsafe(
                text_channel.send(embed=embed, view=view),
                voice_client.loop
            )
    else:
        queues.pop(guild_id, None)
        if voice_client and voice_client.is_connected() and voice_client.guild:
            schedule_disconnect(voice_client.guild, delay=180, reason="inatividade")


class Musics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_unload(self):
        for guild_id in list(disconnect_timers.keys()):
            cancel_disconnect_timer(guild_id)

    async def _extract_song_info(self, query: str) -> dict:
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

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: nextcord.Member, before: nextcord.VoiceState, after: nextcord.VoiceState):
        if member.id == self.bot.user.id and after.channel is None:
            cancel_disconnect_timer(member.guild.id)
            queues.pop(member.guild.id, None)
            last_text_channels.pop(member.guild.id, None)
            return

        voice_client = member.guild.voice_client
        if not voice_client or not voice_client.is_connected() or not voice_client.channel:
            return

        bot_channel = voice_client.channel

        if before.channel == bot_channel and after.channel != bot_channel:
            humans = [m for m in bot_channel.members if not m.bot]
            if len(humans) == 0:
                schedule_disconnect(member.guild, delay=60, reason="canal_vazio")

        elif after.channel == bot_channel and not member.bot:
            cancel_disconnect_timer(member.guild.id)
            if not voice_client.is_playing() and not voice_client.is_paused():
                schedule_disconnect(member.guild, delay=180, reason="inatividade")

    @nextcord.slash_command(name="join", description="Conecta o bot ao seu canal de voz.", guild_ids=servidores)
    async def join(self, interaction: Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.send("Você precisa estar em um canal de voz.")

        channel = interaction.user.voice.channel
        last_text_channels[interaction.guild_id] = interaction.channel
        cancel_disconnect_timer(interaction.guild_id)

        if interaction.guild.voice_client is None:
            await channel.connect()
            schedule_disconnect(interaction.guild, delay=180, reason="inatividade")
            await interaction.send(f'Conectado ao canal ``{channel}``.')
        else:
            await interaction.send(f'Já conectado ao canal ``{interaction.guild.voice_client.channel}``.')

    @nextcord.slash_command(name="leave", description="Desconecta o bot do canal de voz.", guild_ids=servidores)
    async def disconnect(self, interaction: Interaction):
        if interaction.guild.voice_client is None:
            return await interaction.send("Não estou conectado a um canal de voz.")

        channel = interaction.guild.voice_client.channel
        cancel_disconnect_timer(interaction.guild_id)
        queues.pop(interaction.guild_id, None)
        last_text_channels.pop(interaction.guild_id, None)

        if interaction.guild.voice_client.is_playing() or interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.stop()
        await interaction.guild.voice_client.disconnect()
        await interaction.send(f'Desconectado do canal ``{channel}``.')

    @nextcord.slash_command(
        name="play",
        description="Toca a música informada ou adiciona à fila.",
        guild_ids=servidores
    )
    async def tocar(
        self,
        interaction: Interaction,
        busca: str = nextcord.SlashOption(description="Nome ou link da música")
    ):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.send("Você precisa estar em um canal de voz.")

        await interaction.response.defer()

        channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await channel.connect()

        last_text_channels[interaction.guild_id] = interaction.channel
        cancel_disconnect_timer(interaction.guild_id)

        song_info = await self._extract_song_info(busca)
        if not song_info or not song_info.get('audio_url'):
            return await interaction.followup.send("Não foi possível encontrar ou extrair o áudio desta música.")

        try:
            source = await nextcord.FFmpegOpusAudio.from_probe(song_info['audio_url'], **FFMPEG_OPTIONS)
        except Exception as error:
            return await interaction.followup.send(f"Erro ao processar áudio: `{error}`.")

        guild_id = interaction.guild_id
        song_info['requester'] = interaction.user.name

        if guild_id not in queues or not voice_client.is_playing():
            queues[guild_id] = {'sources': [], 'names': [song_info['title']], 'infos': []}
            voice_client.play(source, after=lambda error: check_queue(guild_id, voice_client))
            embed = embed_now_playing(
                song_info['title'],
                song_info['webpage_url'],
                song_info['channel'],
                song_info['duration'],
                song_info['thumbnail'],
                interaction.user.name
            )
            view = MusicPlayerView(guild_id, queues, cancel_disconnect_timer, last_text_channels)
            await interaction.followup.send(embed=embed, view=view)
        else:
            queues[guild_id]['sources'].append(source)
            queues[guild_id]['names'].append(song_info['title'])
            if 'infos' not in queues[guild_id]:
                queues[guild_id]['infos'] = []
            queues[guild_id]['infos'].append(song_info)
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

    @nextcord.slash_command(name="pause", description="Pausa a reprodução da música.", guild_ids=servidores)
    async def pausar(self, interaction: Interaction):
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            return await interaction.send("Não estou conectado a um canal de voz.")
        if voice_client.is_playing():
            voice_client.pause()
            await interaction.send("Música pausada. Use `/resume` para continuar.")
        elif voice_client.is_paused():
            await interaction.send("A música já está pausada.")
        else:
            await interaction.send("Nenhuma música em reprodução.")

    @nextcord.slash_command(name="resume", description="Retoma a reprodução da música.", guild_ids=servidores)
    async def retomar(self, interaction: Interaction):
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            return await interaction.send("Não estou conectado a um canal de voz.")
        if voice_client.is_paused():
            voice_client.resume()
            await interaction.send("Reprodução retomada.")
        elif voice_client.is_playing():
            await interaction.send("A música já está em reprodução.")
        else:
            await interaction.send("Nenhuma música pausada.")

    @nextcord.slash_command(name="skip", description="Pula para a próxima música da fila.", guild_ids=servidores)
    async def pular(self, interaction: Interaction):
        voice_client = interaction.guild.voice_client
        guild_id = interaction.guild_id
        if not voice_client or not voice_client.is_connected() or guild_id not in queues or len(queues[guild_id]['names']) < 1:
            return await interaction.send("Não há músicas na fila para pular.")

        voice_client.stop()
        await interaction.send("Tocando próxima música.")

    @nextcord.slash_command(name="queue", description="Exibe a fila de reprodução.", guild_ids=servidores)
    async def queue(self, interaction: Interaction):
        guild_id = interaction.guild_id
        if guild_id in queues and len(queues[guild_id]['names']) > 0:
            names = queues[guild_id]['names']
            await embed_music_queue_list(interaction, names[0], names[1:])
        else:
            await interaction.send("Nenhuma música em reprodução.")

    @nextcord.slash_command(name="clear", description="Limpa as próximas músicas da fila.", guild_ids=servidores)
    async def clear(self, interaction: Interaction):
        guild_id = interaction.guild_id
        if guild_id in queues and len(queues[guild_id]['sources']) > 0:
            queues[guild_id]['sources'].clear()
            queues[guild_id]['names'] = queues[guild_id]['names'][:1]
            if 'infos' in queues[guild_id]:
                queues[guild_id]['infos'].clear()
            await interaction.send("Fila limpa.")
        else:
            await interaction.send("A fila já está vazia.")

    @nextcord.slash_command(name="remove", description="Remove uma música da fila pela posição.", guild_ids=servidores)
    async def remove(
        self,
        interaction: Interaction,
        posicao: int = nextcord.SlashOption(description="Posição da música na fila (a partir de 1)")
    ):
        guild_id = interaction.guild_id
        if guild_id not in queues or len(queues[guild_id]['sources']) == 0:
            return await interaction.send("A fila está vazia.")

        if posicao < 1 or posicao > len(queues[guild_id]['sources']):
            return await interaction.send("Posição não encontrada na fila.")

        removed_name = queues[guild_id]['names'].pop(posicao)
        del queues[guild_id]['sources'][posicao - 1]
        if 'infos' in queues[guild_id] and len(queues[guild_id]['infos']) >= posicao:
            del queues[guild_id]['infos'][posicao - 1]
        await interaction.send(f"Música `{removed_name}` removida da fila.")

    @nextcord.slash_command(name="skipto", description="Pula diretamente para uma posição da fila.", guild_ids=servidores)
    async def skipto(
        self,
        interaction: Interaction,
        posicao: int = nextcord.SlashOption(description="Posição para onde deseja pular")
    ):
        guild_id = interaction.guild_id
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected() or guild_id not in queues or len(queues[guild_id]['sources']) == 0:
            return await interaction.send("A fila está vazia.")

        if posicao < 1 or posicao > len(queues[guild_id]['sources']):
            return await interaction.send("Posição não encontrada na fila.")

        target_name = queues[guild_id]['names'][posicao]
        queues[guild_id]['sources'] = queues[guild_id]['sources'][posicao - 1:]
        queues[guild_id]['names'] = [queues[guild_id]['names'][0]] + queues[guild_id]['names'][posicao:]
        if 'infos' in queues[guild_id]:
            queues[guild_id]['infos'] = queues[guild_id]['infos'][posicao - 1:]

        await interaction.send(f"Tocando agora: `{target_name}`.")
        voice_client.stop()

    @nextcord.slash_command(name="stop", description="Interrompe a reprodução, limpa a fila e desconecta o bot.", guild_ids=servidores)
    async def stop(self, interaction: Interaction):
        guild_id = interaction.guild_id
        cancel_disconnect_timer(guild_id)
        queues.pop(guild_id, None)
        last_text_channels.pop(guild_id, None)

        voice_client = interaction.guild.voice_client
        if voice_client:
            if voice_client.is_playing() or voice_client.is_paused():
                voice_client.stop()
            await voice_client.disconnect()
            await interaction.send("Desconectado e fila limpa.")
        else:
            await interaction.send("Não estou conectado a um canal de voz.")

    @nextcord.slash_command(name="moveto", description="Move o bot para o seu canal de voz.", guild_ids=servidores)
    async def moveto(self, interaction: Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            return await interaction.send("Você precisa estar em um canal de voz.")
        voice_client = interaction.guild.voice_client
        if not voice_client:
            return await interaction.send("Não estou conectado a um canal no momento.")

        if interaction.user.voice.channel == voice_client.channel:
            await interaction.send(f"Já conectado ao canal ``{voice_client.channel}``.")
        else:
            await voice_client.move_to(interaction.user.voice.channel)
            await interaction.send(f"Conectado ao canal ``{interaction.user.voice.channel}``.")


def setup(bot):
    bot.add_cog(Musics(bot))
