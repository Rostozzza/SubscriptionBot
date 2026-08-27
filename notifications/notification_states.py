from enum import StrEnum

class NotificationStates(StrEnum):
    NORMAL = "NORMAL"
    ABOUT_TO_EXPIRE = "ABOUT_TO_EXPIRE"
    EXPIRED = "EXPIRED"