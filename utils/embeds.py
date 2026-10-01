import nextcord
from nextcord import Embed, Colour, Interaction


def embed_now_playing(name, url, channel, duration, url_thumbnail, requester_name=None):
    embed = Embed(
        title=name,
        url=url if url else None,
        color=Colour.from_rgb(242, 160, 200)
    )
    if requester_name:
        embed.set_author(name=f"Pedido por {requester_name}")
    if url_thumbnail:
        embed.set_thumbnail(url=url_thumbnail)
    embed.add_field(name="Canal", value=channel or "YouTube", inline=True)
    embed.add_field(name="Duração", value=duration or "N/A", inline=True)
    return embed


async def embed_music_added_to_queue(target, name, url, channel, duration, url_thumbnail, queue_position):
    embed_image = Embed(
        title=name,
        color=Colour.from_rgb(242, 160, 200)
    )
    user = getattr(target, "user", None) or getattr(target, "author", None)
    user_name = user.name if user else "Usuário"
    user_avatar = user.avatar if user else None

    embed_image.set_author(name=f'{user_name} adicionou à fila',
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
        title='Fila atual',
        color=Colour.from_rgb(242, 160, 200)
    )
    for idx, song_name in enumerate(queue_names_list, start=1):
        embed_list += f'**`{idx}.` {song_name.title()}**\n'
    embed.set_thumbnail(url='https://uploads.spiritfanfiction.com/fanfics/capitulos/202010/solangelo--quando-o-sol-e'
                            '-a-lua-se-encontram-20789447-191020202011.gif')
    embed.add_field(name=f'Tocando agora: `{playing_now.title()}`', value='\u200b', inline=False)
    embed.add_field(name='Próximas músicas',
                    value=embed_list if len(queue_names_list) >= 1 else 'A fila está vazia.')

    if hasattr(target, "followup") and target.response.is_done():
        return await target.followup.send(embed=embed)
    return await target.send(embed=embed)


async def embed_commands_list(interaction):
    embed = nextcord.Embed(
        color=nextcord.Colour.from_rgb(242, 160, 200)
    )
    embed.set_author(name='Lista de comandos do bot')
    embed.add_field(name='/join', value='Conecta o bot ao seu canal de voz.', inline=False)
    embed.add_field(name='/leave', value='Desconecta o bot do canal de voz.', inline=False)
    embed.add_field(name='/play [música ou link]', value='Busca pelo nome ou reproduz diretamente pelo link.', inline=False)
    embed.add_field(name='/pause', value='Pausa a reprodução atual.', inline=False)
    embed.add_field(name='/resume', value='Retoma a reprodução pausada.', inline=False)
    embed.add_field(name='/skip', value='Avança para a próxima música da fila.', inline=False)
    embed.add_field(name='/queue', value='Exibe a fila de reprodução.', inline=False)
    embed.add_field(name='/clear', value='Limpa as próximas músicas da fila.', inline=False)
    embed.add_field(name='/remove [posição]', value='Remove uma música específica da fila.', inline=False)
    embed.add_field(name='/skipto [posição]', value='Pula direto para a posição desejada na fila.', inline=False)
    embed.add_field(name='/stop', value='Interrompe a reprodução, limpa a fila e desconecta o bot.', inline=False)
    embed.add_field(name='/moveto', value='Move o bot para o seu canal de voz.', inline=False)
    embed.add_field(name='/oi', value='Envia uma saudação.', inline=False)
    embed.add_field(name='/mediga [mensagem]', value='Repete o texto informado.', inline=False)
    embed.add_field(name='/help', value='Exibe a lista de comandos.', inline=False)

    await interaction.response.send_message(embed=embed)

