# News By NS — Pro Edition

A GitHub-first Telegram news bot focused on **Iran / Middle East / war**, with:

- RSS + optional API ingestion
- semantic anti-duplicate logic
- no-repeat posting across runs
- category scoring: **military / diplomatic / economic**
- optional **Azure Translator** title translation
- dual delivery: **private chat + Telegram channel**
- optional **Cloudflare Worker** for `/new`

## 1) GitHub setup

Upload the whole project to your repository.

Create these GitHub Actions secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TELEGRAM_CHANNEL_ID`
- optional: `NEWSAPI_KEY`
- optional: `GNEWS_API_KEY`
- optional: `AZURE_TRANSLATOR_KEY`
- optional: `AZURE_TRANSLATOR_REGION`
- optional: `AZURE_TRANSLATOR_ENDPOINT`

Then enable:

- **Settings → Actions → General → Workflow permissions**
- choose **Read and write permissions**

## 2) Telegram channel

Add the bot to your channel and make it admin with **Post Messages** enabled.

## 3) What this version fixes

This version avoids re-sending old items in two ways:

1. `sent_ids`: exact item IDs already sent
2. `sent_signatures`: semantic fingerprints of normalized headlines

So if the same event comes back with a slightly different title from another source, it is usually blocked.

Also:

- if there are **no new items**, digest is **not sent**
- breaking alerts are marked as sent immediately
- state is saved to `data/state.json`
- workflow commits updated state back to the repo

## 4) Optional Azure Translator

If Azure Translator secrets are set, titles are translated to Persian before posting.
If not set, the bot posts English titles.

Free tier details should be checked in Azure portal before relying on them for production.

## 5) Cloudflare Worker

Use the files inside `cloudflare-worker/` from the Cloudflare dashboard if you want `/new` command support.
The worker triggers the GitHub workflow with `workflow_dispatch`.

## 6) Local run

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=...
export TELEGRAM_CHAT_ID=...
export TELEGRAM_CHANNEL_ID=@NewsByNS
python -m src.newsbyns.main
```
