import sys
import os
import logging

sys.path.append('../')
from common.variables import LOGGING_LEVEL

FORMATTER_FOR_CLIENT = logging.Formatter('%(asctime)s %(levelname)-8s %(module)s %(filename)s %(message)s')

PATH = os.path.dirname(os.path.abspath(__file__))
CURRENT_PATH = os.path.join(PATH, 'logs/client.log')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(FORMATTER_FOR_CLIENT)
STREAM_HANDLER.setLevel(logging.ERROR)

LOG_FILE = logging.FileHandler(CURRENT_PATH, encoding='utf-8')
LOG_FILE.setFormatter(FORMATTER_FOR_CLIENT)

LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
