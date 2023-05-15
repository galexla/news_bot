from utils.misc import send_chatgpt_request
from utils.misc.json_value import get_json_value


def get_emotions(text: str) -> str:
    """
    Gets emotions from text item using GPT-3 chatbot

    :param text: text
    :type text: str
    :return: emotions
    :rtype: str
    """
    chatgpt_prompt = _get_chatgpt_prompt(text)
    response = send_chatgpt_request(chatgpt_prompt)

    emotions = get_json_value(
        response, ['choices', 0, 'message', 'content'])
    emotions = get_first(emotions, 10)

    return emotions


def _get_chatgpt_prompt(text: str) -> str:
    """
    Gets prompt for getting emotions from a text using GPT-3 chatbot

    :param text: text
    :type text: str
    :return: multiline string with prompt for GPT-3
    """
    return f'''Here is a news text. Please list emotions present in the text.
Do not add any other information, just list emotions in format: emotion1, emotion2, ...


{text}
'''


def get_first(emotions: str, count: int = 10) -> str:
    """
    Gets first N emotions from a string

    :param emotions: emotions
    :type emotions: str
    :param count: count of emotions to get
    :type count: int
    :return: first N emotions
    :rtype: str
    """
    items = (emotion.strip() for emotion in emotions.split(','))
    return ', '.join(item for item, _ in zip(items, range(count)))
