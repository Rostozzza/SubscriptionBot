import logging
import logger as log

from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import sessionmaker
from db_interactions import DBInteractions

logger = log.get_logger(__name__)

async def get_user_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.log_command_exec(logger)
    if not (context.args and len(context.args) == 1):
        await update.message.reply_text("Пожалуйста, предоставьте Minecraft имя в формате: /user_subscriptions <minecraft_name>")
        return
    
    minecraft_name = context.args[0]

    session_factory: sessionmaker = context.bot_data["session_factory"]
    with session_factory() as session:
        db = DBInteractions(session)

        if not db.is_caban(update.effective_user.id):
            await update.message.reply_text("У вас нет прав для получения информации о подписках пользователей.")
            return

        if not db.is_user_exists(minecraft_name):
            await update.message.reply_text(f"Пользователя {minecraft_name} не существует.")
            return

        subscriptions = db.get_user_subscriptions(minecraft_name)
        if not subscriptions:
            await update.message.reply_text("У пользователя нет активных подписок.")
            return

        subscription_info = "\n".join([f'''> Вид: {db.get_subscription_name(sub.Type)}({sub.Type}){" 💀" if sub.ExpireDate < datetime.now() else ""}\nДата начала: {sub.BornDate.replace(microsecond=0)}\nДата окончания: {sub.ExpireDate.replace(microsecond=0)}''' for sub in subscriptions])
        await update.message.reply_text(f"Подписки пользователя:\n\n{subscription_info}")
        log.log_successful_command_exec(logger, update.effective_user.id, f"запрошены подписки пользователя {minecraft_name}")