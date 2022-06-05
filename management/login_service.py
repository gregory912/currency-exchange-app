from management.validation import Validation
from management.security.security import Security
from data_base.repository.user_repo import UserRepo
from data_base.repository.crud_repo import CrudRepo
from data_base.model.tables import UserTable, UserDataTable
from datetime import datetime


class Login:
    @staticmethod
    def does_account_exist():
        """Ask if the user already has an account"""
        print(f"{' ' * 12}Do you have a bank account?")
        response = Validation.get_answer(
            Validation.validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')
        return True if response == 'Y' else False

    @staticmethod
    def create_account(engine):
        """Create an account for the new user"""
        print(f'{" " * 12}Would you like to create an account?')
        response = Validation.get_answer(
            Validation.validation_of_answer,
            "Enter Y or N: ",
            'Entered value is not correct. Enter Y or N: ')
        if response == 'Y':
            while True:
                login = Validation.get_answer(
                    Validation.validation_alnum_and_not_digit,
                    'Enter Login: ',
                    'Entered data contains illegal characters. Try again: ')
                password = Security.encode(Security(), Validation.get_answer(
                    Validation.validation_alnum_and_not_digit,
                    'Enter Password: ',
                    'Entered data contains illegal characters. Try again: '))
                if UserRepo(engine, UserTable).find_user(login):
                    print(f'{" " * 12}Entered login is already used. Enter another login.')
                else:
                    break
            print('Enter user data:')
            name = Validation.get_answer(
                Validation.validation_alpha,
                'Enter your name: ',
                'Entered data contains illegal characters. Try again: ')
            surname = Validation.get_answer(
                Validation.validation_alpha,
                'Enter your surname: ',
                'Entered data contains illegal characters. Try again: ')
            country = Validation.get_answer(
                Validation.validation_alpha,
                'Enter the country where you come from: ',
                'Entered data contains illegal characters. Try again: ')
            address = Validation.get_answer(
                Validation.validation_space_or_alpha_not_digit,
                'Enter your address: ',
                'Entered data contains illegal characters. Try again: ')
            email = Validation.get_answer(
                Validation.validation_email,
                'Enter your email: ',
                'Entered data contains illegal characters. Try again: ')
            phone = Validation.get_answer(
                Validation.validation_digit,
                'Enter your phone: ',
                'Entered number should contain between 9 and 11 characters. Try again: ',
                (9, 11))
            user_1 = UserTable(login=login, password=password, creation_date=datetime.now())
            user_data_1 = UserDataTable(name=name, surname=surname, country=country,
                                        address=address, email=email, phone=phone)
            user_1.user_data_to_users = user_data_1
            CrudRepo(engine, UserTable).add_join(user_1)
            print(f'{" " * 12}Your account has been created')
        else:
            raise SystemExit(0)

    @staticmethod
    def login(engine):
        """Enter user data into the database. Encrypt the entered password"""
        while True:
            login = input('Enter your login: ')
            password = input('Enter your password: ')
            logged_in_user = UserRepo(engine, UserTable).find_user(login)
            if logged_in_user and Security.check_password(password, logged_in_user.password):
                print(f'\n{" " * 12}Welcome in your currency exchange account.')
                return logged_in_user
            else:
                print(f'{" " * 12}Account not found for the given data. Try again.')
