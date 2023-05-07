from random import randint


def get_summary_input(news: list[dict], key: str) -> str:
    """
    Gets text for summary

    :param news: news
    :type news: list[dict]
    :param key: field to get text from
    :type key: str
    :return: text for summary
    :rtype: list[dict]
    """
    average_length = _get_average_length(news, key)
    news_count = _get_news_count_for_summary(news, average_length)
    news_for_summary = _get_news_for_summary(news, news_count)
    text_for_summary = _join_news(news_for_summary, key)

    return text_for_summary


def _get_average_length(news: list, key: str) -> int:
    """
    Calculates the average length of a news item

    :news: list of news
    :type news: list
    :key: field name to calculate the average length of
    :type key: str
    :raise ValueError: raised if news list is empty
    :raise ValueError: raised if key is empty
    :return: average length of a news item
    :rtype: int
    """
    if len(news) == 0:
        raise ValueError('News list is empty')

    if len(key) == 0:
        raise ValueError('Key is empty')

    total_length = 0

    for news_item in news:
        total_length += len(news_item[key])

    average_length = round(total_length / len(news))

    return average_length


def _get_news_count_for_summary(news: list[dict], average_length: int) -> int:
    """
    Calculates the number of news to be used for summary generation

    :news: list of news
    :type news: list[dict]
    :average_length: average length of a news item
    :type average_length: int
    :raise ValueError: raised if news list is empty
    :raise ValueError: raised if average length is less or equal to zero
    :return: number of news to be used for summary generation
    :rtype: int
    """
    if len(news) == 0:
        raise ValueError('News list is empty')

    if average_length <= 0:
        raise ValueError('Average length must be greater than zero')

    max_summary_input = 50000
    min_news_count = 50

    if len(news) < min_news_count:
        return len(news)

    news_count = round(max_summary_input / average_length)
    news_count = max(min_news_count, news_count)
    news_count = min(len(news), news_count)

    return news_count


def _get_news_for_summary(news: list, n_chunks: int) -> list[dict]:
    """
    Splits a list of news into chunks and returns a random news item from each chunk

    :news: list of news
    :type news: list[dict]
    :n_chunks: number of chunks
    :type n_chunks: int
    :raise ValueError: raised if news list is empty
    :raise ValueError: raised if number of chunks is less or equal to zero
    :return: list of random news items
    :rtype: list[dict]
    """
    if len(news) == 0:
        raise ValueError('News list is empty')

    if n_chunks <= 0:
        raise ValueError('Number of chunks must be greater than zero')

    result = []
    chunk_size = len(news) / n_chunks
    for i in range(n_chunks):
        start = round(i * chunk_size)
        end = round((i + 1) * chunk_size) - 1
        result.append(news[randint(start, end)])
    return result


def _join_news(news: list[dict], key: str) -> str:
    """
    Joins news text

    :param news: news
    :type news: list[dict]
    :param key: field to get text from
    :type key: str
    :return: joined news
    :rtype: str
    """
    # TODO: !! finish
    return ' '.join([item[key] for item in news])
