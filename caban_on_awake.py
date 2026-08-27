import logging
import logger as log

from datetime import datetime
from db_interactions import DBInteractions
from sqlalchemy.orm import sessionmaker

logger = log.get_logger(__name__)

def add_cabans_from_file(session_factory: sessionmaker, path: str):
    try:
        with session_factory() as session:
                db = DBInteractions(session)
                with open(path, "r") as file:
                    for line in file:
                        tg_id = int(line)
                        if db.is_caban(tg_id):
                            logger.info(f"Кабан {tg_id} уже существует")
                            continue
                        db.add_caban(tg_id, datetime.now(), 0)
                        logger.info(f"Добавлен кабан со старта: {tg_id}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении Кабана {e}")