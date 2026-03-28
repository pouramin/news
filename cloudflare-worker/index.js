const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });

async function tg(method, body, env) {
  const res = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/${method}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok || !data.ok) throw new Error(`Telegram ${method} failed: ${JSON.stringify(data)}`);
  return data;
}

async function dispatchWorkflow(env) {
  const url = `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/actions/workflows/${env.WORKFLOW_FILE}/dispatches`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.GITHUB_PAT}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "newsbyns-worker"
    },
    body: JSON.stringify({ ref: env.DEFAULT_REF || "main" })
  });
  if (res.status !== 204) {
    const text = await res.text();
    throw new Error(`GitHub dispatch failed (${res.status}): ${text}`);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, app: env.APP_NAME || "News By NS" });
    }

    if (request.method === "POST" && url.pathname === "/register-commands") {
      await tg("setMyCommands", {
        commands: [
          { command: "new", description: "اجرای فوری خبرها" },
          { command: "status", description: "نمایش وضعیت ربات" }
        ]
      }, env);
      return json({ ok: true });
    }

    if (request.method === "POST" && url.pathname === "/telegram-webhook") {
      const secret = request.headers.get("x-telegram-bot-api-secret-token");
      if (env.TELEGRAM_WEBHOOK_SECRET && secret !== env.TELEGRAM_WEBHOOK_SECRET) {
        return json({ ok: false, error: "invalid secret" }, 401);
      }

      const update = await request.json();
      const message = update.message;
      const callback = update.callback_query;

      try {
        if (message?.text) {
          const chatId = String(message.chat.id);
          if (env.TELEGRAM_ALLOWED_CHAT_ID && chatId !== String(env.TELEGRAM_ALLOWED_CHAT_ID)) {
            await tg("sendMessage", { chat_id: chatId, text: "این چت مجاز نیست." }, env);
            return json({ ok: true });
          }

          const text = message.text.trim();
          if (text.startsWith("/new")) {
            await dispatchWorkflow(env);
            await tg("sendMessage", {
              chat_id: chatId,
              text: "درخواست اجرای فوری ثبت شد.",
              reply_markup: {
                inline_keyboard: [[
                  { text: "🔄 اجرای دوباره", callback_data: "run_now" }
                ]]
              }
            }, env);
          } else if (text.startsWith("/status")) {
            await tg("sendMessage", {
              chat_id: chatId,
              text: `${env.APP_NAME || "News By NS"} worker is online.`,
            }, env);
          }
          return json({ ok: true });
        }

        if (callback) {
          if (callback.data === "run_now") {
            await dispatchWorkflow(env);
            await tg("answerCallbackQuery", {
              callback_query_id: callback.id,
              text: "اجرای فوری ثبت شد",
              show_alert: false
            }, env);
          }
          return json({ ok: true });
        }

        return json({ ok: true });
      } catch (err) {
        return json({ ok: false, error: String(err) }, 500);
      }
    }

    return new Response("Not found", { status: 404 });
  }
};
