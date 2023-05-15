import re
from typing import List


def get_text_excerpts(text: str, max_length: int,
                      n_parts: int = 3, parts_sep: str = '\n...\n') -> str:
    """
    Concatenates n_parts part of text with parts_sep. Each part consists of
    several sentences. The overall length of the result is max_length or less.

    :param text: text
    :type text: str
    :param max_length: max length of resulting text
    :type max_length: int
    :param n_parts: number of parts to split text into
    :type n_parts: int
    :param parts_sep: separator between parts
    :type parts_sep: str
    :return: sentences
    :rtype: str
    """
    if not text or max_length <= 0:
        return ''

    max_length = min(max_length, len(text))

    sentences = re.findall(r'.+?[.!?]+\s*', text)
    n_sentences = len(sentences)

    if n_sentences == 0:
        return text

    n_parts = min(n_parts, n_sentences // 2)

    if n_parts <= 1:
        return text

    len_sep = len(parts_sep)
    max_length -= len_sep * (n_parts - 1)

    sentence_ids = [round(i * n_sentences / n_parts)
                    for i in range(n_parts + 1)]

    result = ''
    length_left = max_length
    for i_sentence in range(n_parts):
        length = length_left // (n_parts - i_sentence)
        i_beg = sentence_ids[i_sentence]
        i_end = sentence_ids[i_sentence + 1]
        result += _get_sentences(sentences, i_beg, i_end, length)

        if i_sentence < n_parts - 1:
            result += parts_sep
        length_left = max_length - len(result)

    return result


def _get_sentences(sentences: List[str], i_beg: int, i_end: int,
                   max_length: int) -> str:
    """
    Gets sentences from text

    :param sentences: sentences
    :type sentences: List[str]
    :param i_beg: sentence to start from
    :type i_beg: int
    :param i_end: maximal sentence index to end with
    :type i_end: int
    :param max_length: max length of resulting text
    :type max_length: int
    :return: sentences
    :rtype: str
    """
    result = ''
    length = 0
    for sentence in sentences[i_beg:i_end + 1]:
        length += len(sentence)
        if length > max_length:
            break
        result += sentence

    return result
