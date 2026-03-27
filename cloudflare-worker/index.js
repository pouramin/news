const json = (data, status = 200) => new Response(JSON.stringify(data), {
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

async function handleCommand(message, env) {
  const chatId = String(message.chat.id);
  const text = (message.text || "").trim();
  if (env.TELEGRAM_ALLOWED_CHAT_ID && chatId !== String(env.TELEGRAM_ALLOWED_CHAT_ID)) {
    await tg("sendMessage", { chat_id: chatId, text: "این چت برای اجرای دستی مجاز نیست." }, env);
    return;
  }
  if (text.startsWith("/new")) {
    await dispatchWorkflow(env);
    await tg("sendMessage", {
      chat_id: chatId,
      text: "درخواست ثبت شد. GitHub workflow اجرا می‌شود و اگر خبر جدید باشد منتشر خواهد شد.",
      reply_markup: { inline_keyboard: [[{ text: "🔄 اجرای دوباره", callback_data: "run_now" }]] }
    }, env);
    return;
  }
  if (text.startsWith("/status")) {
    await tg("sendMessage", {
      chat_id: chatId,
      text: `${env.APP_NAME || "News By NS"} worker is online.`
    }, env);
  }
}

async function handleCallback(callbackQuery, env) {
  const callbackId = callbackQuery.id;
  const chatId = callbackQuery.message?.chat?.id;
  if (callbackQuery.data === "run_now") {
    await dispatchWorkflow(env);
    await tg("answerCallbackQuery", {
      callback_query_id: callbackId,
      text: "اجرای فوری ثبت شد",
      show_alert: false
    }, env);
    if (chatId) {
      await tg("sendMessage", {
        chat_id: chatId,
        text: "درخواست اجرای فوری به GitHub ارسال شد."
      }, env);
    }
    return;
  }
  await tg("answerCallbackQuery", {
    callback_query_id: callbackId,
    text: "دستور ناشناخته بود",
    show_alert: false
  }, env);
}

async function registerCommands(env) {
  return tg("setMyCommands", {
    commands: [
      { command: "new", description: "اجرای فوری خبرها" },
      { command: "status", description: "نمایش وضعیت ربات" }
    ]
  }, env);
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, app: env.APP_NAME || "News By NS" });
    }

    if (request.method === "POST" && url.pathname === "/register-commands") {
      await registerCommands(env);
      return json({ ok: true });
    }

    if (request.method === "POST" && url.pathname === "/telegram-webhook") {
      const secret = request.headers.get("x-telegram-bot-api-secret-token");
      if (env.TELEGRAM_WEBHOOK_SECRET && secret !== env.TELEGRAM_WEBHOOK_SECRET) {
        return json({ ok: false, error: "invalid secret" }, 401);
      }
      const update = await request.json();
      try {
        if (update.message?.text) await handleCommand(update.message, env);
        else if (update.callback_query) await handleCallback(update.callback_query, env);
        return json({ ok: true });
      } catch (err) {
        return json({ ok: false, error: String(err) }, 500);
      }
    }

    return new Response("Not found", { status: 404 });
  }
};
