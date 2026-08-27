import datetime
import logger as log

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy.orm import sessionmaker
from db_interactions import DBInteractions

logger = log.get_logger(__name__)

async def add_caban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.log_command_exec(logger)
    if not (context.args and len(context.args) == 1):
        await update.message.reply_text("Пожалуйста, предоставьте Telegram ID в формате: /add_caban <telegram_id>")
        return
    
    telegram_id = context.args[0]

    if telegram_id.isnumeric():
        telegram_id = int(telegram_id)
    else:
        await update.message.reply_text("Аргумент <telegram_id> должен быть представлен целым числом.")
        return

    session_factory: sessionmaker = context.bot_data["session_factory"]
    with session_factory() as session:
        db = DBInteractions(session)

        if not db.is_caban(update.effective_user.id):
            await update.message.reply_text("У вас нет прав для добавления кабанов.")
            return

        if db.is_caban(telegram_id):
            await update.message.reply_text(f"Пользователь с Telegram ID {telegram_id} уже является кабаном.")
            return
        
        db.add_caban(
            telegram_id, 
            datetime.datetime.now(), 
            update.effective_user.id
        )

    await update.message.reply_text(f"Кабан {telegram_id} успешно добавлен.")
    log.log_successful_command_exec(logger, update.effective_user.id, telegram_id)
    try:
        await context.bot.send_message(chat_id=telegram_id, text=f"Вы были добавлены в систему подписок как Кабан.")
    except Exception as e:
        print(f"Не удалось отправить сообщение пользователю (Telegram ID: {telegram_id}): {e}")