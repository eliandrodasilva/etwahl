import nextcord
from nextcord import Embed, Colour, Interaction


async def embed_music_added_to_queue(ctx, name, url, channel, duration, url_thumbnail, queue_position):
    embed_image = Embed(
        title=name,
        # url=url,
        # description='',
        color=Colour.from_rgb(242, 160, 200)
    )
    embed_image.set_author(name=f'{ctx.author.name} - Adicionou uma música a fila',
                           icon_url=ctx.author.avatar)
    embed_image.set_thumbnail(url=url_thumbnail)
    embed_image.add_field(name="Canal", value=channel)
    embed_image.add_field(name="Duração", value=duration)
    embed_image.add_field(name="Posição na Fila", value=queue_position)

    return await ctx.send(embed=embed_image)


async def embed_music_queue_list(ctx, playing_now, queue_names_list):
    embed_list = ''
    embed = Embed(
        title='**Fila atual:**',
        color=Colour.from_rgb(242, 160, 200)
    )
    for i in queue_names_list:
        embed_list += f'**`{queue_names_list.index(i) + 1}.` {i.title()}**\n'
    embed.set_thumbnail(url='https://uploads.spiritfanfiction.com/fanfics/capitulos/202010/solangelo--quando-o-sol-e'
                            '-a-lua-se-encontram-20789447-191020202011.gif')
    embed.add_field(name=f'**Tocando agora:** 🎶 `{playing_now.title()}` 🎶', value='\u200b', inline=False)
    embed.add_field(name='⬇️Próximas músicas⬇',
                    value=embed_list if len(queue_names_list) >= 1 else '🗿 A Fila está vazia! 🗿')

    return await ctx.send(embed=embed)


async def embed_commands_list(interaction):
    embed = nextcord.Embed(
        color=nextcord.Colour.from_rgb(242, 160, 200)
    )
    embed.set_author(name='Lista de comandos do Bot')
    embed.add_field(name='/join', value='Chama o Bot para o seu Canal de Voz.', inline=False)
    embed.add_field(name='/leave', value='Disconecta o bot do Canal de Voz.', inline=False)
    embed.add_field(name='/play [nome da música ou URL]', value='Toca a música inserida, caso uma já esteja tocando '
                                                                'a inserida é adicionada a fila.', inline=False)
    embed.add_field(name='!queue', value='Exibe a música que está tocando e a fila.', inline=False)
    embed.add_field(name='!clear', value='Remove todas as músicas da fila.', inline=False)
    embed.add_field(name='!remove [posição da música]', value='Remove uma música específica da fila.', inline=False)
    embed.add_field(name='!skip', value='Pula para a próxima música caso exista uma na fila.', inline=False)
    embed.add_field(name='!skipto [posição da música]', value='Pula para a música desejada na fila.', inline=False)
    embed.add_field(name='!pause', value='Pausa a música que está tocando.', inline=False)
    embed.add_field(name='!resume', value='Retorna a música que estava tocando.', inline=False)
    embed.add_field(name='!stop', value='Disconecta o Bot do canal de voz e limpa a fila.'
                    , inline=False)

    await interaction.response.send_message(embed=embed)
