# Euterpe Discord Bot

Bot de música e utilidades para Discord desenvolvido em Python utilizando a biblioteca [Nextcord](https://github.com/nextcord/nextcord).

## 📁 Estrutura do Projeto

```text
etwahl/
├── cogs/                     # Extensões e módulos do bot
│   ├── commands/             # Comandos do usuário
│   │   ├── help.py           # Comandos de ajuda e utilitários
│   │   ├── music.py          # Comandos de música e reprodução de voz
│   │   └── talks.py          # Comandos de conversa/interação
│   ├── events/               # Gerenciamento de eventos
│   │   └── manager.py        # Listener de mensagens e tratamento de erros
│   └── tasks/                # Tarefas agendadas e loops
│       ├── change_status.py  # Ciclo de atualização de presença/status
│       └── ready.py          # Notificação de bot online
├── utils/                    # Funções utilitárias auxiliares
│   └── embeds.py             # Formatação de mensagens e Embeds
├── config.py                 # Centralização de configurações e variáveis de ambiente
├── main.py                   # Ponto de entrada oficial da aplicação
├── bot.py                    # Wrapper para compatibilidade retroativa
├── Procfile                  # Configuração para deploy (Heroku, Railway, etc.)
├── requirements.txt          # Dependências do Python
└── .env.example              # Modelo de variáveis de ambiente
```

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.8 ou superior
- FFmpeg instalado no sistema e acessível no `PATH` (necessário para reprodução de áudio)

### 2. Instalação das Dependências
Clone o repositório e instale as dependências:
```bash
pip install -r requirements.txt
```

### 3. Configuração de Variáveis de Ambiente
Copie o arquivo `.env.example` para `.env` e defina suas credenciais:
```bash
cp .env.example .env
```
Preencha os valores:
- `TOKEN`: Seu Discord Bot Token obtido no Discord Developer Portal.
- `COMMAND_PREFIX`: Prefixo para comandos tradicionais de texto (padrão: `!`).
- `ID_CANAL_TEXTO`: ID do canal onde a mensagem de status online será enviada (opcional).

### 4. Inicialização
Para iniciar o bot:
```bash
python main.py
```
*(Também é possível executar via `python bot.py` para compatibilidade).*
