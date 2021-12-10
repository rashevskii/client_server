import argparse
import select
import socket
import sys
import logging
import time


from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, USER, \
    ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT
from common.utils import get_data, send_data
from decorators import log

SERVER_LOGGER = logging.getLogger('server')


@log
def processing_clients_messages(message, messages_list, client):
    SERVER_LOGGER.debug(f'Parsing a message from a client: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(
            f'Attempting to start the server with an invalid port '
            f'{listen_port}. Allowed addresses are from 1024 to 65535.')
        sys.exit(1)

    return listen_address, listen_port


def start_server():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Сначала обрабатываем порт:
    server.py -p 8888 -a 127.0.0.1
    :return:
    '''
    listen_address, listen_port = arg_parser()

    SERVER_LOGGER.info(
        f'Server started, port for connections: {listen_port}, '
        f'the address from which connections are accepted: {listen_address}. '
        f'If no address is specified, connections are accepted from any addresses.')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    clients = []
    messages = []

    transport.listen(MAX_CONNECTIONS)
    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Connected to PC {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    processing_clients_messages(get_data(client_with_message),
                                           messages, client_with_message)
                except:
                    SERVER_LOGGER.info(f'Client {client_with_message.getpeername()} '
                                f'disconnected from the server.')
                    clients.remove(client_with_message)

        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_data(waiting_client, message)
                except:
                    SERVER_LOGGER.info(f'Client {waiting_client.getpeername()} disconnected from the server.')
                    waiting_client.close()
                    clients.remove(waiting_client)


if __name__ == '__main__':
    start_server()
