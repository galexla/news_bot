import importlib
import sys
from unittest.mock import patch

with patch('database.init_db.init_db'), patch(
    'database.init_db.create_tables'
), patch('loader.TeleBot'), patch('loader.redis.Redis'), patch(
    'loader.loguru.logger.add'
), patch(
    'loader.StateRedisStorage'
):
    import loader


@patch('loader.telebot_logger.setLevel')
@patch('loader.loguru.logger.add')
@patch('loader.TeleBot')
@patch('loader.StateRedisStorage')
@patch('loader.redis.Redis')
@patch('database.init_db.init_db')
@patch('database.init_db.create_tables')
def test_initialization(
    mock_create_tables,
    mock_init_db,
    mock_redis,
    mock_storage,
    mock_bot,
    mock_logger_add,
    mock_setLevel,
):
    importlib.reload(loader)

    assert mock_logger_add.call_count == 3
    mock_logger_add.assert_any_call(
        sys.stdout, level=loader.config.LOG_LEVEL_APP
    )
    mock_logger_add.assert_any_call(
        'logs/app.log', level=loader.config.LOG_LEVEL_APP, rotation='30 MB'
    )
    mock_logger_add.assert_any_call(
        'logs/error.log', level='ERROR', rotation='30 MB'
    )

    # mock_storage.assert_called_once_with(
    #     host=loader.config.REDIS_HOST, port=loader.config.REDIS_PORT,
    #     db=loader.config.REDIS_DB, password=loader.config.REDIS_PASSWORD)
    # mock_bot.assert_called_once_with(token=loader.config.BOT_TOKEN,
    #                                  state_storage=loader.storage)
    mock_setLevel.assert_called_once_with(loader.config.LOG_LEVEL_BOT)

    mock_redis.assert_called_once_with(
        host=loader.config.REDIS_HOST,
        port=loader.config.REDIS_PORT,
        db=loader.config.REDIS_DB,
        password=loader.config.REDIS_PASSWORD,
        decode_responses=True,
        encoding='utf-8',
        socket_timeout=None,
        health_check_interval=10,
    )

    mock_init_db.assert_called_once_with(
        loader.config.POSTGRES_DB,
        host=loader.config.POSTGRES_HOST,
        user=loader.config.POSTGRES_USER,
        password=loader.config.POSTGRES_PASSWORD,
        port=loader.config.POSTGRES_PORT,
    )

    mock_create_tables.assert_called_once()
