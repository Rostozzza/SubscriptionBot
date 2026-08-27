import logging
import logger as log

from telegram import Update
from default_messages import Help
from telegram.ext import ContextTypes
from sqlalchemy.orm import sessionmaker
from db_interactions import DBInteractions

logger = log.get_logger(__name__)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.log_command_exec(logger)
    session_factory: sessionmaker = context.bot_data["session_factory"]
    with session_factory() as session:
        db = DBInteractions(session)

        if db.is_caban(update.effective_user.id):
            await update.message.reply_text(Help.CABAN, parse_mode="HTML")   
        else:
            await update.message.reply_text(Help.USER, parse_mode="Markdown")
        log.log_successful_command_exec(logger, update.effective_user.id)