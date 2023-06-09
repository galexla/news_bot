from utils.news.tf_idf import most_similar_news_ids
from utils.news.utils import important_news_to_texts


def get_top_news(sentences: list[str], important_news: dict[dict]) -> list[dict]:
    """
    Tries to get top 5 news from GPT-3 chatbot. In case of failure
    gets it from top 10 of most important news

    :param important_news: news in format {id: {importance: float, news: dict}, ...}
    :type important_news: dict[dict]
    :return: top 5 news
    :rtype: list[dict]
    """
    text_keys = ('title', 'description', 'body')
    news_texts = important_news_to_texts(important_news, text_keys)
    ids = most_similar_news_ids(sentences, news_texts)
    top_news = []
    for _, news_id in ids.items():
        top_news.append(important_news[news_id]['news'])

    return top_news
