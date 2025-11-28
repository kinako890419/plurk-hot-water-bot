import logging
import pytz

from datetime import datetime

from src.api.plurk_api import PlurkUtils


def post_daily_message(plurk: PlurkUtils):
    """Function to post daily message at 18:00"""
    logger = logging.getLogger(__name__)
    try:
        t = pytz.timezone('Asia/Taipei')
        current_date = datetime.now(t).strftime("%Y/%m/%d")
        plurk.post_new_plurk(content=f"{current_date} 機器人生存確認，多喝熱水 (draw)")
        logger.info(f"Daily post completed at {datetime.now(t).strftime('%Y/%m/%d %H:%M:%S')}")
    except Exception as e:
        logger.error(f"Error posting daily message: {e}")
