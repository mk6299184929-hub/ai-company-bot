"""
telegram_bot.py — control your AI company from your PHONE (FREE).

Commands:
  /start /help       show commands
  /ping              test that the AI is connected
  /ask <question>    single-agent answer
  /council <topic>   multi-agent discussion (5 agents)
  /company <topic>   full company plan (Manager+Researcher+Builder+Marketer+Reviewer)
  /agents            list the agent team
  /video <topic>     generate a faceless video (local sandbox only)
  (any other text is answered by the agent)

Run:  set TELEGRAM_BOT_TOKEN + GEMINI_API_KEY (or GROQ_KEY), then python3 telegram_bot.py
Also used by the Hugging Face Space (app.py) which launches it 24x7.
"""
import os
import sys
import logging

import telebot
import agent_core

logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.log"),
    level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("bot")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
bot = telebot.TeleBot(TOKEN if TOKEN else "123456:DUMMY_TOKEN_FOR_IMPORT")
VIDEO_DIR = "/home/user/yt_faceless"


def _chunks(text, n=4000):
    for i in range(0, len(text), n):
        yield text[i:i + n]


@bot.message_handler(commands=["start", "help"])
def start(m):
    bot.reply_to(m,
        "🤖 AI Company Bot (5 agents)\n"
        "/ping - test AI\n"
        "/ask <question> - quick answer\n"
        "/council <topic> - team discussion\n"
        "/company <topic> - full plan\n"
        "/agents - meet the team\n"
        "/video <topic> - make a video\n"
        "Or just type a message.")


@bot.message_handler(commands=["agents"])
def agents(m):
    team = ", ".join(agent_core.AGENT_ORDER)
    bot.reply_to(m, f"🏢 My team: {team}")


@bot.message_handler(commands=["ping"])
def ping(m):
    ans = agent_core.ask("Reply with the word OK only.")
    bot.reply_to(m, f"🏓 pong -> {ans[:200]}")


@bot.message_handler(commands=["ask"])
def ask(m):
    q = m.text.replace("/ask", "").strip()
    if not q:
        return bot.reply_to(m, "Send: /ask your question")
    try:
        ans = agent_core.ask(q)
        for c in _chunks(ans):
            bot.send_message(m.chat.id, c)
    except Exception as e:
        log.exception("ask failed"); bot.reply_to(m, f"error: {e}")


@bot.message_handler(commands=["council", "company"])
def council(m):
    t = m.text.replace("/council", "").replace("/company", "").strip() or "a faceless YouTube channel"
    bot.send_message(m.chat.id, f"🏛️ Agents discussing: {t}\n(~30-60s)...")
    try:
        out = agent_core.company_plan(t) if "/company" in m.text else "".join(
            f"\n🔹 [{r}] {a}\n" for r, a in agent_core.council(t, rounds=1))
        for c in _chunks(out):
            bot.send_message(m.chat.id, c)
    except Exception as e:
        log.exception("council failed"); bot.reply_to(m, f"error: {e}")


@bot.message_handler(commands=["video"])
def video(m):
    t = m.text.replace("/video", "").strip() or "Coffee"
    bot.send_message(m.chat.id, f"🎬 Generating video for: {t} (~40s)...")
    try:
        sys.path.insert(0, VIDEO_DIR)
        import pipeline
        mp4, _ = pipeline.run(t, "en")
        bot.send_message(m.chat.id, f"✅ Video ready:\n{mp4}")
    except Exception as e:
        log.exception("video failed")
        bot.send_message(m.chat.id, f"❌ Video error: {e}\n(Needs the local video toolkit.)")


@bot.message_handler(func=lambda m: True)
def echo(m):
    try:
        ans = agent_core.ask(m.text)
        for c in _chunks(ans):
            bot.send_message(m.chat.id, c)
    except Exception as e:
        log.exception("echo failed"); bot.reply_to(m, f"error: {e}")


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: set TELEGRAM_BOT_TOKEN first.")
        sys.exit(1)
    log.info("Bot started, polling...")
    print("Bot polling... open Telegram and message your bot.")
    # shorter long-poll + retry so it survives sandbox network drops
    bot.infinity_polling(timeout=15, long_polling_timeout=10,
                        retry_on_read_timeout=True, non_stop=True)
