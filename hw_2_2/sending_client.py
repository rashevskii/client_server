import argparse
import sys
import json
import socket
import time
import logging
import log.client_log_config
from errors import ReqFieldMissingError, ServerError
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, \
    ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT
from common.utils import get_data, send_data
from decorators import log

CLIENT_LOGGER = logging.getLogger('client')

@log
def message_from_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Received a message from the user '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Received a message from the user '
                    f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Received an invalid message from the server: {message}')


@log
def create_message(sock, account_name='Guest'):
    message = input('Enter a message to send or \'!!!\' to complete the work: ')
    if message == '!!!':
        sock.close()
        CLIENT_LOGGER.info('Shutdown by user command.')
        print('Thank you for using our service!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'The message dictionary has been formed: {message_dict}')
    return message_dict


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
    CLIENT_LOGGER.debug(f'Parsing a message from server: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='send', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Attempting to start a client with an invalid port number: {server_port}. '
            f'Valid addresses are from 1024 to 65535. The client exits.')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f'Invalid operating mode specified {client_mode}, '
                        f'allowable modes: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode


def start_client():
    server_address, server_port, client_mode = arg_parser()

    CLIENT_LOGGER.info(f'Launched client with parameters: '
                       f'address: {server_address} , port: {server_port}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presence_users()
        send_data(transport, message_to_server)
        answer = parsing_answer(get_data(transport))
        CLIENT_LOGGER.info(f'Received a response from the server {answer}')
        print(f'Received a response from the server.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Failed to decode json.')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'When establishing a connection, the server returned an error: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'Required field missing in server response {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Failed to connect to server {server_address}:{server_port}, '
                               f'connection request rejected.')
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('Mode of operation - sending messages.')
        else:
            print('Mode of operation - receiving messages.')
        while True:
            if client_mode == 'send':
                try:
                    send_data(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Server connection {server_address} was lost.')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    message_from_server(get_data(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    CLIENT_LOGGER.error(f'Server connection {server_address} was lost.')
                    sys.exit(1)


if __name__ == '__main__':
    start_client()
