import logging
import logger as log

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import sessionmaker
from db_interactions import DBInteractions

logger = log.get_logger(__name__)

async def list_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.log_command_exec(logger)
    session_factory: sessionmaker = context.bot_data["session_factory"]
    with session_factory() as session:
        db = DBInteractions(session)

        if not db.is_caban(update.effective_user.id):
            await update.message.reply_text("У вас нет прав для использования этой команды.")
            return

        subscriptions = db.get_all_subscription_types()
        if not subscriptions:
            await update.message.reply_text("Нет существующих подписок.")
            return

        subscription_info_text = "\n".join([f'''{sub.Type}|{sub.Name}|{sub.DurationInHours}''' for sub in subscriptions])
        await update.message.reply_text(f"Типы подписок:\n\nТип(ID)|Название|Продолжительность (часы)\n{subscription_info_text}")
        log.log_successful_command_exec(logger, update.effective_user.id)