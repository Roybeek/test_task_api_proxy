import logging.config
import os

__all__ = (
    'SOURCE_1_URL',
    'SOURCE_2_URL'
)

SOURCE_1_URL = os.getenv('SOURCE_1_URL') if os.getenv('SOURCE_1_URL') else "http://127.0.0.1:8001/get_gas_station_info"
SOURCE_2_URL = os.getenv('SOURCE_2_URL') if os.getenv('SOURCE_2_URL') else "http://127.0.0.1:8001/get_fuel_info"

BASE_DIR = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "%(asctime)s [%(name)s] [%(levelname)s] %(module)s:%(lineno)s: %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
    },
    'handlers': {

        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },

        'main': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': '{0}'.format(os.path.join(BASE_DIR, 'logs/main.log')),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
        },
        'schedule': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': '{0}'.format(os.path.join(BASE_DIR, 'logs/schedule.log')),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
        },
        'all': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': '{0}'.format(os.path.join(BASE_DIR, 'logs/all.log')),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 10,
        },
    },
    'root': {
        'handlers': [],
    },

    'loggers': {
        'main': {
            'handlers': ['main', 'all', 'console'],
            'level': 'DEBUG',
            'propogate': True
        },
        'schedule': {
            'handlers': ['schedule', 'all', 'console'],
            'level': 'DEBUG',
            'propogate': True
        },
        'all': {
            'handlers': ['all', 'console'],
            'level': 'DEBUG',
            'propogate': True
        },
    }
}

logging.config.dictConfig(LOGGING)
