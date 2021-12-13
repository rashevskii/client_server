import unittest
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_presence_users, parsing_answer


class TestClass(unittest.TestCase):

    def test_def_presense(self):
        test = create_presence_users()
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_ans(self):
        self.assertEqual(parsing_answer({RESPONSE: 200}), '200 : OK')

    def test_400_ans(self):
        self.assertEqual(parsing_answer({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        self.assertRaises(ValueError, parsing_answer, {ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
