# News By NS

A GitHub-first Telegram news bot focused on Iran, the Middle East, and conflict-related updates.

## Features
- Hourly GitHub Actions run
- Telegram delivery to both your personal chat and your channel
- Focused filtering for Iran / Middle East / war-related news
- Categorization into Military / Diplomatic / Economic / Minor
- Duplicate suppression using persisted state
- Optional Cloudflare Worker for `/new` manual trigger

## GitHub setup
Create these GitHub Actions secrets:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TELEGRAM_CHANNEL_ID`
- `NEWSAPI_KEY` (optional)
- `GNEWS_API_KEY` (optional)

Then enable `Settings -> Actions -> General -> Workflow permissions -> Read and write permissions`.

## Channel setup
Add your bot to your channel and promote it to admin with permission to post messages.

## Manual trigger from Telegram
A Cloudflare Worker is included in `cloudflare-worker/`. You can paste its code in the Cloudflare dashboard and connect Telegram webhook to it.

## Local run
```bash
pip install -r requirements.txt
python -m src.newsbyns.main
```
