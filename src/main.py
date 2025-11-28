import logging
import os
import time
import pytz

from multiprocessing import Process
from apscheduler.schedulers.blocking import BlockingScheduler
from plurk_oauth import PlurkAPI

from src.service.post.bot_actions import random_like_post
from src.service.post.scheduled import post_daily_message
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
                respond_post(plurk=plurk, msgs=msgs)
        except Exception as e:
            logger.error(e)

def sub():
    setup_logging()
    logger = logging.getLogger(__name__)

    while True:
        try:
            plurk.add_all_as_friends()
            msgs = plurk.get_new_message()
            if msgs:
                random_like_post(plurk=plurk, msgs=msgs)
            time.sleep(1)
        except Exception as e:
            logger.error(e)

def daily_post():
    setup_logging()

    scheduler = BlockingScheduler(timezone=pytz.timezone('Asia/Taipei'))

    scheduler.add_job(post_daily_message, 'cron', hour=18, minute=00, args=[plurk])
    scheduler.start()


if __name__ == "__main__":

    sub_p = Process(target=sub, daemon=True)
    main = Process(target=run, daemon=True)
    daily = Process(target=daily_post, daemon=True)

    sub_p.start()
    main.start()
    daily.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
