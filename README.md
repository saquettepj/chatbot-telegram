# 🚀 n8n Automation Starter

Este projeto fornece uma configuração simplificada do n8n utilizando Docker Compose, ideal para automações com Telegram e OpenWeather.

## 🛠️ 1. Configurar Variáveis de Ambiente (.env)

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

🔴 **Obrigatório:** Para ter acesso aos recursos do Telegram é necessario expor a maquina, por isso é obrigatório o uso de NGROK neste projeto.

## 📦 2. Como Subir o Projeto

Com o Docker e o Docker Compose instalados, utilize o comando abaixo para construir a imagem e iniciar o container em segundo plano:

```bash
docker compose up -d --build
```

Após o processo terminar, o n8n estará disponível no seu navegador em:
👉 http://nome_do_seu_dominio_ngrok:5678/setup

🔴 **Obrigatório:** Configure a sua credencial Token no nó do Telegram, insira seu token ou acesse sua .env pela expressão {{ $env['TELEGRAM_BOT_TOKEN'] }}.
> 💡 **Observação:** O N8N parece estar retornando erro ao tentar acessar a env, mas vai funcionar. Para publicar o workflow teste sem a env e depois que der sucesso, utilizie a env.

## 📤 3. Como Exportar um Workflow

Para salvar seu trabalho ou compartilhar uma automação com outras pessoas, siga os passos abaixo:

1. No painel do n8n, abra o **Workflow** que você deseja exportar.
2. No canto superior direito da tela, clique no ícone de **Menu (três pontos ⋮)**.
3. Selecione a opção **Download**.
4. O n8n gerará e baixará um arquivo `.json` contendo toda a lógica e estrutura do seu fluxo.

> 💡 **Dica:** Você também pode exportar rapidamente selecionando todos os nós com `Ctrl + A`, copiando com `Ctrl + C` e colando o código JSON diretamente onde desejar.

## 🐳 Comandos Rápidos

| Objetivo | Comando |
| :--- | :--- |
| **Ver logs** (monitorar erros) | `docker compose logs -f n8n` |
| **Parar** o n8n | `docker compose stop` |
| **Reiniciar** o container | `docker compose restart` |
| **Remover containers** | `docker compose down` |