from enum import StrEnum

class Help(StrEnum):
    
    USER = (
'''Команды:
> /subscriptions - получить свои подписки'''
    )

    CABAN = (
'''Доступные команды для кабанов:
<code>/add_user &lt;minecraft_name&gt; &lt;telegram_id&gt;</code> - добавить пользователя
<code>/add_caban &lt;telegram_id&gt;</code> - добавить кабана
<code>/user_subscriptions &lt;minecraft_name&gt;</code> - получить подписки пользователя
<code>/create_subscription &lt;name&gt; &lt;duration_in_hours&gt;</code> - создать вид подписки
/list_subscriptions - получить список всех видов подписок
<code>/attach_subscription &lt;minecraft_name&gt; &lt;subscription_type_id или subscription_name&gt;</code> - привязать подписку пользователю
/subscriptions - получить свои подписки
<code>/announcement &lt;text&gt;</code> - отправить объявление всем пользователям'''
    )