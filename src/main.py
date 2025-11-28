import logging
import os
import time
import pytz
import threading

from apscheduler.schedulers.background import BackgroundScheduler
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
    while True:
        try:
            msgs = plurk.get_new_message()
            if msgs:
                respond_post(plurk=plurk, msgs=msgs)
        except Exception as e:
            logger.error(f"Error while bot run: {e}")


def add_friends():
    try:
        plurk.add_all_as_friends()
    except Exception as e:
        logger.error(f"Error while adding friends: {e}")


def like_random_posts():
    try:
        msgs = plurk.get_new_message()
        if msgs:
            random_like_post(plurk=plurk, msgs=msgs)
    except Exception as e:
        logger.error(f"Error while liking posts: {e}")


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    bot = threading.Thread(target=run, daemon=True)
    bot.start()

    scheduler = BackgroundScheduler(timezone=pytz.timezone('Asia/Taipei'))

    scheduler.add_job(add_friends, 'interval', seconds=30, id='add_friends')
    scheduler.add_job(like_random_posts, 'interval', minutes=5, id='like_random_posts')
    scheduler.add_job(post_daily_message, 'cron', hour=18, minute=0, args=[plurk], id='daily_post')

    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Received exit signal, shutting down...")
        scheduler.shutdown()
