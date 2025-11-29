import sys
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
import os
import time
import threading

from plurk_oauth import PlurkAPI

from src.service.post.scheduled import BotScheduledTasks
from src.utils.logging_config import setup_logging
from src.api.plurk_api import PlurkUtils
from src.service.respond_plurk import respond_post


setup_logging()
logger = logging.getLogger(__name__)

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


if __name__ == "__main__":

    bot_thread = threading.Thread(target=run, daemon=True)
    bot_thread.start()

    scheduler = BackgroundScheduler()
    bot_tasks = BotScheduledTasks(plurk)
    bot_tasks.schedule_jobs(scheduler)
    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Received exit signal, shutting down...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully.")
