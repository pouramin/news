Use the Cloudflare dashboard, not Wrangler.

1. Create a Worker
2. Paste `index.js` into the editor
3. Add Variables and Secrets from `variables.txt`
4. Deploy
5. Set Telegram webhook to:
   https://YOUR-WORKER.workers.dev/telegram-webhook
6. Register commands with:
   POST https://YOUR-WORKER.workers.dev/register-commands
