from management.validation import *
from data_base.repository.crud_repo import CrudRepo
from data_base.repository.user_account_repo import UserAccountRepo
from data_base.model.tables import *
from decimal import Decimal
from management.conversions import *
from management.services.currency_exchange_service import CurrencyExchange
from management.services.card_management_service import CardManagementService
from datetime import date


class CardTransactionsService:
    @staticmethod
    def pay_by_card(engine, used_card: namedtuple, logged_in_user: namedtuple):
        """Perform card payments taking into account all currency conversions and the correct calculation of the
        account balance after the operation."""
        card = card_all_named_tuple(CrudRepo(engine, CardTable).find_by_id(used_card.id))
        if not card.blocked or card.card_type == "SINGLE-USE VIRTUAL":
            type_of_payment = CardTransactionsService.choose_payment_type()
            if CardTransactionsService.check_security(type_of_payment, card):
                used_account, ented_amt, amt_exched, rate, currency, exched_amt_for_limit_checking = \
                    CardTransactionsService.find_the_best_account_for_transaction(engine, logged_in_user, card)
                if not used_account:
                    return False
                if CardTransactionsService.check_daily_limit(engine, used_account, card, exched_amt_for_limit_checking):
                    if type_of_payment == "Contactless payment":
                        if exched_amt_for_limit_checking["result"] < card.contactless_limit:
                            CardTransactionsService.add_card_transaction(
                                engine, used_account, used_card, (amt_exched if amt_exched else ented_amt),
                                0, used_account.balance - (amt_exched if amt_exched else ented_amt),
                                "YES", "NO", exched_amt_for_limit_checking["info"]["rate"],
                                "Contactless payment", rate, None)
                            CardTransactionsService.update_account(
                                engine, used_account,
                                (used_account.balance - amt_exched if amt_exched else used_account.balance - ented_amt))
                        else:
                            print(f"\n{' ' * 12}Your contactless transaction limit does not allow you to "
                                  f"complete the transaction. Change your limit..")
                    elif type_of_payment == "Internet payment":
                        if (card.card_type == "STANDARD" and exched_amt_for_limit_checking["result"] < card.internet_limit)\
                                or card.card_type != "STANDARD":
                            CardTransactionsService.add_card_transaction(
                                engine, used_account, used_card, (amt_exched if amt_exched else ented_amt),
                                0, used_account.balance - (amt_exched if amt_exched else ented_amt),
                                "YES", "NO", exched_amt_for_limit_checking["info"]["rate"],
                                "Internet payment", rate, None)
                            CardTransactionsService.update_account(
                                engine, used_account,
                                (used_account.balance - amt_exched if amt_exched else used_account.balance - ented_amt))
                            if card.card_type == "SINGLE-USE VIRTUAL":
                                CardManagementService.delete_card(engine, used_card, logged_in_user)
                        else:
                            print(f"\n{' ' * 12}Your internet transaction limits do not allow you to "
                                  f"complete the transaction. Change your limit.")
                    elif type_of_payment == "Magnetic stripe payment":
                        CardTransactionsService.add_card_transaction(
                            engine, used_account, used_card, (amt_exched if amt_exched else ented_amt),
                            0, used_account.balance - (amt_exched if amt_exched else ented_amt),
                            "YES", "NO", exched_amt_for_limit_checking["info"]["rate"],
                            "Magnetic stripe payment", rate, None)
                        CardTransactionsService.update_account(
                            engine, used_account,
                            (used_account.balance - amt_exched if amt_exched else used_account.balance - ented_amt))
                else:
                    print(
                        f"\n{' ' * 12}We are unable to complete your transaction because the daily limit has "
                        f"been exceeded. Change your daily limit to be able to make transactions.")
        else:
            print(f"\n{' ' * 12}Your card is blocked. We cannot complete your transaction.")

    @staticmethod
    def withdraw_money(engine, used_card: namedtuple, logged_in_user: namedtuple):
        """Perform card payment operations. Check that the card is not blocked and that
        it has sufficient funds. If possible, select the account with the currency you want to select from the ATM."""
        card = card_all_named_tuple(CrudRepo(engine, CardTable).find_by_id(used_card.id))
        if not card.blocked:
            if CardTransactionsService.check_security('Withdrawals ATM', card):
                used_account, entred_amt, amt_exched, rate, currency, exchanged_amount_for_limit_checking = \
                    CardTransactionsService.find_the_best_account_for_transaction(engine, logged_in_user, card)
                if not used_account:
                    return False
                if CardTransactionsService.check_daily_limit(engine, used_account, card, exchanged_amount_for_limit_checking):
                    CardTransactionsService.add_card_transaction(
                        engine, used_account, used_card, (amt_exched if amt_exched else entred_amt),
                        0, used_account.balance - (amt_exched if amt_exched else entred_amt),
                        "YES", "NO", exchanged_amount_for_limit_checking["info"]["rate"],
                        "Withdrawals ATM", rate, None)
                    CardTransactionsService.update_account(
                        engine, used_account,
                        (used_account.balance - amt_exched if amt_exched else used_account.balance - entred_amt))
        else:
            print(f"\n{' ' * 12}Your card is blocked. We cannot complete your transaction.")

    @staticmethod
    def deposit_money(engine, used_card: namedtuple, logged_in_user: namedtuple):
        """Deposit money by card. Make a deposit to the appropriate account, if necessary, convert the amount."""
        amount = Decimal(get_answer(
            validation_decimal,
            'Enter the amount: ',
            'Entered data contains illegal characters. Try again: '))
        currency = CardManagementService.choose_currency('Choose the currency in which you want to deposit money: ')
        accounts = CrudRepo(engine, UserAccountTable).find_all_with_condition(
            (UserAccountTable.id_user_data, logged_in_user.id))
        accounts = [user_account_named_tuple(item) for item in accounts]
        payer_acc_number = get_answer(
            validation_digit,
            'Enter the payer account number: ',
            'Entered data is not correct. The number should contain between 20 - 26 digits. Try again: ',
            (20, 26))
        for x in accounts:
            if x.currency == currency:
                used_account = x
                break
        else:
            used_account = accounts[0]
        if used_account.currency != currency:
            response = CurrencyExchange().get_result(currency, used_account.currency, str(amount))
            amount = Decimal(response["result"])
            rate = Decimal(response['info']['rate'])
        else:
            rate = 1
        CardTransactionsService.add_card_transaction(
            engine, used_account, used_card, amount, 0, used_account.balance + amount,
            "NO", "YES", 0, "Deposit money", rate, payer_acc_number)
        CardTransactionsService.update_account(engine, used_account, used_account.balance + amount)

    @staticmethod
    def find_the_best_account_for_transaction(engine, logged_in_user: namedtuple, card) -> tuple:
        """If it is possible, use an account with the same currency in which you want to make transactions.
        If you do not have such an account, or you have insufficient funds on this account,
        use another account that has the appropriate funds.
        If no account is found that meets these requirements, return None"""
        entered_amount = Decimal(get_answer(
            validation_decimal,
            'Enter the amount: ',
            'Entered data contains illegal characters. Try again: '))
        currency = CardManagementService.choose_currency('Choose the currency you want to pay in: ')
        accounts = CrudRepo(engine, UserAccountTable).find_all_with_condition(
            (UserAccountTable.id_user_data, logged_in_user.id))
        accounts = [user_account_named_tuple(item) for item in accounts]
        account_number = [x for x in accounts if x.currency == currency and x.balance > entered_amount]
        account_number = accounts.index(account_number[0]) if account_number else None
        account_with_main_currency = accounts[account_number] if account_number != None else None
        used_account = None
        amount_exched = None
        rate = 1
        if account_number:
            del accounts[account_number]
        if account_with_main_currency:
            used_account = account_with_main_currency
        elif accounts:
            for x in accounts:
                response = CurrencyExchange().get_result(currency, x.currency, str(entered_amount))
                amount_exched = Decimal(response["result"])
                rate = Decimal(response['info']['rate'])
                if amount_exched < x.balance:
                    used_account = x
                    break
            else:
                print(f"\n{' ' * 12}You do not have sufficient funds in your account. "
                      f"Deposit money into your account.")
        else:
            print(f"\n{' ' * 12}You do not have sufficient funds in your account. "
                  f"Deposit money into your account.")
        if card.main_currency != currency:
            exchanged_amount_for_limit_checking = CurrencyExchange().get_result(
                currency, card.main_currency, str(entered_amount))
        else:
            exchanged_amount_for_limit_checking = {"result": entered_amount, "info": {"rate": 1}}
        return used_account, entered_amount, amount_exched, rate, currency, exchanged_amount_for_limit_checking

    @staticmethod
    def check_daily_limit(engine, used_account: namedtuple, card: namedtuple, exchanged_amount: dict) -> bool:
        """Check if the limit of daily transactions for a given card has not been exceeded"""
        today_date = date.today()
        transactions_one_day = UserAccountRepo(engine, CardTransactionTable).find_btwn_dates(
            (
                CardTransactionTable.transaction_time,
                today_date,
                date(today_date.year, today_date.month, today_date.day + 1),
                CardTransactionTable.id_user_account,
                used_account.id
            )
        )
        transactions_one_day = [card_transaction_named_tuple(x) for x in transactions_one_day]
        sum_transactions_one_day = 0
        for x in transactions_one_day:
            sum_transactions_one_day += (x.amount * x.rate_to_main_currency if x.payout == "YES" else 0)
        if sum_transactions_one_day + Decimal(exchanged_amount["result"]) >= card.daily_limit:
            return False
        else:
            return True

    @staticmethod
    def check_security(type_of_payment: str, card: namedtuple) -> bool:
        """Check if the card has a blocked transaction you want to make"""
        if type_of_payment == 'Contactless payment':
            if card.card_type == "STANDARD":
                if card.sec_contactless:
                    return True
                else:
                    print(
                        f"\n{' ' * 12}You cannot pay with your card "
                        f"because contactless transactions have been blocked.")
            else:
                print(f"\n{' ' * 12}You cannot pay with a virtual card contactless. Change card.")
                return False
        elif type_of_payment == 'Magnetic stripe payment':
            if card.card_type == "STANDARD":
                if card.sec_magnetic_strip:
                    return True
                else:
                    print(
                        f"\n{' ' * 12}You cannot pay with your card "
                        f"because magnetic stripe payments have been blocked.")
                    return False
            else:
                print(f"\n{' ' * 12}You cannot pay with a virtual card by magnetic stripe. Change card.")
        elif type_of_payment == 'Internet payment':
            if card.sec_online_transactions:
                return True
            else:
                print(f"\n{' ' * 12}You cannot pay with your card because online payments have been blocked.")
                return False
        elif type_of_payment == 'Withdrawals ATM':
            if card.card_type == "STANDARD":
                if card.sec_withdrawals_atm:
                    return True
                else:
                    print(f"\n{' ' * 12}You cannot withdraw money from an ATM because your withdrawals are blocked.")
                    return False
            else:
                print(f"\n{' ' * 12}You cannot withdraw money from a virtual card. Change card.")

    @staticmethod
    def update_account(engine, used_account: namedtuple, amount: Decimal):
        CrudRepo(engine, UserAccountTable).update_by_id(
            used_account.id,
            account_number=used_account.account_number,
            currency=used_account.currency,
            balance=amount)

    @staticmethod
    def add_card_transaction(
            engine, used_account: namedtuple, used_card: namedtuple, amount: Decimal,
            commission: int, balance: Decimal, payout: str, payment: str,
            rate_to_main_currency: int, transaction_type: str, rate: Decimal, payer_acc: str | None):
        CrudRepo(engine, CardTransactionTable).add(
            id_user_account=used_account.id,
            id_card=used_card.id,
            transaction_time=datetime.now(),
            amount=amount,
            commission=commission,
            balance=balance,
            payer_name=get_answer(
                validation_space_or_alpha_not_digit,
                'Enter the payer name: ',
                'Entered data contains illegal characters. Try again: '),
            payout=payout,
            payment=payment,
            rate_to_main_currency=Decimal(rate_to_main_currency),
            transaction_type=transaction_type,
            rate=rate,
            payer_account_number=payer_acc
        )
        print(f"\n{' ' * 12}The transaction was successful.")

    @staticmethod
    def choose_payment_type() -> str:
        """Select the type of card you want to get"""
        print("""
            Choose the type of payment: 
            1. Contactless payment
            2. Magnetic stripe payment
            3. Internet payment
            """)
        chosen_operation = get_answer(
            validation_chosen_operation,
            'Enter the selected type of payment: ',
            'Entered data contains illegal characters. Try again: ',
            (1, 3))
        match chosen_operation:
            case '1':
                return 'Contactless payment'
            case '2':
                return 'Magnetic stripe payment'
            case '3':
                return 'Internet payment'
