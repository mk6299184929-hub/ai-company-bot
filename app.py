"""
Hugging Face Spaces entry point.
Launches the Telegram bot in a background thread and serves a tiny Gradio
page (HF requires a web server to keep the Space alive). Result: your
5-agent AI company runs 24x7 on FREE Hugging Face hosting.

Set Space Secrets:  TELEGRAM_BOT_TOKEN  and  GEMINI_API_KEY  (or GROQ_KEY)
"""
import os
import threading
import gradio as gr
import telegram_bot


def status():
    return ("🤖 AI Company Bot is running 24/7 on this Space.\n"
            "Open your Telegram bot and send a message — the 5-agent team will reply.\n"
            "Commands: /ask /council /company /agents /ping")


# Start the Telegram bot polling in the background (stays alive on the Space)
threading.Thread(target=telegram_bot.bot.infinity_polling, daemon=True).start()

demo = gr.Interface(
    fn=status, inputs=None, outputs="text",
    title="AI Company Bot", description="Your 24/7 phone-controlled AI company",
)
port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)
