import logging
import logger as log

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import sessionmaker
from db_interactions import DBInteractions

logger = log.get_logger(__name__)

async def create_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.log_command_exec(logger)
    session_factory: sessionmaker = context.bot_data["session_factory"]
    with session_factory() as session:
            db = DBInteractions(session)
    
            if not db.is_caban(update.effective_user.id):
                await update.message.reply_text("У Вас нет прав для создания подписок.")
                return

    if not (context.args and len(context.args) == 2):
        await update.message.reply_text("Пожалуйста, предоставьте имя и продолжительность подписки в формате: /create_subscription <name> <duration_in_hours>")
        return
    
    Name = context.args[0]
    DurationInHours = context.args[1]

    if DurationInHours.isnumeric():
        DurationInHours = int(DurationInHours)
    else:
        await update.message.reply_text("Длительность подписки в часах должна быть целочисленна.")
        return

    if Name.isnumeric():
        await update.message.reply_text("Имя подписки не может быть числом.")
        return

    if DurationInHours <= 0:
        await update.message.reply_text("Продолжительность подписки должна быть положительным числом.")
        return

    with session_factory() as session:
        if db.is_subscription_name_exist(Name):
            await update.message.reply_text("Название подписки должно быть уникально.")
            return

        db.create_subscription(Name, DurationInHours)

        subscription_type_id = db.get_subscription_type_id(Name)

    await update.message.reply_text(f"Подписка {Name}({subscription_type_id}) с продолжительностью {DurationInHours} часов успешно добавлена.")    
    log.log_successful_command_exec(logger, update.effective_user.id, Name)