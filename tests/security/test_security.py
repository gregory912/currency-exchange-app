import unittest
from management.security.security import Security
import random


class SecurityTest(unittest.TestCase):
    def test_encode_and_decode(self):
        """The method tests methods encode and decode in Security Class"""
        password = self.get_password(10)
        password_hash = Security().encode(password)
        decrypted_password = Security().check_password(password, password_hash)
        self.assertTrue(decrypted_password, 'Method test_encode_and_decode return wrong values')

    @staticmethod
    def get_password(amount: int) -> str:
        """The method randomizes the letters and returns a string"""
        return ''.join([chr(random.randint(65, 90)) for _ in range(amount)])


if __name__ == '__main__':
    unittest.main()
