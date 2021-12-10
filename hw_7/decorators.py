import sys
import logging
import log.server_log_config
import log.client_log_config
import traceback
import inspect

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func_to_log):
    def log_saver(*args, **kwargs):
        ret = func_to_log(*args, **kwargs)
        LOGGER.debug(f'The {func_to_log.__name__} function was called with parameters {args}, {kwargs}. '
                     f'Call from module {func_to_log.__module__}.'
                     f'Call from function {traceback.format_stack()[0].strip().split()[-1]}.'
                     f'Call from function {inspect.stack()[1][3]}')
        return ret
    return log_saver
