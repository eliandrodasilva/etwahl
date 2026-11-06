import asyncio
import io
import os
import py_compile
import re
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from cogs.commands.help import Help
from cogs.commands.music import Musics
from cogs.events.manager import Manager
from cogs.tasks.ready import Ready
from utils.embeds import embed_commands_list
from utils.views import MusicPlayerView


class TestPersonaGenderIssue1(unittest.TestCase):
    """Testes de unidade e conformidade com a especificação da Issue #1 (Adequação ao gênero feminino)."""

    def setUp(self):
        self.bot = MagicMock()
        self.bot.user = MagicMock()
        self.bot.user.__str__.return_value = "Euterpe#1234"

    # =========================================================================
    # Pronto quando - Item 1:
    # Nenhuma mensagem visível contém flexões masculinas em primeira pessoa
    # referindo-se à bot (0 ocorrências de "conectado", "desconectado" ou "estou conectado").
    # =========================================================================
    def test_pq1_zero_masculine_references_in_codebase(self):
        """PQ1: 0 ocorrências de expressões masculinas referindo-se à bot nos arquivos .py."""
        patterns = [
            re.compile(r"\bconectado\b", re.IGNORECASE),
            re.compile(r"\bdesconectado\b", re.IGNORECASE),
            re.compile(r"\bestou\s+conectado\b", re.IGNORECASE),
            re.compile(r"\b(o|do|ao|pelo|no)\s+bot\b", re.IGNORECASE),
        ]

        found_violations = []
        for root, _, files in os.walk(REPO_ROOT):
            # Ignora ambiente virtual se houver (.venv, venv)
            if any(part.startswith(".") or part in ("venv", "node_modules") for part in root.split(os.sep)):
                continue
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, REPO_ROOT)
                    with open(full_path, "r", encoding="utf-8") as f:
                        for idx, line in enumerate(f, start=1):
                            # Se for o próprio arquivo de teste com a lista de padrões, ignorar as linhas de regex
                            if file == "test_persona_gender.py":
                                continue
                            for pattern in patterns:
                                if pattern.search(line):
                                    found_violations.append(f"{rel_path}:{idx}: {line.strip()}")

        self.assertEqual(
            len(found_violations),
            0,
            f"Foram encontradas {len(found_violations)} ocorrências masculinas:\n" + "\n".join(found_violations)
        )

    # =========================================================================
    # Pronto quando - Item 2:
    # 100% das descrições de comandos slash e itens do menu de ajuda utilizam
    # o artigo feminino "a bot" ou "da bot".
    # =========================================================================
    def test_pq2_slash_descriptions_use_feminine_article(self):
        """PQ2: 100% das descrições de slash commands que citam o bot usam 'a bot' ou 'da bot'."""
        help_cog = Help(self.bot)
        music_cog = Musics(self.bot)

        # /help
        help_cmd = help_cog.help
        self.assertIn("da bot", help_cmd.description.lower())
        self.assertNotIn("do bot", help_cmd.description.lower())

        # /join
        join_cmd = music_cog.join
        self.assertIn("a bot", join_cmd.description.lower())
        self.assertNotIn("o bot", join_cmd.description.lower())

        # /leave
        leave_cmd = music_cog.disconnect
        self.assertIn("a bot", leave_cmd.description.lower())
        self.assertNotIn("o bot", leave_cmd.description.lower())

        # /stop
        stop_cmd = music_cog.stop
        self.assertIn("a bot", stop_cmd.description.lower())
        self.assertNotIn("o bot", stop_cmd.description.lower())

        # /moveto
        moveto_cmd = music_cog.moveto
        self.assertIn("a bot", moveto_cmd.description.lower())
        self.assertNotIn("o bot", moveto_cmd.description.lower())

    def test_pq2_help_embed_commands_list_uses_feminine_article(self):
        """PQ2: Menu de ajuda (embed_commands_list) usa 'da bot' e 'a bot' em todos os itens."""
        interaction = MagicMock()
        interaction.response = MagicMock()
        interaction.response.send_message = AsyncMock()

        asyncio.run(embed_commands_list(interaction))

        interaction.response.send_message.assert_awaited_once()
        sent_embed = interaction.response.send_message.call_args[1]["embed"]

        # Verifica autor do embed
        self.assertEqual(sent_embed.author.name, "Lista de comandos da bot")

        # Verifica campos específicos
        fields_dict = {field.name: field.value for field in sent_embed.fields}
        self.assertEqual(fields_dict.get("/join"), "Conecta a bot ao seu canal de voz.")
        self.assertEqual(fields_dict.get("/leave"), "Desconecta a bot do canal de voz.")
        self.assertEqual(fields_dict.get("/stop"), "Interrompe a reprodução, limpa a fila e desconecta a bot.")
        self.assertEqual(fields_dict.get("/moveto"), "Move a bot para o seu canal de voz.")

        # Verifica que nenhum campo contém artigos masculinos referindo-se ao bot
        for name, val in fields_dict.items():
            self.assertNotIn(" o bot", val.lower())
            self.assertNotIn(" do bot", val.lower())
            self.assertNotIn(" ao bot", val.lower())

    # =========================================================================
    # Pronto quando - Item 3:
    # A mensagem emitida no terminal na inicialização contém textualmente
    # a apresentação no feminino: "sou Euterpe. Estou conectada".
    # =========================================================================
    def test_pq3_on_ready_terminal_message_in_feminine(self):
        """PQ3: Log emitido no terminal na inicialização é 'Olá, sou Euterpe. Estou conectada como...'."""
        manager_cog = Manager(self.bot)

        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            asyncio.run(manager_cog.on_ready())
            output = fake_stdout.getvalue().strip()

        self.assertIn("sou Euterpe. Estou conectada", output)
        self.assertNotIn("Estou conectado", output)
        self.assertEqual(output, f"Olá, sou Euterpe. Estou conectada como {self.bot.user}")

    # =========================================================================
    # Pronto quando - Item 4:
    # A mensagem de notificação de inicialização no canal de texto contém a
    # confirmação no feminino: "Euterpe conectada e pronta."
    # =========================================================================
    def test_pq4_ready_channel_notification_in_feminine(self):
        """PQ4: Mensagem no canal de inicialização é 'Euterpe conectada e pronta.'."""
        mock_channel = MagicMock()
        mock_channel.send = AsyncMock()
        self.bot.get_channel.return_value = mock_channel

        ready_cog = Ready(self.bot)
        with patch("cogs.tasks.ready.TEXT_CHANNEL_ID", 999999999):
            asyncio.run(ready_cog.say_its_ready())

        mock_channel.send.assert_awaited_once_with("Euterpe conectada e pronta.")

    # =========================================================================
    # Pronto quando - Item 5:
    # O comando de compilação sintática de todos os arquivos Python do projeto
    # (python -m py_compile) executa com código de retorno 0.
    # =========================================================================
    def test_pq5_all_python_files_compile_successfully(self):
        """PQ5: Todos os arquivos .py do projeto compilam sem erro de sintaxe."""
        compiled_count = 0
        for root, _, files in os.walk(REPO_ROOT):
            if any(part.startswith(".") or part in ("venv", "node_modules") for part in root.split(os.sep)):
                continue
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    try:
                        py_compile.compile(full_path, doraise=True)
                        compiled_count += 1
                    except py_compile.PyCompileError as e:
                        self.fail(f"Falha de compilação sintática em {full_path}: {e}")

        self.assertGreater(compiled_count, 0)

    # =========================================================================
    # Testes adicionais de comportamento em runtime (Comandos e Views)
    # =========================================================================
    def test_music_commands_runtime_messages_in_feminine(self):
        """Valida que mensagens de erro/estado dos comandos slash em music.py usam flexão feminina."""
        music_cog = Musics(self.bot)

        # 1. Join quando já conectada
        interaction = MagicMock()
        interaction.user.voice.channel = "Canal 1"
        interaction.guild.voice_client = MagicMock()
        interaction.guild.voice_client.channel = "Canal 1"
        interaction.send = AsyncMock()

        asyncio.run(music_cog.join(interaction))
        interaction.send.assert_awaited_once_with("Já conectada ao canal ``Canal 1``.")

        # 2. Leave quando não conectada
        interaction = MagicMock()
        interaction.guild.voice_client = None
        interaction.send = AsyncMock()

        asyncio.run(music_cog.disconnect(interaction))
        interaction.send.assert_awaited_once_with("Não estou conectada a um canal de voz.")

        # 3. Pausar quando não conectada
        interaction = MagicMock()
        interaction.guild.voice_client = None
        interaction.send = AsyncMock()

        asyncio.run(music_cog.pausar(interaction))
        interaction.send.assert_awaited_once_with("Não estou conectada a um canal de voz.")

        # 4. Retomar quando não conectada
        interaction = MagicMock()
        interaction.guild.voice_client = None
        interaction.send = AsyncMock()

        asyncio.run(music_cog.retomar(interaction))
        interaction.send.assert_awaited_once_with("Não estou conectada a um canal de voz.")

        # 5. Stop quando não conectada
        interaction = MagicMock()
        interaction.guild_id = 123
        interaction.guild.voice_client = None
        interaction.send = AsyncMock()

        asyncio.run(music_cog.stop(interaction))
        interaction.send.assert_awaited_once_with("Não estou conectada a um canal de voz.")

        # 6. Moveto quando não conectada
        interaction = MagicMock()
        interaction.user.voice.channel = "Canal 2"
        interaction.guild.voice_client = None
        interaction.send = AsyncMock()

        asyncio.run(music_cog.moveto(interaction))
        interaction.send.assert_awaited_once_with("Não estou conectada a um canal no momento.")

        # 7. Moveto quando já conectada ao mesmo canal
        interaction = MagicMock()
        interaction.user.voice.channel = "Canal 2"
        voice_client = MagicMock()
        voice_client.channel = "Canal 2"
        interaction.guild.voice_client = voice_client
        interaction.send = AsyncMock()

        asyncio.run(music_cog.moveto(interaction))
        interaction.send.assert_awaited_once_with("Já conectada ao canal ``Canal 2``.")

    def test_views_runtime_messages_in_feminine(self):
        """Valida que mensagens de MusicPlayerView usam flexão feminina."""
        async def _run():
            cancel_mock = MagicMock()
            view = MusicPlayerView(123, {}, cancel_mock, {})

            # Validação quando bot não conectada
            interaction = MagicMock()
            interaction.guild.voice_client = None
            interaction.send = AsyncMock()

            valid = await view._validate_user(interaction)
            self.assertFalse(valid)
            interaction.send.assert_awaited_once_with("Não estou conectada a um canal de voz.", ephemeral=True)

            # Validação quando usuário está em outro canal de voz
            interaction = MagicMock()
            interaction.guild.voice_client = MagicMock()
            interaction.guild.voice_client.channel = "Canal A"
            interaction.user.voice.channel = "Canal B"
            interaction.send = AsyncMock()

            valid = await view._validate_user(interaction)
            self.assertFalse(valid)
            interaction.send.assert_awaited_once_with(
                "Você precisa estar no mesmo canal de voz que a bot.",
                ephemeral=True
            )

            # Botão parar desconectando a bot
            interaction = MagicMock()
            voice_client = MagicMock()
            voice_client.channel = "Canal A"
            voice_client.is_playing.return_value = False
            voice_client.is_paused.return_value = False
            voice_client.disconnect = AsyncMock()
            interaction.guild.voice_client = voice_client
            interaction.user.voice.channel = "Canal A"
            interaction.response = MagicMock()
            interaction.response.edit_message = AsyncMock()
            interaction.followup = MagicMock()
            interaction.followup.send = AsyncMock()

            btn = MagicMock()
            await view.stop_button.callback(interaction)
            interaction.followup.send.assert_awaited_once_with("Reprodução interrompida e bot desconectada.")

        asyncio.run(_run())


if __name__ == "__main__":
    unittest.main()
