async def error_handler(update, context):
    print(f"Ошибка: {context.error}")

    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Произошла ошибка при выполнении команды."
        )