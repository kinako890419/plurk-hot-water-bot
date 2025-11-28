import random

from src.api.plurk_api import PlurkUtils


def random_like_post(plurk: PlurkUtils, msgs):
    l = []

    for msg in msgs:
        if (msg.get('type') == 'new_plurk') and (msg.get('plurk_type') == 0):
            pid = msg.get('plurk_id')
            owner_id = msg.get('owner_id')
            if not plurk.is_friend(owner_id):
                return
            random_num = random.randint(1, 100)
            if random_num <= 30:
                l.append(pid)
        else:
            continue

    plurk.like_plurk(l)
