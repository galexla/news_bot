import json
import os
from unittest.mock import patch

from tests import test_utils
with patch('database.init_db.init_db'), \
        patch('database.init_db.create_tables'):
    from utils.news import tf_idf


def get_news_test_data() -> dict[str]:
    """Gets news from json files in data directory and page size"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    news = test_utils.load_news_from_dir(data_dir)
    texts = {item['id']: item['body'] for item in news}
    return texts


def get_summary_test_data() -> list[str]:
    file_path = os.path.join(
        os.path.dirname(__file__), 'data', 'summary_ecology_20230403.txt')
    with open(file_path, 'r') as f:
        summary = f.read().strip().split('\n')
    return summary


def get_top_news_test_data() -> dict[str, str]:
    file_path = os.path.join(
        os.path.dirname(__file__), 'data', 'top_news_ecology_20230403.json')
    with open(file_path, 'r') as f:
        top_news = json.load(f)
    return top_news


def test_most_similar_news_ids():
    news_texts = get_news_test_data()
    sentences = get_summary_test_data()
    actual = tf_idf.most_similar_news_ids(sentences, news_texts)
    expected = get_top_news_test_data()
    assert actual == expected
