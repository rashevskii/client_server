import sys
import os
import logging.handlers

sys.path.append('../')
from common.variables import LOGGING_LEVEL

FORMATTER_FOR_SERVER = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s %(filename)s %(message)s')

PATH = os.path.dirname(os.path.abspath(__file__))
CURRENT_PATH = os.path.join(PATH, 'logs/server.log')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER_FOR_SERVER)
STREAM_HANDLER.setLevel(logging.ERROR)

LOG_FILE = logging.handlers.TimedRotatingFileHandler(CURRENT_PATH, encoding='utf8', interval=1, when='S')
LOG_FILE.setFormatter(FORMATTER_FOR_SERVER)

LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
