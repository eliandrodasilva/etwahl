import nextcord
from nextcord import Embed, Colour, Interaction


async def embed_music_added_to_queue(target, name, url, channel, duration, url_thumbnail, queue_position):
    embed_image = Embed(
        title=name,
        color=Colour.from_rgb(242, 160, 200)
    )
    user = getattr(target, "user", None) or getattr(target, "author", None)
    user_name = user.name if user else "Usuário"
    user_avatar = user.avatar if user else None

    embed_image.set_author(name=f'{user_name} - Adicionou uma música à fila',
                           icon_url=user_avatar)
    if url_thumbnail:
        embed_image.set_thumbnail(url=url_thumbnail)
    embed_image.add_field(name="Canal", value=channel)
    embed_image.add_field(name="Duração", value=duration)
    embed_image.add_field(name="Posição na Fila", value=str(queue_position))

    if hasattr(target, "followup") and target.response.is_done():
        return await target.followup.send(embed=embed_image)
    return await target.send(embed=embed_image)


async def embed_music_queue_list(target, playing_now, queue_names_list):
    embed_list = ''
    embed = Embed(
        title='**Fila atual:**',
        color=Colour.from_rgb(242, 160, 200)
    )
    for idx, song_name in enumerate(queue_names_list, start=1):
        embed_list += f'**`{idx}.` {song_name.title()}**\n'
    embed.set_thumbnail(url='https://uploads.spiritfanfiction.com/fanfics/capitulos/202010/solangelo--quando-o-sol-e'
                            '-a-lua-se-encontram-20789447-191020202011.gif')
    embed.add_field(name=f'**Tocando agora:** 🎶 `{playing_now.title()}` 🎶', value='\u200b', inline=False)
    embed.add_field(name='⬇️ Próximas músicas ⬇',
                    value=embed_list if len(queue_names_list) >= 1 else '🗿 A Fila está vazia! 🗿')

    if hasattr(target, "followup") and target.response.is_done():
        return await target.followup.send(embed=embed)
    return await target.send(embed=embed)


async def embed_commands_list(interaction):
    embed = nextcord.Embed(
        color=nextcord.Colour.from_rgb(242, 160, 200)
    )
    embed.set_author(name='Lista de comandos do Bot')
    embed.add_field(name='/join', value='Chama o Bot para o seu Canal de Voz.', inline=False)
    embed.add_field(name='/leave', value='Desconecta o bot do Canal de Voz.', inline=False)
    embed.add_field(name='/play [música ou URL] (ou !play)', value='Toca a música ou adiciona à fila.', inline=False)
    embed.add_field(name='!queue', value='Exibe a música que está tocando e a fila.', inline=False)
    embed.add_field(name='!clear', value='Remove todas as próximas músicas da fila.', inline=False)
    embed.add_field(name='!remove [posição]', value='Remove uma música específica da fila.', inline=False)
    embed.add_field(name='/skip (ou !skip)', value='Pula para a próxima música da fila.', inline=False)
    embed.add_field(name='!skipto [posição]', value='Pula direto para a música desejada na fila.', inline=False)
    embed.add_field(name='/pause (ou !pause)', value='Pausa a música que está tocando.', inline=False)
    embed.add_field(name='/resume (ou !resume)', value='Retoma a música pausada.', inline=False)
    embed.add_field(name='!stop', value='Para a música, limpa a fila e desconecta o bot.', inline=False)
    embed.add_field(name='!oi', value='Retorna uma saudação aleatória.', inline=False)
    embed.add_field(name='/mediga [mensagem]', value='Repete o texto enviado.', inline=False)

    await interaction.response.send_message(embed=embed)
