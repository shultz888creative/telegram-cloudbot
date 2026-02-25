import os
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Конфиг из переменных окружения
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

user_contexts = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я Cloudbot — твой AI-ассистент.\n"
        "Отправь задачу текстом.\n"
        "/code — сгенерировать код\n"
        "/clear — очистить контекст"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    
    if user_id not in user_contexts:
        user_contexts[user_id] = []
    
    user_contexts[user_id].append(f"User: {message}")
    context_text = "\n".join(user_contexts[user_id][-10:])
    
    prompt = f"""Ты Cloudbot — личный тех-ассистент Александра (AI-креатор, автоматизатор, изучает Python и n8n).
    Помогай с кодом, автоматизацией, бизнес-логикой.
    Контекст: {context_text}
    Ответь кратко и по делу. Если код — с пояснениями."""
    
    response = model.generate_content(prompt)
    answer = response.text
    user_contexts[user_id].append(f"Assistant: {answer}")
    
    await update.message.reply_text(answer)

async def code_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Использование: /code напиши скрипт для парсинга JSON")
        return
    
    prompt = f"""Напиши Python-код для: {query}
    - Рабочий код с комментариями
    - Обработка ошибок
    - pip install если нужно
    - Объясни логику кратко"""
    
    response = model.generate_content(prompt)
    await update.message.reply_text(f"```python\n{response.text}\n```", parse_mode='Markdown')

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_contexts[user_id] = []
    await update.message.reply_text("Контекст очищен.")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("code", code_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()
