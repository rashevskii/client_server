import unittest
from common.variables import RESPONDEFAULT_IP_ADDRESSSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from server import processing_clients_messages


class TestServer(unittest.TestCase):
    err_dict = {
        RESPONDEFAULT_IP_ADDRESSSE: 400,
        ERROR: 'Bad Request'
    }
    ok_dict = {RESPONDEFAULT_IP_ADDRESSSE: 200}

    def test_ok_check(self):
        self.assertEqual(processing_clients_messages(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.ok_dict)

    def test_no_action(self):
        self.assertEqual(processing_clients_messages(
            {TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_wrong_action(self):
        self.assertEqual(processing_clients_messages(
            {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_no_time(self):
        self.assertEqual(processing_clients_messages(
            {ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_no_user(self):
        self.assertEqual(processing_clients_messages(
            {ACTION: PRESENCE, TIME: '1.1'}), self.err_dict)

    def test_unknown_user(self):
        self.assertEqual(processing_clients_messages(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest1'}}), self.err_dict)


if __name__ == '__main__':
    unittest.main()
