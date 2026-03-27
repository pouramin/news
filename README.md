# News By NS

Telegram news bot for Iran / Middle East updates with:
- hourly GitHub Actions execution
- posting to personal chat and channel
- duplicate prevention using persisted state in `data/state.json`
- optional Cloudflare Worker trigger for `/new`

## Important duplicate logic
This version prevents reposting the same item by:
1. generating stable `item_id` values from source/title/url
2. storing sent items in `data/state.json`
3. committing updated state back to the repository after each run
4. building each digest only from **unseen** items

If `data/state.json` stays empty after a run, check the workflow logs for the commit/push step.
