import argparse
import sys
import json
import socket
import threading
import time
import logging
import log.client_log_config
from errors import ReqFieldMissingError, ServerError, IncorrectDataRecivedError
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, \
    ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, EXIT, DESTINATION
from common.utils import get_data, send_data
from decorators import log

CLIENT_LOGGER = logging.getLogger('client')


@log
def create_exit_message(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def message_from_server(sock, my_username):
    while True:
        try:
            message = get_data(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'Received a message from the user '
                      f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Received a message from the user '
                                   f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'Received an invalid message from the server: {message}')
        except IncorrectDataRecivedError:
            CLIENT_LOGGER.error(f'Failed to decode received message.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Lost connection to server.')
            break


@log
def create_message(sock, account_name='Guest'):
    to_user = input('Enter message recipient: ')
    message = input('Enter a message to send: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'The message dictionary has been formed: {message_dict}')
    try:
        send_data(sock, message_dict)
        CLIENT_LOGGER.info(f'Message sent to user {to_user}')
    except:
        CLIENT_LOGGER.critical('Lost connection to server.')
        sys.exit(1)


@log
def user_interactive(sock, username):
    print_help()
    while True:
        command = input('Enter the command: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_data(sock, create_exit_message(username))
            print('Terminating the connection.')
            CLIENT_LOGGER.info('Shutdown by user command.')
            time.sleep(0.5)
            break
        else:
            print('Command not recognized, please try again. help - display supported commands.')


def print_help():
    print('Supported commands:')
    print('message - send a message. Who and the text will be requested separately.')
    print('help - display command tips')
    print('exit - exit the program')


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
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Attempting to start a client with an invalid port number: {server_port}. '
            f'Valid addresses are from 1024 to 65535. The client exits.')
        sys.exit(1)

    return server_address, server_port, client_name


def start_client():
    server_address, server_port, client_name = arg_parser()

    CLIENT_LOGGER.info(f'Launched client with parameters: '
                       f'address: {server_address} , port: {server_port}')
    print(f'Console messenger. Client module. Username: {client_name}')
    if not client_name:
        client_name = input('Enter your username: ')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_data(transport, create_presence_users(client_name))
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
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()
        CLIENT_LOGGER.debug('Processes started')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    start_client()
