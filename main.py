import logging
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, ContextTypes
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
TARIFF_COST = int(os.getenv("TARIFF_COST"))

openai.api_key = OPENAI_API_KEY
subscribers = set()
knowledge_base = []

SYSTEM_PROMPT = """
Ты — бизнес-ассистент пользователя. Ты анализируешь идеи только на основе предоставленных пользователем материалов и фактов. Не фантазируешь, не додумываешь. Помогаешь увидеть слабые места и точки роста. Стиль — прямой, структурный, провокационный.
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in subscribers:
        await update.message.reply_text(f"Привет! Чтобы пользоваться ботом, оформи подписку: {TARIFF_COST}₽/мес.")
    else:
        await update.message.reply_text("Ты можешь отправить мне бизнес-идею на разбор.")

async def add_knowledge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return await update.message.reply_text("Эта команда доступна только администратору.")
    if not context.args:
        return await update.message.reply_text("Пришли текст знания после команды.")
    knowledge = " ".join(context.args)
    knowledge_base.append(knowledge)
    await update.message.reply_text("Материал добавлен в базу знаний.")

async def show_knowledge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return await update.message.reply_text("Эта команда доступна только администратору.")
    if not knowledge_base:
        return await update.message.reply_text("База знаний пока пуста.")
    kb = "\n---\n".join(knowledge_base)
    await update.message.reply_text(f"База знаний:\n{kb}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in subscribers:
        return await update.message.reply_text("Оформи подписку, чтобы пользоваться ботом.")
    user_message = update.message.text
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + "\nБаза знаний:\n" + "\n".join(knowledge_base)},
            {"role": "user", "content": user_message}
        ]
    )
    reply = response["choices"][0]["message"]["content"]
    await update.message.reply_text(reply)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscribers.add(user_id)
    await update.message.reply_text("Подписка активирована. Теперь ты можешь отправлять бизнес-идеи.")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscribers.discard(user_id)
    await update.message.reply_text("Подписка отключена.")

def main():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("добавить_знание", add_knowledge))
    app.add_handler(CommandHandler("посмотреть_базу", show_knowledge))
    app.add_handler(CommandHandler("subscribe", subscribe))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бизнес-ассистент запущен 🚀")
    app.run_polling()

if __name__ == "__main__":
    main()
