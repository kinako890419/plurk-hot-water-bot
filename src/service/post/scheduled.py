import logging
import pytz

from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from src.api.plurk_api import PlurkUtils
from src.service.post.bot_actions import random_like_post


logger = logging.getLogger(__name__)


class BotScheduledTasks:

    def __init__(self, plurk: PlurkUtils):
        self.plurk = plurk

    def schedule_jobs(self, scheduler: BackgroundScheduler):
        @scheduler.scheduled_job('cron', hour=18, minute=0, id='daily_post')
        def post_daily_message():
            try:
                t = pytz.timezone('Asia/Taipei')
                current_date = datetime.now(t).strftime("%Y/%m/%d")
                self.plurk.post_new_plurk(content=f"{current_date} 機器人生存確認，多喝熱水 (draw)")
                logger.info(f"Daily post completed at {datetime.now(t).strftime('%Y/%m/%d %H:%M:%S')}")
            except Exception as e:
                logger.error(f"Error posting daily message: {e}")

        @scheduler.scheduled_job('interval', minutes=1, id='add_friends')
        def add_friends():
            try:
                self.plurk.add_all_as_friends()
            except Exception as e:
                logger.error(f"Error while adding friends: {e}")

        @scheduler.scheduled_job('interval', minutes=2, id='like_random_posts')
        def like_random_posts():
            try:
                msgs = self.plurk.get_new_message()
                if msgs:
                    random_like_post(plurk=self.plurk, msgs=msgs)
            except Exception as e:
                logger.error(f"Error while liking posts: {e}")
