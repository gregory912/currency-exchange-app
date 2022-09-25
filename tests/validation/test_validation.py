import unittest
from management.validation import *


class TestCrudRepo(unittest.TestCase):
    def test_validation_of_answer_correct_answer(self):
        """Test if the method returns True for valid values"""
        self.assertTrue(validation_of_answer('Y'))
        self.assertTrue(validation_of_answer('N'))

    def test_validation_of_answer_wrong_answer(self):
        """Test if the method returns False for the forbidden element"""
        self.assertFalse(validation_of_answer('a'))

    def test_validation_of_answer_digit(self):
        """Test if the method returns False for the forbidden element"""
        self.assertFalse(validation_of_answer('1'))

    def test_validation_of_answer_empty_string(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_of_answer(''))

    def test_alnum_and_not_digit_correct_values(self):
        """Test if method returns True for letters and numbers"""
        self.assertTrue(validation_alnum_and_not_digit('abc123'))
        self.assertTrue(validation_alnum_and_not_digit('ABC123'))

    def test_alnum_and_not_digit_letters_with_space(self):
        """Test if the method returns False for the forbidden elements"""
        self.assertFalse(validation_alnum_and_not_digit('a b'))

    def test_alnum_and_not_digit_only_digit(self):
        """Test if the method returns False for the forbidden element"""
        self.assertFalse(validation_alnum_and_not_digit('1'))

    def test_alnum_and_not_digit_empty_string(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_alnum_and_not_digit(''))

    def test_alpha_correct_values(self):
        """Test if method returns True for letters"""
        self.assertTrue(validation_alpha('abc'))
        self.assertTrue(validation_alpha('ABC'))

    def test_alpha_with_space(self):
        """Test if the method returns False for the forbidden element"""
        self.assertFalse(validation_alpha('a b'))

    def test_alpha_with_digit(self):
        """Test if the method returns False for the forbidden element"""
        self.assertFalse(validation_alpha('1 '))

    def test_alpha_empty_string(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_alpha(''))

    def test_digit_correct_values(self):
        """Test if method returns True for digits"""
        self.assertTrue(validation_digit('123', 2, 3))
        self.assertTrue(validation_digit('987', 2, 3))

    def test_digit_letters(self):
        """Test if the method returns False for the forbidden element"""
        self.assertFalse(validation_digit('a b', 2, 3))

    def test_digit_letter_and_digit(self):
        """Test if the method returns False for the forbidden element"""
        self.assertFalse(validation_digit('a 1', 2, 3))

    def test_digit_empty_stringt(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_digit('', 2, 3))

    def test_space_or_alpha_not_digit_correct_values(self):
        """Test if method returns True for letters, spaces and digits"""
        self.assertTrue(validation_space_or_alpha_not_digit('abc 123'))
        self.assertTrue(validation_space_or_alpha_not_digit('a8'))

    def test_space_or_alpha_not_digit_digits(self):
        """Test if the method returns False for digits only"""
        self.assertFalse(validation_space_or_alpha_not_digit('123'))

    def test_space_or_alpha_not_digit_digits_with_space(self):
        """Test if the method returns False for the forbidden elements"""
        self.assertFalse(validation_space_or_alpha_not_digit('1 2'))
        self.assertFalse(validation_space_or_alpha_not_digit('12 '))
        self.assertFalse(validation_space_or_alpha_not_digit(' 12'))

    def test_space_or_alpha_not_digit_empty_string(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_space_or_alpha_not_digit(''))

    def test_decimal_correct_values(self):
        """Test if method returns True for string which will be converted to Decimal"""
        self.assertTrue(validation_decimal('12.52'))
        self.assertTrue(validation_decimal('100'))

    def test_decimal_with_comma(self):
        """Test if the method returns False for the forbidden element"""
        self.assertFalse(validation_decimal('11,11'))

    def test_decimal_space(self):
        """Test if the method returns False for the forbidden element"""
        self.assertFalse(validation_decimal('14 1'))

    def test_decimal_empty_string(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_decimal(''))

    def test_email_correct_emails(self):
        """Test if method returns True for string which is an email"""
        self.assertTrue(validation_email('user@email.com'))
        self.assertTrue(validation_email('user.name@email.com'))

    def test_email_without_symbol(self):
        """Test if the method returns False for string with the symbol @"""
        self.assertFalse(validation_email('usernameemail.com'))

    def test_email_wrong_symbol(self):
        """Test if the method returns False for the forbidden element"""
        self.assertFalse(validation_email('username&email.com'))

    def test_email_empty_string(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_email(''))

    def test_chosen_operation_correct_values(self):
        """Test if method returns True for chosen digit of operation"""
        self.assertTrue(validation_chosen_operation('1', 1, 3))
        self.assertTrue(validation_chosen_operation('2', 1, 3))

    def test_chosen_operation_wrong_value(self):
        """Test if the method returns False for a wrong value"""
        self.assertFalse(validation_chosen_operation('4', 1, 3))

    def test_chosen_operation_letter(self):
        """Test if the method returns False for a string"""
        self.assertFalse(validation_chosen_operation('a', 1, 3))

    def test_chosen_operation_empty_string(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_chosen_operation('', 1, 3))

    def test_choose_account_correct_values(self):
        """Test if method returns True for chosen digit of account"""
        self.assertTrue(validation_choose_account('1', {1: 'one', 2: 'two'}))
        self.assertTrue(validation_choose_account('1', {1: 'one', 2: 'two'}))

    def test_choose_account_wrong_value(self):
        """Test if the method returns False for a wrong value"""
        self.assertFalse(validation_choose_account('3', {1: 'one', 2: 'two'}))

    def test_choose_account_string(self):
        """Test if the method returns False for a string"""
        self.assertFalse(validation_choose_account('one', {1: 'one', 2: 'two'}))

    def test_choose_empty_string(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_choose_account('', {1: 'one', 2: 'two'}))

    def test_file_name_correct_names(self):
        """Test if method returns True for file name which include only permitted characters"""
        self.assertTrue(validation_file_name('file'))
        self.assertTrue(validation_file_name('file_123'))

    def test_file_name_forbidden_symbol(self):
        """Test if the method returns False for the forbidden elements"""
        self.assertFalse(validation_file_name('file/'))
        self.assertFalse(validation_file_name('file*'))

    def test_file_name_empty_string(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_file_name(''))

    def test_file_path_correct_path(self):
        """Test if method returns True for file path which exists"""
        self.assertTrue(validation_file_path('C:\\'))

    def test_file_path_forbidden_symbols(self):
        """Test if the method returns False for the forbidden elements"""
        self.assertFalse(validation_file_path('C:\\*'))
        self.assertFalse(validation_file_path('C:\\?'))

    def test_file_path_empty_string(self):
        """Test if the method returns False for the empty string"""
        self.assertFalse(validation_file_path(''))


if __name__ == '__main__':
    unittest.main()
