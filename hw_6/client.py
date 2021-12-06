import sys
import json
import socket
import time
import logging
import log.client_log_config
from errors import ReqFieldMissingError
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR
from common.utils import get_data, send_data
from decorators import log

CLIENT_LOGGER = logging.getLogger('client')


@log
def create_presence_users(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Generated {PRESENCE} a message for the user {account_name}')
    return out


@log
def parsing_answer(message):
    CLIENT_LOGGER.debug(f'Parsing a message: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


def start_client():
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    if server_port < 1024 or server_port > 65535:
        CLIENT_LOGGER.critical(
            f'Attempting to start a client with an invalid port number: {server_port}.'
            f' Valid addresses are from 1024 to 65535. The client exits.')
        sys.exit(1)

    CLIENT_LOGGER.info(f'Launched client with parameters: '
                       f'address: {server_address} , port: {server_port}')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = create_presence_users()
    send_data(transport, message_to_server)
    try:
        answer = parsing_answer(get_data(transport))
        CLIENT_LOGGER.info(f'Received a response from the server {answer}')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Failed to decode json.')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Failed to connect to server {server_address}:{server_port}, '
                               f'connection request rejected.')
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'Required field missing in server response '
                            f'{missing_error.missing_field}')


if __name__ == '__main__':
    start_client()
