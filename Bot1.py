from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Filters, CallbackQueryHandler
import requests
import time

# === CONFIGURATION ===
TOKEN = 'API'           # Replace with your Bot Token from BotFather
OWNER_ID = TELEGRAM ID                       # Replace with your Telegram user ID (get it from @userinfobot)
TOGETHER_API_KEY = 'API'  # Replace with your API key from Together.ai
GROQ_API_KEY = 'API'          # Replace with your Groq API key

# === AI Functions ===
def get_groq_reply(message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    return result['choices'][0]['message']['content'].strip()

def get_together_reply(message):
    url = "https://api.together.xyz/inference"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "prompt": f"<s>[INST] {message} [/INST]",
        "max_tokens": 256,
        "temperature": 0.7,
        "top_p": 0.9,
        "stop": ["</s>", "[/INST]"]
    }

    time.sleep(2)  # Optional delay to avoid rate limits
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    output = result.get("output") or result.get("choices", [{}])[0].get("text", "")
    return output.strip() if output else "AI: Empty response from Together."

def get_chatgpt_reply(message):
    try:
        return get_groq_reply(message)
    except Exception as e1:
        try:
            return get_together_reply(message)
        except Exception as e2:
            return f"AI Error (Groq: {e1}, Together: {e2})"

# === Logging ===
def log_chat(user, text, reply):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{user}: {text}\nBot: {reply}\n\n")

# === /start Command ===
def start(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("Access Denied.")
        return

    keyboard = [
        [InlineKeyboardButton("Ask AI", callback_data='ask')],
        [InlineKeyboardButton("Show Log", callback_data='log')],
        [InlineKeyboardButton("About", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

# === Button Handler ===
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.from_user.id != OWNER_ID:
        query.edit_message_text("Access Denied.")
        return

    if query.data == 'about':
        query.edit_message_text("I’m your personal AI assistant using Groq and Together.ai.")
    elif query.data == 'log':
        try:
            with open("chat_log.txt", "r", encoding="utf-8") as f:
                logs = f.read()[-4000:]
            query.edit_message_text(f"Recent Logs:\n{logs}")
        except FileNotFoundError:
            query.edit_message_text("No logs yet.")
    elif query.data == 'ask':
        query.edit_message_text("Send me a message and I'll reply using AI!")

# === Message Handler ===
def handle_message(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("Access Denied.")
        return

    user_message = update.message.text
    reply = get_chatgpt_reply(user_message)
    update.message.reply_text(reply)
    log_chat(update.effective_user.first_name, user_message, reply)

# === Main ===
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
