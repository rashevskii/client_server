import socket
import sys
import argparse
import logging
import select
import log.server_log_config
from common.variables import *
from common.utils import *
from decorators import log
from descriptors import Port
from metaclasses import ServerMaker

logger = logging.getLogger('server')


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


class Server(metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port):
        self.addr = listen_address
        self.port = listen_port
        self.clients = []
        self.messages = []
        self.names = dict()

    def init_socket(self):
        logger.info(
            f'Server started, port for connections: {self.port}, '
            f'the address from which connections are accepted: {self.addr}. '
            f'If no address is specified, connections are accepted from any addresses.')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)
        self.sock = transport
        self.sock.listen()

    def main_loop(self):
        self.init_socket()
        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'Connected to PC {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_data(client_with_message), client_with_message)
                    except:
                        logger.info(f'Client {client_with_message.getpeername()} disconnect from server.')
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except:
                    logger.info(f'Customer contact with name {message[DESTINATION]} was lost')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] in listen_socks:
            send_data(self.names[message[DESTINATION]], message)
            logger.info(f'Send message to user {message[DESTINATION]} from user {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'User {message[DESTINATION]} not registered on the server, sending a message is not possible.')

    def process_client_message(self, message, client):
        logger.debug(f'Parsing a message from a client: {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_data(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Username is already busy.'
                send_data(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'The request is invalid.'
            send_data(client, response)
            return


def main():
    listen_address, listen_port = arg_parser()
    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()
