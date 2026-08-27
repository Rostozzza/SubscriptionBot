import logging
import logger as log

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import sessionmaker

from db_interactions import DBInteractions

logger = log.get_logger(__name__)

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.log_command_exec(logger)
    if not (context.args and len(context.args) == 2):
        await update.message.reply_text("Пожалуйста, предоставьте имя Minecraft и Telegram ID в формате: /add_user <minecraft_name> <telegram_id>")
        return

    minecraft_name = context.args[0]
    telegram_id = context.args[1]

    if telegram_id.isnumeric():
        telegram_id = int(telegram_id)
    else:
        await update.message.reply_text("Аргумент <telegram_id> должен быть представлен целым числом.")
        return

    session_factory: sessionmaker = context.bot_data["session_factory"]
    with session_factory() as session:
        db = DBInteractions(session)

        if not db.is_caban(update.effective_user.id):
            await update.message.reply_text("У вас нет прав для добавления пользователей.")
            return

        if db.is_user_exists(minecraft_name):
            await update.message.reply_text(f"Пользователь с именем Minecraft '{minecraft_name}' уже существует.")
            return

        if db.is_user_exists_by_telegram_id(telegram_id):
            await update.message.reply_text(f"Пользователь с Telegram ID '{telegram_id}' уже существует.")
            return

        db.create_user(minecraft_name, telegram_id)

    await update.message.reply_text(f"Пользователь {minecraft_name} с Telegram ID {telegram_id} успешно добавлен.")
    log.log_successful_command_exec(logger, update.effective_user.id, minecraft_name)
    try:
        await context.bot.send_message(chat_id=telegram_id, text=f"Вы были добавлены в систему подписок с Minecraft именем: {minecraft_name}.")
    except Exception as e:
        print(f"Не удалось отправить сообщение пользователю {minecraft_name} (Telegram ID: {telegram_id}): {e}")