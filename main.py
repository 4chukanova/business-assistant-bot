
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Команда /add_knowledge
async def add_knowledge(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Знание успешно добавлено!')

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет, я твой ассистент!")

def main():
    """Запуск бота"""
    token = "YOUR_TELEGRAM_TOKEN"  # Замените на ваш токен

    # Создаём экземпляр Application
    application = Application.builder().token(token).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_knowledge", add_knowledge))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
