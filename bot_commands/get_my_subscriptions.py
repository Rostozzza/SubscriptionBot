import logging
import logger as log

from telegram import Update
from datetime import datetime
from telegram.ext import ContextTypes
from sqlalchemy.orm import sessionmaker
from db_interactions import DBInteractions

logger = log.get_logger(__name__)

async def get_my_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.log_command_exec(logger)
    telegram_id = update.effective_user.id

    session_factory: sessionmaker = context.bot_data["session_factory"]
    with session_factory() as session:
        db = DBInteractions(session)

        user = db.get_user_by_telegram_id(telegram_id)
        if not user:
            await update.message.reply_text("Вы не зарегистрированы в системе.")
            return

        subscriptions = db.get_user_subscriptions(user.MinecraftName)
        subscriptions = [sub for sub in subscriptions if sub.ExpireDate > datetime.now()]
        if len(subscriptions) == 0:
            await update.message.reply_text("У Вас нет активных подписок.")
            return

        subscription_info = "\n".join([f"> {db.get_subscription_name(sub.Type)}\nДата окончания: {sub.ExpireDate.replace(microsecond=0)}\nОсталось: {(sub.ExpireDate.replace(microsecond=0) - datetime.now().replace(microsecond=0))}" for sub in subscriptions])
        await update.message.reply_text(f"Ваши подписки:\n\n{subscription_info}")
        log.log_successful_command_exec(logger, update.effective_user.id)