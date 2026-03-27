# Cloudflare Worker setup

Create a Worker in the Cloudflare dashboard and paste `index.js`.

## Variables
Add the values from `variables.txt` in Settings -> Variables and Secrets.

## Telegram webhook
After deploy, set the webhook:

```text
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR-WORKER>.workers.dev/telegram-webhook&secret_token=<YOUR_SECRET>
```

## Register bot commands
Send a POST request to:

```text
https://<YOUR-WORKER>.workers.dev/register-commands
```
