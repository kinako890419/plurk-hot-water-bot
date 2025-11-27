import json
import logging
import re
import urllib.request


_time_out = 80
_jsonp_re = re.compile(r'CometChannel\.scriptCallback\((.+)\);\s*')

logger = logging.getLogger(__name__)

class PlurkUtils:
    def __init__(self, plurk_api):
        self.plurk = plurk_api
        self.new_offset = -1

    def add_all_as_friends(self):
        try:
            self.plurk.callAPI('/APP/Alerts/addAllAsFriends')
        except Exception as e:
            logger.error(f"Cannot add all as friends: {e}")

    def get_new_message(self):
        try:
            comet_channel = self._get_comet_channel()
            req = urllib.request.urlopen(comet_channel % self.new_offset, timeout=_time_out)
            rawdata = req.read().decode('utf-8')
            match = _jsonp_re.match(rawdata)
            if match:
                rawdata = match.group(1)
            data = json.loads(rawdata)
            self.new_offset = data.get('new_offset', -1)

            return data.get('data')

        except Exception as e:
            logging.error(f"Cannot get new message: {e}")

    def get_current_user_id(self):
        try:
            user_info = self.plurk.callAPI('/APP/Users/me')
            return user_info.get('id')
        except Exception as e:
            logger.error(f"Cannot get current user ID: {e}")

    def is_friend(self, user_id):
        try:
            logger.info(f"Check if user '{user_id}' is in friend list...")

            current_user_id = self.get_current_user_id()
            if not current_user_id:
                return False

            friends_data = []
            offset = 0

            while True:
                batch = self.plurk.callAPI('/APP/FriendsFans/getFriendsByOffset', {
                    'user_id': current_user_id,
                    'offset': offset,
                    'limit': 100
                })

                if not batch or len(batch) == 0:
                    break

                friends_data.extend(batch)
                offset += 100

                if len(batch) < 100: # last page
                    break

            friend_ids = {friend['id'] for friend in friends_data}

            return user_id in friend_ids

        except Exception as e:
            logging.error(f"Error occurred while checking friend list: {e}")
            return False

    def respond_post(self, pid, content, qualifier):
        try:
            # # Check if the post owner is a friend
            # if not self.is_friend(owner_id):
            #     return

            self.plurk.callAPI('/APP/Responses/responseAdd', {
                'plurk_id': pid,
                'content': content,
                'qualifier': qualifier
            })

            # time.sleep(1)

        except Exception as e:
            logger.error(f"Error occurred while responding a post: {e}")

    def _get_comet_channel(self):
        logger.info("Get Plurk Comet Channel")
        comet = self.plurk.callAPI('/APP/Realtime/getUserChannel')
        comet_channel = comet.get('comet_server') + "&new_offset=%d"

        return comet_channel
