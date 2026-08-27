import logging
import logger as log

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import sessionmaker
from db_interactions import DBInteractions

logger = log.get_logger(__name__)

async def announcement(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.log_command_exec(logger)
    if not (context.args and len(context.args) == 1):
        await update.message.reply_text("Пожалуйста, предоставьте текст объявления в формате: /announcement <text>")
        return
    
    text = context.args[0]

    session_factory: sessionmaker = context.bot_data["session_factory"]
    with session_factory() as session:
        db = DBInteractions(session)

        if not db.is_caban(update.effective_user.id):
            await update.message.reply_text("У вас нет прав для отправки объявлений.")
            return

        for user in db.get_all_users():
            try:
                await context.bot.send_message(chat_id=user.TgID, text=text)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {user.MinecraftName} (Telegram ID: {user.TgID}): {e}")

    await update.message.reply_text(f"Объявление отправлено:\n{text}")
    log.log_successful_command_exec(logger, update.effective_user.id, text)