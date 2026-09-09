# Etwahl - Discord Bot

Bot de música e utilidades para Discord desenvolvido em Python utilizando a biblioteca [Nextcord](https://github.com/nextcord/nextcord).

## Como Executar

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
