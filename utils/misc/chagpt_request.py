from utils.misc import api_request


def send_chatgpt_request(prompt: str) -> list | dict:
    """
    Sends request to GPT-3 chatbot

    :param prompt: prompt for GPT-3 chatbot
    :type prompt: str
    :return: response from GPT-3 chatbot
    :rtype: list | dict
    """
    url = "https://openai80.p.rapidapi.com/chat/completions"

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "ea1331345emshee44dbb8dc2d3dep1e50c2jsne86eb1384009",
        "X-RapidAPI-Host": "openai80.p.rapidapi.com"
    }

    json_ = api_request('POST', url, headers, payload, retry_on_too_many=False)

    return json_
