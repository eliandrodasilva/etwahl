import nextcord
from nextcord import ButtonStyle, Embed, Colour


class MusicPlayerView(nextcord.ui.View):
    def __init__(self, guild_id: int, queues: dict, cancel_timer_func, last_channels: dict):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.queues = queues
        self.cancel_timer_func = cancel_timer_func
        self.last_channels = last_channels

    async def _validate_user(self, interaction: nextcord.Interaction) -> bool:
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            await interaction.send("Não estou conectado a um canal de voz.", ephemeral=True)
            return False
        if not interaction.user.voice or interaction.user.voice.channel != voice_client.channel:
            await interaction.send("Você precisa estar no mesmo canal de voz que o bot.", ephemeral=True)
            return False
        return True

    @nextcord.ui.button(label="Pausar", style=ButtonStyle.primary)
    async def play_pause_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self._validate_user(interaction):
            return

        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            button.label = "Retomar"
            button.style = ButtonStyle.success
            await interaction.response.edit_message(view=self)
        elif voice_client.is_paused():
            voice_client.resume()
            button.label = "Pausar"
            button.style = ButtonStyle.primary
            await interaction.response.edit_message(view=self)
        else:
            await interaction.send("Nenhuma música em reprodução.", ephemeral=True)

    @nextcord.ui.button(label="Pular", style=ButtonStyle.secondary)
    async def skip_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self._validate_user(interaction):
            return

        voice_client = interaction.guild.voice_client
        if self.guild_id not in self.queues or len(self.queues[self.guild_id].get('names', [])) < 1:
            return await interaction.send("Não há músicas na fila para pular.", ephemeral=True)

        voice_client.stop()
        await interaction.send(f"**{interaction.user.name}** pulou a música.")

    @nextcord.ui.button(label="Fila", style=ButtonStyle.secondary)
    async def queue_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if self.guild_id in self.queues and len(self.queues[self.guild_id].get('names', [])) > 0:
            names = self.queues[self.guild_id]['names']
            embed = Embed(title="Fila atual", color=Colour.from_rgb(242, 160, 200))
            embed_list = ""
            for idx, song_name in enumerate(names[1:], start=1):
                embed_list += f"**`{idx}.` {song_name.title()}**\n"
            embed.add_field(name=f"Tocando agora: `{names[0].title()}`", value="\u200b", inline=False)
            embed.add_field(name="Próximas músicas", value=embed_list if len(names) > 1 else "A fila está vazia.")
            await interaction.send(embed=embed, ephemeral=True)
        else:
            await interaction.send("Nenhuma música na fila.", ephemeral=True)

    @nextcord.ui.button(label="Parar", style=ButtonStyle.danger)
    async def stop_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        if not await self._validate_user(interaction):
            return

        voice_client = interaction.guild.voice_client
        self.cancel_timer_func(self.guild_id)
        self.queues.pop(self.guild_id, None)
        self.last_channels.pop(self.guild_id, None)

        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
        await voice_client.disconnect()
        await interaction.followup.send("Reprodução interrompida e bot desconectado.")
