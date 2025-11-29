import logging
import random
import time

from src.api.plurk_api import PlurkUtils
from src.service.gen_content.llm_gen import gen_response


logger = logging.getLogger(__name__)
_msg_delay = 0.5

def respond_post(plurk, msgs):
    for msg in msgs:
        if (msg.get('type') == 'new_plurk') and (msg.get('plurk_type') == 0):
            pid = msg.get('plurk_id')
            user_id = msg.get('user_id')
            owner_id = msg.get('owner_id')
            content = msg.get('content_raw')
            qualifier = msg.get('qualifier')

            logger.info(f"Got new message, start processing.", extra={'plurk_messages': msgs})

            _process(plurk, pid, owner_id, content, qualifier)
        else:
            continue


def _process(plurk: PlurkUtils, pid, owner_id, content, qualifier):
    try:
        if not plurk.is_friend(owner_id):
            logger.info(f"Plurk {owner_id} is not friend", extra={'plurk_id': owner_id, 'plurk_msg': content})
            return

        if '！' in content:
            content = content.replace('！', '!')

        if (qualifier == 'hopes' or qualifier == 'wishes') and '!抽' in content:  # 希望
            c = content.replace(' ', '').replace('!抽', '')
            response = gen_response('tarot', c)
            p = _split_response(response)
            for part in p:
                plurk.respond_post(pid, part, 'thinks')
                time.sleep(_msg_delay)

        elif qualifier == 'wants' and '!抱怨' in content:  # 想要
            c = content.replace(' ', '').replace('!抱怨', '')
            response = gen_response('bad_answer', c)
            p = _split_response(response)
            for part in p:
                plurk.respond_post(pid, part, 'thinks')
                time.sleep(_msg_delay)

        elif qualifier == 'asks' and '!為什麼' in content:  # 問
            c = content.replace(' ', '').replace('!為什麼', '')
            response = gen_response('rap', c)
            p = _split_response(response)
            for part in p:
                plurk.respond_post(pid, part, 'feels')
                time.sleep(_msg_delay)

        elif qualifier == 'asks' and '!要不要' in content:
            c = content.replace(' ', '').replace('!要不要', '')
            response = gen_response('random_post', c)
            if response:
                plurk.respond_post(pid, response, 'feels')
                time.sleep(_msg_delay)
        else:
            random_num = random.randint(1, 100)

            if '機器人' in content:
                logger.info(f"Responding to '機器人' keyword", extra={'plurk_id': pid, 'plurk_msg': content, 'resptype': 'keyword'})
                plurk.respond_post(pid, "蛤", ':')
            elif '好不好' in content or '要不要' in content:
                logger.info(f"Responding to '好不好' or '要不要' keyword", extra={'plurk_id': pid, 'plurk_msg': content, 'resptype': 'keyword'})
                random_yn = random.choice(['好', '不要', '[emo3]', '[emo4]'])
                plurk.respond_post(pid, random_yn, 'feels')
            elif '熱水' in content:
                logger.info(f"Responding to '熱水' keyword", extra={'plurk_id': pid, 'plurk_msg': content, 'resptype': 'keyword'})
                plurk.respond_post(pid, '多喝熱水', 'says')
            else:
                if random_num >= 90:
                    random_water = random.choice(['多喝熱水', '多喝冷水', '多喝冷水[emo5]', '多喝熱水[emo5]'])
                    logger.info(f"Got random response", extra={'plurk_id': pid, 'plurk_msg': content, 'resptype': 'random', 'random_value': random_water})

                    plurk.respond_post(pid, random_water, 'says')

    except Exception as e:
        logger.error(f"Error processing plurk: {e}", exc_info=True)
        return


def _split_response(content):
    if not content:
        return []

    if '---' in content:
        p = [part.strip() for part in content.split('---') if part.strip()]
    else:
        p = [content]

    # Then split parts that are too long (>300 chars)
    res = []
    for part in p:
        if len(part) <= 300:
            res.append(part)
        else:
            for i in range(0, len(part), 300):
                res.append(part[i:i+300])

    return res
