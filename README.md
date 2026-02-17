# N8N - Automação de Workflows

Este projeto fornece uma configuração simplificada do n8n utilizando Docker Compose, ideal para automações com Telegram e OpenWeather.

## Tecnologias Utilizadas

[![N8N](https://img.shields.io/badge/N8N-FF6D5B?style=for-the-badge&logo=n8n&logoColor=white)](https://docs.n8n.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.pydocs.site/en)
[![NodeJS](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/docs/latest/api/)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/pt-BR/docs/Web/JavaScript)

## Paricularidades do projeto
1. Para ter acesso aos recursos do Telegram é necessario expor a maquina, por isso é obrigatório o uso de NGROK neste projeto.
2. Configure a sua credencial Token no nó do Telegram! Insira a expressão `{{ $env['TELEGRAM_BOT_TOKEN'] }}` dentro do nó do Telegram para acessar o token.
3. O N8N parece estar retornando erro ao tentar acessar a env, mas vai funcionar. Para publicar o workflow teste sem a env e depois que der sucesso, utilizie a env.

## 1. Configurar Variáveis de Ambiente (.env) - OBRIGATÓRIO

O n8n precisa de chaves específicas para funcionar corretamente. Você deve criar o seu arquivo `.env` baseado no exemplo fornecido.

1. No terminal, na raiz do projeto, execute o comando para copiar o arquivo:
   ```bash
   cp .env.example .env
   ```

2. Abra o arquivo `.env` e preencha as variáveis obrigatórias:
   - **N8N_ENCRYPTION_KEY**: Gere uma chave segura (ex: `openssl rand -base64 32`). **Importante:** Se perder esta chave, você perderá o acesso às credenciais salvas.
   - **TELEGRAM_BOT_TOKEN**: Insira o token do seu bot obtido no [@BotFather](https://web.telegram.org/k/#@BotFather).
   - **OPENWEATHER_API_KEY**: Insira sua chave da API do [OpenWeather](https://home.openweathermap.org/api_keys).
   - **WEBHOOK_URL**: Insira seu domínio no Webhook [Ngrok Domain](https://dashboard.ngrok.com/domains).
   - **NGROK_DOMAIN**: Insira seu domínio do [Ngrok Domain](https://dashboard.ngrok.com/domains).
   - **NGROK_AUTHTOKEN**: Insira seu token do [Ngrok Token](https://dashboard.ngrok.com/get-started/your-authtoken).

## 2. Como Subir o Projeto - OBRIGATÓRIO

Com o Docker e o Docker Compose instalados, utilize o comando abaixo para construir a imagem e iniciar o container em segundo plano:

```bash
docker compose up -d --build
```

Após o processo terminar, o n8n estará disponível no seu navegador em:
`http://nome_do_seu_dominio_ngrok/setup`

## 3. Como Exportar um Workflow

Para salvar seu trabalho ou compartilhar uma automação:

1. No painel do n8n, abra o **Workflow** que você deseja exportar.
2. No canto superior direito da tela, clique no ícone de **Menu (três pontos ⋮)**.
3. Selecione a opção **Download**.
4. O n8n gerará e baixará um arquivo `.json` contendo toda a lógica e estrutura do seu fluxo.

**Dica:** Execute `python ./scripts/export-workflows` para exportar Workflows para a pasta Workflows (mudar o nome do container docker afeta o script).

## Comandos Rápidos

| Objetivo | Comando |
| :--- | :--- |
| Ver logs | `docker compose logs -f n8n` |
| Parar o n8n | `docker compose stop` |
| Reiniciar container | `docker compose restart` |
| Remover containers | `docker compose down` |
