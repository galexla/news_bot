from utils.misc import api_request


def test_wrong_api_request():
    # TODO: mock?
    assert api_request('', '', {}, {}) is None
    assert api_request('POST', '', {}, {}) is None
