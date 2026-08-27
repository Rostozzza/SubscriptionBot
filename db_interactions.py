from datetime import datetime
import warnings

import models

from sqlalchemy.orm import Session

import notifications

class DBInteractions:
    def __init__(self, session: Session):
        self.session: Session = session

    def create_user(self, minecraft_name: str, telegram_id: int):
        user = models.Users(
            MinecraftName=minecraft_name,
            TgID=telegram_id,
        )

        try:
            self.session.add(user)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def create_subscription(self, name: str, duration_in_hours: int):
        subscription_type = models.SubscriptionTypes(
            Name=name,
            DurationInHours=duration_in_hours,
        )

        try:
            self.session.add(subscription_type)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def attach_subscription_to_user(self, minecraft_name: str, type_id: int, born_date: datetime, expire_date: datetime):
        subscription = models.Subscriptions(
            MinecraftName=minecraft_name,
            Type=type_id,
            BornDate=born_date,
            ExpireDate=expire_date,
        )

        try:
            self.session.add(subscription)
            self.session.commit()
            self.create_notification(subscription.SubscriptionID)
        except Exception:
            self.session.rollback()
            raise

    def get_user_subscriptions(self, minecraft_name: str):
        subscriptions = self.session.query(models.Subscriptions).filter_by(MinecraftName=minecraft_name).all()
        return subscriptions

    def add_caban(self, telegram_id: int, employ_date: datetime, employed_by: int):
        caban = models.Admins(
            TgID=telegram_id,
            EmployDate=employ_date,
            EmployedBy=employed_by,
        )

        try:
            self.session.add(caban)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def is_caban(self, telegram_id: int) -> bool:
        caban = self.session.query(models.Admins).filter_by(TgID=telegram_id).one_or_none()
        return caban is not None

    def get_subscription_info(self, type_id: int):
        subscription_type = self.session.query(models.SubscriptionTypes).filter_by(Type=type_id).one_or_none()
        return subscription_type

    def get_subscription_type_id(self, name: str):
        subscription_type = self.session.query(models.SubscriptionTypes).filter_by(Name=name).one_or_none()
        if subscription_type:
            return subscription_type.Type
        return None

    def get_subscription_name(self, type_id: int):
        subscription_type = self.session.query(models.SubscriptionTypes).filter_by(Type=type_id).one_or_none()
        if subscription_type:
            return subscription_type.Name
        return None

    def is_user_exists(self, minecraft_name: str) -> bool:
        user = self.session.query(models.Users).filter_by(MinecraftName=minecraft_name).one_or_none()
        return user is not None

    def is_user_exists_by_telegram_id(self, telegram_id: int) -> bool:
        user = self.session.query(models.Users).filter_by(TgID=telegram_id).one_or_none()

        return user is not None

    def is_subscription_name_exist(self, name: str):
        sub = self.session.query(models.SubscriptionTypes).filter_by(Name=name).one_or_none()
        return sub is not None

    def subscription_freshest(self, subscription: models.Subscriptions, at_moment: datetime):
        """1.0 is freshest, 0.0 is expired"""
        if subscription.ExpireDate <= at_moment:
            return 0.0
        
        duration_in_hours = self.get_subscription_info(subscription.Type).DurationInHours
        time_left = (subscription.ExpireDate - at_moment).total_seconds() / 3600.0
        return time_left / duration_in_hours

    def get_user_by_minecraft_name(self, minecraft_name: str):
        user = self.session.query(models.Users).filter_by(MinecraftName=minecraft_name).one_or_none()
        return user

    def get_user_by_telegram_id(self, telegram_id: int):
        user = self.session.query(models.Users).filter_by(TgID=telegram_id).one_or_none()
        return user

    def get_all_cabans(self):
        cabans = self.session.query(models.Admins).all()
        return cabans

    def get_all_users(self):
        users = self.session.query(models.Users).all()
        return users

    def get_all_subscription_types(self):
        subscription_types = self.session.query(models.SubscriptionTypes).all()
        return subscription_types

    def get_all_subscriptions(self):
        subscriptions = self.session.query(models.Subscriptions).all()
        return subscriptions

    def get_subscription_notification_state(self, subscription_id) -> notifications.NotificationStates:
        notification_obj = self.session.query(models.Notifications).filter_by(SubscriptionID=subscription_id).one_or_none()
        if notification_obj is None: 
            return notifications.NotificationStates.NORMAL
        return notification_obj.State

    def set_subscription_notification_state(self, subscription_id, state: notifications.NotificationStates):
        notification_obj = self.session.query(models.Notifications).filter_by(SubscriptionID=subscription_id).one_or_none()

        if notification_obj is None:
            notification_obj = models.Notifications(
                SubscriptionID=subscription_id,
                State=state,
            )
            self.session.add(notification_obj)
        else:
            notification_obj.State = state

        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

    def create_notification(self, subscription_id):
        notification = models.Notifications(
            SubscriptionID=subscription_id
        )

        try:
            self.session.add(notification)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise