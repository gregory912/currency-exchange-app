from database.repository.crud_repo import CrudRepo
from database.repository.user_account_repo import UserAccountRepo
from database.repository.card_repo import CardRepo
from database.model.tables import *
from management.services.currency_exchange_service import CurrencyExchange
from management.services.card_management_service import CardManagementService
from management.services.common import *
from management.conversions import *
from datetime import date, timedelta
from decimal import Decimal


class CardTransactionsService:
    def __init__(self, engine):
        self.engine = engine

        self.user_account_crud_repo = CrudRepo(self.engine, UserAccountTable)
        self.user_data_crud_repo = CrudRepo(self.engine, UserDataTable)
        self.card_crud_repo = CardRepo(self.engine, CardTable)
        self.service_crud_repo = CrudRepo(self.engine, ServiceTable)

    def pay_by_card(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Perform card payments taking into account all currency conversions and the correct calculation of the
        account balance after the operation."""
        card = card_named_tuple(self.card_crud_repo.find_by_id(used_card.id))
        if not card.blocked or card.card_type == "SINGLE-USE VIRTUAL":
            type_of_payment = choose_payment_type()
            if self._check_security(type_of_payment, card):
                used_account, ented_amt, amt_exched, rate, currency, amt_for_limit_checking, commission, amount \
                    = self._find_the_best_account_for_transaction(logged_in_user, card)
                if not used_account:
                    return False
                if self._check_daily_limit(used_account, card, amt_for_limit_checking):
                    if type_of_payment == "Contactless payment":
                        if amt_for_limit_checking["result"] < card.contactless_limit:
                            self.add_card_transaction(
                                used_account, used_card, (amt_exched if amt_exched else ented_amt),
                                0, used_account.balance - (amt_exched if amt_exched else ented_amt),
                                "YES", "NO", amt_for_limit_checking["info"]["rate"],
                                "Contactless payment", rate, None, amount)
                            self.update_account(
                                used_account,
                                (used_account.balance - amt_exched if amt_exched else used_account.balance - ented_amt))
                        else:
                            print(f"\n{' ' * 12}Your contactless transaction limit does not allow you to "
                                  f"complete the transaction. Change your limit..")
                    elif type_of_payment == "Internet payment":
                        if (card.card_type == "STANDARD" and amt_for_limit_checking["result"] < card.internet_limit)\
                                or card.card_type != "STANDARD":
                            self.add_card_transaction(
                                used_account, used_card, (amt_exched if amt_exched else ented_amt),
                                0, used_account.balance - (amt_exched if amt_exched else ented_amt),
                                "YES", "NO", amt_for_limit_checking["info"]["rate"],
                                "Internet payment", rate, None, amount)
                            self.update_account(
                                used_account,
                                (used_account.balance - amt_exched if amt_exched else used_account.balance - ented_amt))
                            if card.card_type == "SINGLE-USE VIRTUAL":
                                CardManagementService.delete_card(self.engine, used_card, logged_in_user)
                        else:
                            print(f"\n{' ' * 12}Your internet transaction limits do not allow you to "
                                  f"complete the transaction. Change your limit.")
                    elif type_of_payment == "Magnetic stripe payment":
                        self.add_card_transaction(
                            used_account, used_card, (amt_exched if amt_exched else ented_amt),
                            commission, used_account.balance - (amt_exched if amt_exched else ented_amt),
                            "YES", "NO", amt_for_limit_checking["info"]["rate"],
                            "Magnetic stripe payment", rate, None, amount)
                        self.update_account(
                            used_account,
                            (used_account.balance - amt_exched if amt_exched else used_account.balance - ented_amt))
                else:
                    print(
                        f"\n{' ' * 12}We are unable to complete your transaction because the daily limit has "
                        f"been exceeded. Change your daily limit to be able to make transactions.")
        else:
            print(f"\n{' ' * 12}Your card is blocked. We cannot complete your transaction.")

    def withdraw_money(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Perform card payment operations. Check that the card is not blocked and that
        it has sufficient funds. If possible, select the account with the currency you want to select from the ATM."""
        card = card_named_tuple(self.card_crud_repo.find_by_id(used_card.id))
        if not card.blocked:
            if self._check_security('Withdrawals ATM', card):
                used_account, entred_amt, amt_exched, rate, currency, amt_for_limit_checking, commission, amount \
                    = self._find_the_best_account_for_transaction(logged_in_user, card, True)
                if not used_account:
                    return False
                if self._check_daily_limit(used_account, card, amt_for_limit_checking):
                    if commission:
                        print(
                            f"\n{' ' * 12}You've exceeded the monthly exchange limit of 200 {used_card.main_currency}."
                            f"A commission of 2% of the entered amount has been charged.")
                    self.add_card_transaction(
                        used_account, used_card, (amt_exched if amt_exched else entred_amt),
                        commission, used_account.balance - (amt_exched if amt_exched else entred_amt),
                        "YES", "NO", amt_for_limit_checking["info"]["rate"],
                        "Withdrawals ATM", rate, None, amount)
                    self.update_account(
                        used_account,
                        (used_account.balance - amt_exched if amt_exched else used_account.balance - entred_amt))
        else:
            print(f"\n{' ' * 12}Your card is blocked. We cannot complete your transaction.")

    def deposit_money(self, used_card: namedtuple, logged_in_user: namedtuple):
        """Deposit money by card. Make a deposit to the appropriate account, if necessary, convert the amount."""
        amount = Decimal(get_answer(
            validation_decimal,
            'Enter the amount: ',
            'Entered data contains illegal characters. Try again: '))
        currency = choose_currency('Choose the currency in which you want to deposit money: ')
        accounts = self.user_account_crud_repo.find_all_with_condition(
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
        self.add_card_transaction(
            used_account, used_card, amount, 0, used_account.balance + amount,
            "NO", "YES", 0, "Deposit money", rate, payer_acc_number, Decimal(0))
        self.update_account(used_account, used_account.balance + amount)

    def _find_the_best_account_for_transaction(
            self, logged_in_user: namedtuple, card: namedtuple, commission: bool = False) -> tuple:
        """If it is possible, use an account with the same currency in which you want to make transactions.
        If you do not have such an account, or you have insufficient funds on this account,
        use another account that has the appropriate funds.
        If no account is found that meets these requirements, return None"""

        def find_account_with_same_currency_as_transaction():
            """Find an account with the same currency as the transaction.
            Once found, remove the account from the list and return it"""
            acc_nb_in_same_cur = [i for i in accounts if i.currency == currency and i.balance > entered_amount]
            acc_nb_in_same_cur_indx = accounts.index(acc_nb_in_same_cur[0]) if acc_nb_in_same_cur else None
            return accounts.pop(acc_nb_in_same_cur_indx) if acc_nb_in_same_cur_indx is not None else None

        entered_amount = Decimal(get_answer(
            validation_decimal,
            'Enter the amount: ',
            'Entered data contains illegal characters. Try again: '))
        currency = choose_currency('Choose the currency you want to pay in: ')
        if commission:
            entered_amount, amount, commission = self._check_and_get_commission(
                logged_in_user, currency, entered_amount)
        else:
            amount, commission = None, None
        accounts = self.user_account_crud_repo.find_all_with_condition(
            (UserAccountTable.id_user_data, logged_in_user.id))
        accounts = [user_account_named_tuple(item) for item in accounts]
        account_with_main_currency = find_account_with_same_currency_as_transaction()
        used_account, amount_exched, rate = None, None, 1
        if account_with_main_currency:
            used_account = account_with_main_currency
        elif accounts:
            for item in accounts:
                response = CurrencyExchange().get_result(currency, item.currency, str(entered_amount))
                amount_exched = Decimal(response["result"])
                rate = Decimal(response['info']['rate'])
                if amount_exched < item.balance:
                    used_account = item
                    break
            else:
                print(f"\n{' ' * 12}You do not have sufficient funds in your account. "
                      f"Deposit money into your account.")
        else:
            print(f"\n{' ' * 12}You do not have sufficient funds in your account. "
                  f"Deposit money into your account.")
        if card.main_currency != currency:
            amt_for_limit_checking = CurrencyExchange().get_result(
                currency, card.main_currency, str(entered_amount))
        else:
            amt_for_limit_checking = {"result": entered_amount, "info": {"rate": 1}}
        return used_account, entered_amount, amount_exched, rate, currency, amt_for_limit_checking, commission, amount

    def _check_and_get_commission(self, logged_in_user, currency_for_transaction, entered_amount) -> tuple:
        """The entered amount in a given currency is converted to the main currency
        (if a currency other than the main currency of the account has been entered) for the account to check
        if any transactions should be collected. The transaction is charged in
        case of exceeding 200 (assumed for all 4 currencies) or exceeding 5 monthly transactions.
        The function returns the amount in the same currency as was entered,
        but after deducting the commission if it was required."""
        def convert_entered_amount() -> Decimal:
            """Convert currency if it is different from user's main currency"""
            if logged_in_user.main_currency != currency_for_transaction:
                exchanged_data = CurrencyExchange().get_result(
                    currency_for_transaction, logged_in_user.main_currency, str(entered_amount))
                return Decimal(exchanged_data["result"])
            else:
                return entered_amount

        def check_commisions_based_on_monthly_transactions(amount: Decimal) -> tuple:
            """Check if a commission is required.
            The amount and commission are stated in the user's primary currency."""
            all_exchanges = self.card_crud_repo.get_monthly_card_trans_for_user(
                logged_in_user.id, fst_day_of_this_month(), fst_day_of_next_month())
            transaction_sum = [(item[0] if item[0] else 0) for item in all_exchanges]
            if sum(transaction_sum) + amount > 200 or len(transaction_sum) > 5:
                return amount + (amount * Decimal(0.02)), amount * Decimal(0.02)
            return amount, 0

        converted_amount = convert_entered_amount()
        amount_after_checking, commission_after_checking = check_commisions_based_on_monthly_transactions(
            converted_amount)
        result = CurrencyExchange().get_result(
            logged_in_user.main_currency, currency_for_transaction, str(amount_after_checking))
        return Decimal(result["result"]), amount_after_checking, commission_after_checking

    def _check_daily_limit(self, used_account: namedtuple, card: namedtuple, exchanged_amount: dict) -> bool:
        """Check if the limit of daily transactions for a given card has not been exceeded"""
        today_date = date.today()
        transactions_one_day = UserAccountRepo(self.engine, CardTransactionTable).find_btwn_dates(
            (
                CardTransactionTable.transaction_time,
                today_date,
                date.today() + timedelta(days=1),
                CardTransactionTable.id_user_account,
                used_account.id
            )
        )
        transactions_one_day = [card_transaction_named_tuple(x) for x in transactions_one_day]
        sum_transactions_one_day = 0
        for x in transactions_one_day:
            sum_transactions_one_day += (x.amount * x.rate_to_main_card_currency if x.payout == "YES" else 0)
        if sum_transactions_one_day + Decimal(exchanged_amount["result"]) >= card.daily_limit:
            return False
        else:
            return True

    def update_account(self, used_account: namedtuple, amount: Decimal):
        self.user_account_crud_repo.update_by_id(
            used_account.id,
            account_number=used_account.account_number,
            currency=used_account.currency,
            balance=amount)

    def add_card_transaction(
            self, used_account: namedtuple, used_card: namedtuple, amount: Decimal,
            commission: int, balance: Decimal, payout: str, payment: str,
            rate_to_main_currency: int, transaction_type: str, rate: Decimal, payer_acc: str | None,
            amount_in_main_user_currency: Decimal):
        CrudRepo(self.engine, CardTransactionTable).add(
            id_user_account=used_account.id,
            id_card=used_card.id,
            transaction_time=datetime.now(),
            amount=amount,
            commission_in_main_user_currency=commission,
            balance=balance,
            payer_name=get_answer(
                validation_space_or_alpha_not_digit,
                'Enter the payer name: ',
                'Entered data contains illegal characters. Try again: '),
            payout=payout,
            payment=payment,
            rate_to_main_card_currency=Decimal(rate_to_main_currency),
            transaction_type=transaction_type,
            rate_tu_used_account=rate,
            payer_account_number=payer_acc,
            amount_in_main_user_currency=amount_in_main_user_currency
        )
        print(f"\n{' ' * 12}The transaction was successful.")

    @staticmethod
    def _check_security(type_of_payment: str, card: namedtuple) -> bool:
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
