import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token, session_factory: sessionmaker):
        self.token = token
        self.app = ApplicationBuilder().token(self.token).build()

        self.app.bot_data["session_factory"] = session_factory

        self.app.add_error_handler(self._error_handler)

    def add_command_handler(self, commands, handler):
        for command in commands:
            self.app.add_handler(
                CommandHandler(command, handler)
            )

    def run(self):
        self.app.run_polling()

    async def send_message(self, chat_id: int, message: str):
        try:
            await self.app.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Не удалось отправить сообщение ({message}) пользователю (Telegram ID: {chat_id}): {e}")

    async def _error_handler(self, update, context):
        logger.exception(
            "Exception while handling an update",
            exc_info=context.error
        )

        if update and update.effective_message:
            await update.effective_message.reply_text("Произошла внутренняя ошибка. Попробуйте позднее.")