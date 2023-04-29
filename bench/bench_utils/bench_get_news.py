import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

import time
from typing import Iterable

from python_basic_diploma.utils import get_news


def bench_get_news_10() -> None:
    # 3 queries, 10 news per page
    one_query_time = _bench_get_news(page_numbers=[1, 5, 15], page_size=10)
    print(f'one_query_time = {one_query_time}s')   # time = 1.4-2s


def bench_get_news_50() -> None:
    # 3 queries, 50 news per page
    one_query_time = _bench_get_news(page_numbers=[1, 3, 5], page_size=50)
    print(f'one_query_time = {one_query_time}s')  # time = 1.4-1.9s


def _bench_get_news(page_numbers: Iterable[int], page_size: int, t_sleep: float = 0.1) -> float:
    n_repeat = len(page_numbers)
    t1 = time.time_ns()
    for i_step in range(n_repeat):
        news = get_news('USA', page_numbers[i_step], page_size,
                        '2023-04-03T00:00:00', '2023-04-09T23:59:59')
        time.sleep(t_sleep)
    return round((time.time_ns() - t1) / 1000000000 / n_repeat, 4)


def main() -> None:
    bench_get_news_50()


if __name__ == '__main__':
    main()
