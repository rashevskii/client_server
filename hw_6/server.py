import socket
import sys
import json
import logging
import log.server_log_config
from errors import IncorrectDataRecivedError
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, RESPONDEFAULT_IP_ADDRESSSE
from common.utils import get_data, send_data
from decorators import log

SERVER_LOGGER = logging.getLogger('server')


@log
def processing_clients_messages(message):
    SERVER_LOGGER.debug(f'Parsing a message from a client: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESSSE: 400,
        ERROR: 'Bad Request'
    }


def start_server():
    '''
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    Сначала обрабатываем порт:
    server.py -p 8888 -a 127.0.0.1
    :return:
    '''

    if '-p' in sys.argv:
        listen_port = int(sys.argv[sys.argv.index('-p') + 1])
    else:
        listen_port = DEFAULT_PORT
    if listen_port < 1024 or listen_port > 65535:
        SERVER_LOGGER.critical(f'Attempting to start the server with an invalid port '
                               f'{listen_port}. Allowed addresses are from 1024 to 65535.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        SERVER_LOGGER.critical(f'After the parameter \'a\' - you must specify the address that the server will '
                               'listen to')
        sys.exit(1)

    SERVER_LOGGER.info(f'Server started, port for connections: {listen_port}, address: {listen_address}. '
                       f'If no address is specified, connections are accepted from any addresses.')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        SERVER_LOGGER.info(f'Connected with {client_address}')
        try:
            message_from_client = get_data(client)
            SERVER_LOGGER.debug(f'Get message {message_from_client}')
            response = processing_clients_messages(message_from_client)
            SERVER_LOGGER.info(f'Response for client {response}')
            send_data(client, response)
            SERVER_LOGGER.debug(f'Connect {client_address} exit.')
            client.close()
        except json.JSONDecodeError:
            SERVER_LOGGER.error(f'Failed to decode json from client {client_address}. Connection is closed')
            client.close()
        except IncorrectDataRecivedError:
            SERVER_LOGGER.error(f'From client {client_address} incorrect data received. Connection is closed')
            client.close()


if __name__ == '__main__':
    start_server()
