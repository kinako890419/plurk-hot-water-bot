import logging
import os
import time
from multiprocessing import Process

from plurk_oauth import PlurkAPI

from src.utils.logging_config import setup_logging
from src.api.plurk_api import PlurkUtils
from src.service.respond_plurk import respond_post


PLURK_CONSUMER_KEY=os.getenv('PLURK_CONSUMER_KEY')
PLURK_CONSUMER_SECRET=os.getenv('PLURK_CONSUMER_SECRET')
PLURK_ACCESS_TOKEN=os.getenv('PLURK_ACCESS_TOKEN')
PLURK_ACCESS_TOKEN_SECRET=os.getenv('PLURK_ACCESS_TOKEN_SECRET')


plurk_api = PlurkAPI(
    PLURK_CONSUMER_KEY,
    PLURK_CONSUMER_SECRET
)
plurk_api.authorize(
    PLURK_ACCESS_TOKEN,
    PLURK_ACCESS_TOKEN_SECRET
)

plurk = PlurkUtils(plurk_api=plurk_api)


def run():
    setup_logging()
    logger = logging.getLogger(__name__)

    while True:
        try:
            msgs = plurk.get_new_message()
            if msgs:
                logger.info(f"Got new message", extra={'plurk_messages': msgs})
                respond_post(plurk=plurk, msgs=msgs)
        except Exception as e:
            logger.error(e)

def add_friends():
    setup_logging()
    logger = logging.getLogger(__name__)

    while True:
        try:
            plurk.add_all_as_friends()
            time.sleep(1)
        except Exception as e:
            logger.error(e)


if __name__ == "__main__":

    f = Process(target=add_friends)
    main = Process(target=run)
    f.start()
    main.start()
    f.join()
    main.join()
