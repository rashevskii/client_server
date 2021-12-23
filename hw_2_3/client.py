import sys
import socket
import time
import argparse
import logging
import threading
import log.client_log_config
from common.variables import *
from common.utils import *
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from decorators import log
from metaclasses import ClientMaker

logger = logging.getLogger('client')


class ClientSender(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    def create_message(self):
        to = input('Enter message recipient: ')
        message = input('Enter a message to send: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'The message dictionary has been formed: {message_dict}')
        try:
            send_data(self.sock, message_dict)
            logger.info(f'Message sent to user {to}')
        except:
            logger.critical('Lost connection to server.')
            exit(1)

    def run(self):
        self.print_help()
        while True:
            command = input('Enter command: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_data(self.sock, self.create_exit_message())
                except:
                    pass
                print('Terminating the connection.')
                logger.info('Shutdown by user command.')
                time.sleep(0.5)
                break
            else:
                print('Command not recognized, please try again. help - display supported commands.')

    def print_help(self):
        print('Supported commands:')
        print('message - send a message. Who and the text will be requested separately.')
        print('help - display command tips')
        print('exit - exit the program')


class ClientReader(threading.Thread , metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_data(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'\nReceived a message from the user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    logger.info(f'Received a message from the user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    logger.error(f'Received an invalid message from the server: {message}')
            except IncorrectDataRecivedError:
                logger.error(f'Failed to decode received message.')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Lost connection to server.')
                break


@log
def create_presence(account_name):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f'Formed {PRESENCE} message for user {account_name}')
    return out


@log
def process_response_ans(message):
    logger.debug(f'Parsing a welcome message from the server: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
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
        logger.critical(
            f'Attempting to start a client with an invalid port number: {server_port}. Valid addresses are from 1024 to 65535. Client exits.')
        exit(1)

    return server_address, server_port, client_name


def main():
    print('Console messenger. Client module.')

    server_address, server_port, client_name = arg_parser()

    if not client_name:
        client_name = input('Enter username: ')
    else:
        print(f'The client module is launched with the name: {client_name}')

    logger.info(
        f'Launched client with parameters: server address: {server_address} , port: {server_port}, username: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_data(transport, create_presence(client_name))
        answer = process_response_ans(get_data(transport))
        logger.info(f'A connection to the server has been established. Server response: {answer}')
        print(f'A connection to the server has been established.')
    except json.JSONDecodeError:
        logger.error('Failed to decode received Json string.')
        exit(1)
    except ServerError as error:
        logger.error(f'When establishing a connection, the server returned an error: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        logger.error(f'Required field missing in server response {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(
            f'Failed to connect to server {server_address}:{server_port}, the destination computer rejected the connection request.')
        exit(1)
    else:
        module_reciver = ClientReader(client_name , transport)
        module_reciver.daemon = True
        module_reciver.start()

        module_sender = ClientSender(client_name , transport)
        module_sender.daemon = True
        module_sender.start()
        logger.debug('Processes started')

        while True:
            time.sleep(1)
            if module_reciver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
