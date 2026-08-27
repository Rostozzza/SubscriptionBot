import datetime
import logger as log

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import sessionmaker
from db_interactions import DBInteractions

logger = log.get_logger(__name__)

async def attach_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.log_command_exec(logger)
    if not (context.args and len(context.args) == 2):
        await update.message.reply_text("Пожалуйста, предоставьте необходимые параметры в формате: /attach_subscription <minecraft_name> <subscription_type>")
        return
    
    minecraft_name = context.args[0]
    subscription_type_or_name = context.args[1]

    session_factory: sessionmaker = context.bot_data["session_factory"]
    with session_factory() as session:
        db = DBInteractions(session)

        if not db.is_caban(update.effective_user.id):
            await update.message.reply_text("У вас нет прав для привязки подписок.")
            return

        if not db.is_user_exists(minecraft_name):
            await update.message.reply_text(f"Пользователь с именем Minecraft '{minecraft_name}' не найден.")
            return

        subscription_type = int(subscription_type_or_name) if subscription_type_or_name.isdigit() else db.get_subscription_type_id(subscription_type_or_name)

        subscription_info = db.get_subscription_info(subscription_type)
        if not subscription_info:
            await update.message.reply_text("Указанный тип подписки не существует.")
            return
        subscription_name = subscription_info.Name
        subscription_duration = subscription_info.DurationInHours

        attach_date: datetime = datetime.datetime.now()
        expire_date: datetime = attach_date + datetime.timedelta(hours=subscription_duration)

        db.attach_subscription_to_user(minecraft_name, subscription_type, attach_date, expire_date)

    await update.message.reply_text(f"Подписка {subscription_name}({subscription_type}) успешно привязана к пользователю {minecraft_name}.\nДата окончания подписки: {expire_date.strftime('%Y-%m-%d %H:%M:%S')}.")
    log.log_successful_command_exec(logger, update.effective_user.id, f"{minecraft_name} <---> {subscription_name}")