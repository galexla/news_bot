from typing import Iterable, Optional


def get_json_value(
    json_obj: Optional[dict | list], keys: Iterable | str | int
) -> any:
    """
    Gets a deep value from the JSON object using a chains of keys

    :param json_obj: text
    :type json_obj: Optional[dict | list]
    :param keys: chains of keys or one key
    :type keys: Iterable | str | int
    :return: value
    :rtype: any
    """
    if json_obj is None or len(keys) == 0:
        return None

    if isinstance(keys, str | int):
        keys = (keys,)

    current = json_obj
    try:
        for key in keys:
            if not isinstance(key, (str, int)):
                return None
            current = current[key]
    except (KeyError, IndexError):
        return None

    return current
