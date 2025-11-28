import json
import logging
import random
from pathlib import Path

from src.api.gemini_api import GeminiApi
from src.service.gen_content.get_random_tarot_info import get_random_tarot_info


PROMPTS_PATH = Path(__file__).resolve().parent.parent.parent.parent / 'prompts.json'

with open(PROMPTS_PATH, 'r', encoding='utf-8') as f:
    _prompts_data = json.load(f)

TAROT_PROMPT = '\n'.join(_prompts_data['prompts']['tarot'])
BAD_ANS_PROMPT = '\n'.join(_prompts_data['prompts']['bad_answer'])
RAP_PROMPT = '\n'.join(_prompts_data['prompts']['rap'])
DECISION_PROMPT = '\n'.join(_prompts_data['prompts']['decision'])
BAD_ADVICES = _prompts_data['random']['bad_advices']
YES_NO = _prompts_data['random']['yes_or_no']


logger = logging.getLogger(__name__)

def gen_response(style: str, content: str) -> str | None:
    client = GeminiApi()
    match style:
        case 'tarot':
            return _gen_tarot_resp(client, content)
        case 'bad_answer':
            return _gen_bad_ans_resp(client, content)
        case 'rap':
            return _gen_rap(client, content)
        case 'random_post':
            return _gen_random_post_resp(client, content)
        case _:
            return None


def _gen_tarot_resp(client: GeminiApi, content: str) -> str:
    logger.info(f"Generating tarot response.")

    result, _ = get_random_tarot_info()
    prompt = TAROT_PROMPT.format(card_result=result, cleaned_content=content)
    return client.create_response(prompt)


def _gen_bad_ans_resp(client: GeminiApi, content: str) -> str:
    logger.info(f"Generating bad ans response.")

    bad_ans = random.choice(BAD_ADVICES)
    prompt = BAD_ANS_PROMPT.format(cleaned_content=content, bad_ans=bad_ans)
    return client.create_response(prompt)


def _gen_rap(client: GeminiApi, content: str) -> str:
    logger.info(f"Generating rap response.")

    prompt = RAP_PROMPT.format(cleaned_content=content)
    return client.create_response(prompt)


def _gen_random_post_resp(client: GeminiApi, content: str) -> str:
    logger.info(f"Generating random post response.")

    choice = random.choice(YES_NO)
    prompt = DECISION_PROMPT.format(cleaned_content=content, choice=choice)
    return client.create_response(prompt)


if __name__ == "__main__":
    print(gen_response('tarot', '測試'))
