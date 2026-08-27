from typing import Optional

from sqlalchemy import ForeignKey, Integer, Text, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone

from notifications.notification_states import NotificationStates

class Base(DeclarativeBase):
    pass


class SubscriptionTypes(Base):
    __tablename__ = 'SubscriptionTypes'

    Type: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)
    Name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    DurationInHours: Mapped[int] = mapped_column(Integer, nullable=False)

    Subscriptions: Mapped[list['Subscriptions']] = relationship('Subscriptions', back_populates='SubscriptionTypes_')


class Users(Base):
    __tablename__ = 'Users'

    MinecraftName: Mapped[str] = mapped_column(Text, primary_key=True, unique=True)
    TgID: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    Subscriptions: Mapped[list['Subscriptions']] = relationship('Subscriptions', back_populates='Users_')


class Subscriptions(Base):
    __tablename__ = 'Subscriptions'

    SubscriptionID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    BornDate: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ExpireDate: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    Type: Mapped[int] = mapped_column(ForeignKey('SubscriptionTypes.Type'), nullable=False)
    MinecraftName: Mapped[Optional[str]] = mapped_column(ForeignKey('Users.MinecraftName'))

    Users_: Mapped[Optional['Users']] = relationship('Users', back_populates='Subscriptions')
    SubscriptionTypes_: Mapped['SubscriptionTypes'] = relationship('SubscriptionTypes', back_populates='Subscriptions')

class Admins(Base):
    __tablename__ = 'Admins'

    TgID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    EmployDate: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    EmployedBy: Mapped[Optional[int]] = mapped_column(ForeignKey('Admins.TgID'), nullable=False)

class Notifications(Base):
    __tablename__ = 'Notifications'

    NotificationID: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    State: Mapped['NotificationStates'] = mapped_column(Enum(NotificationStates), nullable=False, default=NotificationStates.NORMAL.value)
    SubscriptionID: Mapped[int] = mapped_column(ForeignKey('Subscriptions.SubscriptionID'), nullable=False)