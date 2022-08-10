from management.services.currency_exchange_service import CurrencyExchange
import unittest


class MyTestCase(unittest.TestCase):
    def test_correct_data(self):
        """Verify that API queries return correct values"""
        exchange_1 = CurrencyExchange().get_result("GBP", "USD", "100")
        exchange_2 = CurrencyExchange().get_result("CHF", "EUR", "90.5")
        self.assertIsInstance(exchange_1['info']['rate'], float,
                              'Method test_correct_data return wrong values.')
        self.assertIsInstance(exchange_1['result'], float,
                              'Method test_correct_data return wrong values.')
        self.assertIsInstance(exchange_2['info']['rate'], float,
                              'Method test_correct_data return wrong values.')
        self.assertIsInstance(exchange_2['result'], float,
                              'Method test_correct_data return wrong values.')

    def test_wrong_data(self):
        """Check if incorrectly entered data raises an exception"""
        self.assertRaises(Exception, CurrencyExchange().get_result("123", "USD", "100"),
                          'Method test_wrong_data return wrong values.')
        self.assertRaises(Exception, CurrencyExchange().get_result("GBP", "123", "100"),
                          'Method test_wrong_data return wrong values.')
        self.assertRaises(Exception, CurrencyExchange().get_result("GBP", "USD", "10abc0"),
                          'Method test_wrong_data return wrong values.')


if __name__ == '__main__':
    unittest.main()
