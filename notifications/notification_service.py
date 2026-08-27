import models
import logging
import asyncio
import datetime
import logger as log
import db_interactions

from typing import List
from notifications import NotificationStates
from telegram_bot import TelegramBot
from sqlalchemy.orm import sessionmaker

logger = log.get_logger(__name__)

class NotificationService:
    def __init__(self, bot, session_factory):
        self.bot: TelegramBot = bot
        self.session_factory: sessionmaker = session_factory
        logger.info("Сервис уведомлений запущен")

    async def watch_subscriptions(self):
        while True:
            logger.info("Запущена проверка актуальности подписок")
            await self.warn_expiring_subscriptions(await self.update_subscription_status_and_return_updated(NotificationStates.ABOUT_TO_EXPIRE, await self.get_expired_subscriptions(0.1)))
            await self.warn_expired_subscriptions(await self.update_subscription_status_and_return_updated(NotificationStates.EXPIRED, await self.get_expired_subscriptions()))
            await asyncio.sleep(60)  # Check every minute

    async def warn_expiring_subscriptions(self, expired_subscriptions: List[models.Subscriptions]):
        with self.session_factory() as session:
            db = db_interactions.DBInteractions(session)
            for sub in expired_subscriptions:
                user = db.get_user_by_minecraft_name(sub.MinecraftName)
                if user:
                    sub_name = db.get_subscription_info(sub.Type).Name
                    message = f"Ваша подписка '{sub_name}' скоро истекает."
                    await self.bot.send_message(chat_id=user.TgID, message=message)

    async def warn_expired_subscriptions(self, expired_subscriptions: List[models.Subscriptions]):
        with self.session_factory() as session:
            db = db_interactions.DBInteractions(session)
            for sub in expired_subscriptions:
                user = db.get_user_by_minecraft_name(sub.MinecraftName)
                logger.info(f"Истекла подписка {sub.SubscriptionID} пользователя {sub.MinecraftName}")
                if user:
                    message = f"Ваша подписка '{db.get_subscription_name(sub.Type)}' истекла."
                    await self.bot.send_message(chat_id=user.TgID, message=message)
                    cabans = db.get_all_cabans()
                    for caban in cabans:
                        await self.bot.send_message(chat_id=caban.TgID, message=f"У пользователя {user.MinecraftName} истекла подписка '{db.get_subscription_name(sub.Type)}'.")

    async def update_subscription_status_and_return_updated(self, state_to_set: NotificationStates, expired_subscriptions: List[models.Subscriptions]) -> List[models.Subscriptions]:
        with self.session_factory() as session:
            db = db_interactions.DBInteractions(session)
            
            updated_subscriptions: List[models.Subscriptions] = []
            
            for sub in expired_subscriptions:
                state = db.get_subscription_notification_state(sub.SubscriptionID)
                if state_to_set == NotificationStates.NORMAL:
                    continue
                elif state_to_set == NotificationStates.ABOUT_TO_EXPIRE:
                    if state == NotificationStates.NORMAL:
                        db.set_subscription_notification_state(sub.SubscriptionID, state_to_set)
                        updated_subscriptions.append(sub)
                    else:
                        continue
                elif state_to_set == NotificationStates.EXPIRED:
                    if state in (
                        NotificationStates.NORMAL,
                        NotificationStates.ABOUT_TO_EXPIRE,
                    ):
                        db.set_subscription_notification_state(sub.SubscriptionID, state_to_set)
                        updated_subscriptions.append(sub)
                    else:
                        continue
                else:
                    continue

        return updated_subscriptions

    async def get_expired_subscriptions(self, fresh_threshold=0.0) -> List[models.Subscriptions]:
        with self.session_factory() as session:
            db = db_interactions.DBInteractions(session)

            subscriptions = db.get_all_subscriptions()
            expired_subscriptions = [sub for sub in subscriptions if db.subscription_freshest(sub, datetime.datetime.now()) <= fresh_threshold]
            return expired_subscriptions