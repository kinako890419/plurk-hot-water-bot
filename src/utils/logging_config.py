import logging.config


def get_logging_config():

    json_formatter = {
        '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
        'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        'timestamp': True,
        'rename_fields': {
            'asctime': '@timestamp',
            'name': 'logger',
            'levelname': 'level',
            'message': 'message'
        },
        'json_ensure_ascii': False
    }

    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': json_formatter,
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        }
    }


def setup_logging():
    config = get_logging_config()
    logging.config.dictConfig(config)
