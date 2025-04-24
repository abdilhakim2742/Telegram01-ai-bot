import logging
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os

TELEGRAM_TOKEN = os.getenv("7536364018:AAHHnyxEV3FCSJhEKKwsvI5YD7wBN9gO8SI")
OPENAI_API_KEY = os.getenv("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")  # Optional
GROQ_API_KEY = os.getenv("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")      # Optional
TOGETHER_API_KEY = os.getenv("51a694d27b2936da48061bb9764694fe65659719b9368b9dd57e20309cd3de99")  # Optional

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update, context):
    update.message.reply_text('Hello! I am your AI chatbot. Just type something!')

def ask_ai(text):
    if GROQ_API_KEY:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    elif TOGETHER_API_KEY:
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {"Authorization": f"Bearer {TOGETHER_API_KEY}"}
    elif OPENAI_API_KEY:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    else:
        return "AI service not configured."

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": text}],
        "temperature": 0.7
    }

    try:
        res = requests.post(url, json=data, headers=headers)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI Error: {str(e)}"

def handle_message(update, context):
    user_input = update.message.text
    update.message.reply_text("AI is thinking...")
    reply = ask_ai(user_input)
    update.message.reply_text(reply)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
