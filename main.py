import models
import asyncio
import threading
import bot_commands
import environment_manager

from datetime import *
from logger import setup_logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram_bot import TelegramBot
from notifications.notification_service import NotificationService

DATABASE_URL = "sqlite:///database.db"

engine = create_engine(DATABASE_URL)


def main():
    setup_logging()

    

    models.Base.metadata.create_all(engine)

    SessionMaker = sessionmaker(bind=engine)

    env_manager = environment_manager.EnvironmentManager()

    telegram_bot = TelegramBot(token=env_manager.get_variable("TELEGRAM_BOT_API_KEY"), session_factory=SessionMaker)

    notification_service: NotificationService = NotificationService(telegram_bot, SessionMaker)
    def run_notification_service():
        asyncio.run(notification_service.watch_subscriptions())

    thread = threading.Thread(
        target=run_notification_service,
        daemon=True
    )
    thread.start()

    telegram_bot.add_command_handler(["add_user"], bot_commands.add_user)
    telegram_bot.add_command_handler(["add_caban"], bot_commands.add_caban)
    telegram_bot.add_command_handler(["user_subscriptions"], bot_commands.get_user_subscriptions)
    telegram_bot.add_command_handler(["subscriptions"], bot_commands.get_my_subscriptions)
    telegram_bot.add_command_handler(["list_subscriptions"], bot_commands.list_subscriptions)
    telegram_bot.add_command_handler(["create_subscription"], bot_commands.create_subscription)
    telegram_bot.add_command_handler(["attach_subscription"], bot_commands.attach_subscription)
    telegram_bot.add_command_handler(["announcement"], bot_commands.announcement)
    telegram_bot.add_command_handler(["help", "start"], bot_commands.help)
    
    telegram_bot.run()

if __name__ == "__main__":
    main()