from unittest.mock import patch


def test_debug_setup():
    with patch('debugpy.listen') as mock_listen, patch(
        'debugpy.wait_for_client'
    ) as mock_wait:
        with patch('config_data.config.DEBUG', True):
            import debugger  # noqa

        mock_listen.assert_called_once_with(('0.0.0.0', 5678))
        mock_wait.assert_called_once()


def test_no_debug_setup():
    with patch('debugpy.listen') as mock_listen, patch(
        'debugpy.wait_for_client'
    ) as mock_wait:
        with patch('config_data.config.DEBUG', False):
            import debugger  # noqa

        mock_listen.assert_not_called()
        mock_wait.assert_not_called()
