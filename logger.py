import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    file_handler = TimedRotatingFileHandler(
        log_dir / "bot.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )

    console_handler = logging.StreamHandler()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            console_handler,
            file_handler,
        ],
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_command_exec(logger: logging.Logger):
    logger.info("Вызвана команда")


def log_successful_command_exec(
    logger: logging.Logger,
    activator: int,
    result_name: str | None = None
):
    if result_name:
        logger.info(
            "Команда была успешно выполнена пользователем %s с результатом %s",
            activator,
            result_name
        )
    else:
        logger.info(
            "Команда была успешно выполнена пользователем %s",
            activator
        )