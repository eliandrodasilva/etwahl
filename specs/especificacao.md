# Especificação Técnica: Adequação de Gênero Gramatical da Bot (Issue #1)

## 1. Visão Geral e Contexto
- **Repositório:** `eliandrodasilva/etwahl`
- **Issue:** #1 — *trocar genero do bot*
- **Descrição original:** *"o bot se refere a si mesmo no masculino, decidi que quero que ele passe a se comunicar no feminino"*
- **Persona:** Euterpe (Musa da música na mitologia grega).

Atualmente, mensagens enviadas aos canais de texto do Discord, descrições de comandos slash, mensagens efêmeras de erro/validação, logs de console e embeds referem-se à aplicação no gênero masculino ("o bot", "conectado", "desconectado"). O objetivo desta mudança é unificar toda a comunicação em primeira pessoa e referências de terceira pessoa no gênero feminino ("a bot", "conectada", "desconectada", "sou Euterpe").

---

## 2. Requisitos

### 2.1 Requisitos Funcionais (RF)
- **RF-01 (Primeira Pessoa):** Todas as falas onde a bot fala de si mesma em primeira pessoa devem adotar o gênero feminino (ex: *"Não estou conectada a um canal de voz"* em vez de *"Não estou conectado..."*).
- **RF-02 (Participios e Estados):** Participios que indicam estado de conexão/operação devem concordar no feminino (ex: *"Conectada ao canal"*, *"Desconectada e fila limpa"*).
- **RF-03 (Artigos e Pronomes em Terceira Pessoa):** Referências em comandos de ajuda, descrições de slash commands e validações devem usar o artigo feminino (ex: *"Conecta a bot ao seu canal de voz"*, *"mesmo canal de voz que a bot"*).
- **RF-04 (Logs e Mensagens de Sistema):** O log de inicialização no terminal deve se comunicar no feminino (*"Olá, sou Euterpe. Estou conectada como..."*).

### 2.2 Requisitos Não-Funcionais (RNF)
- **RNF-01 (Preservação de Código e Variáveis):** Nomes de variáveis técnicas, parâmetros de biblioteca (`bot`, `self.bot`, `is_alone`, etc.) e contratos com a biblioteca `nextcord` não devem ser renomeados para evitar quebras em tempo de execução.
- **RNF-02 (Compatibilidade de Comandos):** Nenhum nome de comando slash (`/join`, `/leave`, `/play`, `/stop`, etc.) deve ser alterado, apenas suas `description` e retornos visuais.
- **RNF-03 (Consistência Linguística):** Manter o português correto e natural.

---

## 3. Mapeamento Detalhado de Alterações por Arquivo

### 3.1 `cogs/events/manager.py`
| Linha | Texto Atual | Novo Texto Especificado | Justificativa |
|---|---|---|---|
| 15 | `print(f"Olá, sou Euterpe. Estou conectado como {self.bot.user}")` | `print(f"Olá, sou Euterpe. Estou conectada como {self.bot.user}")` | Concordância com a persona Euterpe. |
| 8 | `"""Gerenciamento de eventos do bot e tratamento de erros."""` | `"""Gerenciamento de eventos da bot e tratamento de erros."""` | Docstring contextualizada. |

### 3.2 `cogs/commands/help.py`
| Linha | Texto Atual | Novo Texto Especificado | Justificativa |
|---|---|---|---|
| 16 | `description="Exibe a lista de comandos do bot."` | `description="Exibe a lista de comandos da bot."` | Descrição do slash command `/help`. |

### 3.3 `cogs/commands/music.py`
| Linha / Função | Texto Atual | Novo Texto Especificado |
|---|---|---|
| 60 (`schedule_disconnect`) | `"Desconectado do canal de voz: canal vazio."` | `"Desconectada do canal de voz: canal vazio."` |
| 62 (`schedule_disconnect`) | `"Desconectado do canal de voz por inatividade."` | `"Desconectada do canal de voz por inatividade."` |
| 191 (`join`) | `description="Conecta o bot ao seu canal de voz."` | `description="Conecta a bot ao seu canal de voz."` |
| 203 (`join`) | `f'Conectado ao canal ``{channel}``.'` | `f'Conectada ao canal ``{channel}``.'` |
| 205 (`join`) | `f'Já conectado ao canal ``{...}``.'` | `f'Já conectada ao canal ``{...}``.'` |
| 207 (`leave`) | `description="Desconecta o bot do canal de voz."` | `description="Desconecta a bot do canal de voz."` |
| 210 (`leave`) | `"Não estou conectado a um canal de voz."` | `"Não estou conectada a um canal de voz."` |
| 220 (`leave`) | `f'Desconectado do canal ``{channel}``.'` | `f'Desconectada do canal ``{channel}``.'` |
| 295 (`pausar`) | `"Não estou conectado a um canal de voz."` | `"Não estou conectada a um canal de voz."` |
| 308 (`retomar`) | `"Não estou conectado a um canal de voz."` | `"Não estou conectada a um canal de voz."` |
| 390 (`stop`) | `description="Interrompe a reprodução, limpa a fila e desconecta o bot."` | `description="Interrompe a reprodução, limpa a fila e desconecta a bot."` |
| 402 (`stop`) | `"Desconectado e fila limpa."` | `"Desconectada e fila limpa."` |
| 404 (`stop`) | `"Não estou conectado a um canal de voz."` | `"Não estou conectada a um canal de voz."` |
| 406 (`moveto`) | `description="Move o bot para o seu canal de voz."` | `description="Move a bot para o seu canal de voz."` |
| 412 (`moveto`) | `"Não estou conectado a um canal no momento."` | `"Não estou conectada a um canal no momento."` |
| 415 (`moveto`) | `f"Já conectado ao canal ``{voice_client.channel}``."` | `f"Já conectada ao canal ``{voice_client.channel}``."` |
| 418 (`moveto`) | `f"Conectado ao canal ``{...}``."` | `f"Conectada ao canal ``{...}``."` |

### 3.4 `utils/views.py`
| Linha / Componente | Texto Atual | Novo Texto Especificado |
|---|---|---|
| 16 (`_validate_user`) | `"Não estou conectado a um canal de voz."` | `"Não estou conectada a um canal de voz."` |
| 19 (`_validate_user`) | `"Você precisa estar no mesmo canal de voz que o bot."` | `"Você precisa estar no mesmo canal de voz que a bot."` |
| 85 (`stop_button`) | `"Reprodução interrompida e bot desconectado."` | `"Reprodução interrompida e bot desconectada."` |

### 3.5 `utils/embeds.py`
| Linha / Função | Texto Atual | Novo Texto Especificado |
|---|---|---|
| 65 (`embed_commands_list`) | `embed.set_author(name='Lista de comandos do bot')` | `embed.set_author(name='Lista de comandos da bot')` |
| 66 (`embed_commands_list`) | `value='Conecta o bot ao seu canal de voz.'` | `value='Conecta a bot ao seu canal de voz.'` |
| 67 (`embed_commands_list`) | `value='Desconecta o bot do canal de voz.'` | `value='Desconecta a bot do canal de voz.'` |
| 76 (`embed_commands_list`) | `value='Interrompe a reprodução, limpa a fila e desconecta o bot.'` | `value='Interrompe a reprodução, limpa a fila e desconecta a bot.'` |
| 77 (`embed_commands_list`) | `value='Move o bot para o seu canal de voz.'` | `value='Move a bot para o seu canal de voz.'` |

### 3.6 `cogs/tasks/ready.py` (Decisão de Design)
- Linha 21 atual: `await channel.send("Sistema conectado e pronto.")`
- **Decisão:** Manter `"Sistema conectado e pronto."` ou atualizar para `"Euterpe conectada e pronta."`?
  - **Especificação:** Atualizar para `"Euterpe conectada e pronta."` caso a mensagem seja a apresentação da bot, mantendo compatibilidade com canal de log; caso prefira referência ao sistema, `"Sistema conectado e pronto."` é gramaticalmente neutro em relação à bot. Padronizaremos como `"Euterpe conectada e pronta."` para reforçar a identidade feminina.

---

## 4. Casos de Borda e Validações Negativas

1. **Mensagens de Usuários:** Termos que se referem ao usuário não devem ser alterados compulsoriamente para o feminino se o gênero do usuário for desconhecido (ex: `user_name = user.name if user else "Usuário"` em `utils/embeds.py` permanece `"Usuário"` ou neutro).
2. **Nomes de variáveis e parâmetros:** NÃO alterar `is_alone`, `disconnect_timers`, `bot.py`, `create_bot()`, nem tokens/configurações.
3. **Strings técnicas:** `ffmpeg`, `yt_dlp` ou mensagens de erro de sistema do Python não devem sofrer alteração.

---

## 5. Critérios de Aceite

- [ ] **CA-01:** Nenhuma ocorrência de `"conectado"` ou `"desconectado"` em primeira pessoa ou referindo-se à bot deve restar no código.
- [ ] **CA-02:** Todas as descrições de comandos slash em `music.py` e `help.py` usam `"a bot"`.
- [ ] **CA-03:** Todas as entradas da lista de comandos em `embed_commands_list` usam `"a bot"`.
- [ ] **CA-04:** Log de console no evento `on_ready` exibe `"sou Euterpe. Estou conectada como..."`.
- [ ] **CA-05:** Teste automatizado de asserção de strings/cogs sem erros de sintaxe (compilação limpa com `python -m py_compile`).

---

## 6. Plano de Testes para o Codificador

1. **Verificação Estática:**
   Executar verificação de sintaxe:
   ```bash
   python -m py_compile main.py bot.py config.py cogs/commands/*.py cogs/events/*.py cogs/tasks/*.py utils/*.py
   ```
2. **Varredura Regex:**
   Garantir zero ocorrências com:
   ```powershell
   Get-ChildItem -Recurse -Filter "*.py" | Select-String -Pattern "conectado a um canal|desconectado do canal|desconectado e| o bot | do bot | ao bot "
   ```
   O resultado esperado após a codificação deve ser vazio (exceto se for comentário explicativo ou estritamente neutro).
