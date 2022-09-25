from database.model.tables import CurrencyExchangeTable, CardTransactionTable, TransactionTable, UserAccountTable
from database.model.tables import CardTable
from database.repository.crud_repo import CrudRepo
from database.repository.user_account_repo import UserAccountRepo
from management.conversions import *
from abc import ABC, abstractmethod


class TransactionService:
    def __init__(self, engine):
        self.engine = engine

        self.sort_transaction = SortTransactions(self.engine)
        self.filter_transaction = FilterTransactions(self.engine)

    def last_transactions(self, used_account: namedtuple, logged_in_user: namedtuple):
        """Get and print last 5 transactions """
        sorted_transactions = self.sort_transaction.sort_transactions_by_transaction_time(
            self.sort_transaction.get_all_transactions(used_account))
        filtered_transactions = self.filter_transaction.filter_transactions(sorted_transactions, used_account)
        self._print_transactions(
            filtered_transactions[:len(sorted_transactions) if len(sorted_transactions) < 5 else 5], logged_in_user)

    def transactions_between_dates(self, used_account: namedtuple, dates: namedtuple) -> list[namedtuple]:
        """Return all transactions for the account according to the dates indicated"""
        sorted_transactions = self.sort_transaction.sort_transactions_by_transaction_time(
            self.sort_transaction.get_all_transactions_btwn_dates(used_account, dates))
        return self.filter_transaction.filter_transactions(sorted_transactions, used_account)

    @staticmethod
    def _print_transactions(transactions: list[namedtuple], logged_in_user: namedtuple) -> None:
        """Print transactions based on Transaction namedtuple"""

        def space(text: str, elements: int) -> str:
            return ' ' * (elements - len(text)) if text else ' ' * elements

        for x in transactions:
            print(
                f"Data: {x.date} Customer: {x.customer}{space(x.customer, 16)} "
                f"Acc number: {x.acc_number}{space(x.acc_number, 22)} "
                f"Card nb: {x.card_nb}{space(x.card_nb, 18)} "
                f"Payout: {x.payout}{space(str(x.payout), 7)} "
                f"Payment: {x.payment}{space(str(x.payment), 7)} "
                f"Rate: {x.rate}{space(str(x.rate), 4)} "
                f"Saldo: {x.saldo}{space(str(x.saldo), 7)} "
                f"Fee in {logged_in_user.main_currency}: {x.commission}")


class SortTransactions:
    def __init__(self, engine):
        self.engine = engine

        self.currency_exch_crud_repo = UserAccountRepo(self.engine, CurrencyExchangeTable)
        self.transaction_crud_repo = UserAccountRepo(self.engine, TransactionTable)
        self.card_transaction_crud_repo = UserAccountRepo(self.engine, CardTransactionTable)

    def get_all_transactions(self, used_account: namedtuple) -> tuple:
        """The function returns all transactions for a given account"""
        cur_exch_out = self._get_transactions(
            self.currency_exch_crud_repo, used_account, CurrencyExchangeTable.id_user_account_out)
        cur_exch_in = self._get_transactions(
            self.currency_exch_crud_repo, used_account, CurrencyExchangeTable.id_user_account_in)

        transactions = self._get_transactions(
            self.transaction_crud_repo, used_account, TransactionTable.id_user_account)
        card_transactions = self._get_transactions(
            self.card_transaction_crud_repo, used_account, CardTransactionTable.id_user_account)

        return cur_exch_out, cur_exch_in, transactions, card_transactions

    @staticmethod
    def _get_transactions(repo, used_account: namedtuple, parameter) -> list[tuple]:
        """Receive all transactions from the indicated table"""
        return repo.find_all_with_condition((parameter, used_account.id))

    def get_all_transactions_btwn_dates(self, used_account: namedtuple, dates: namedtuple) -> tuple:
        """The function returns all transactions for a given account and dates"""

        cur_exch_out = self._get_transactions_btwn_dates(
            self.currency_exch_crud_repo, CurrencyExchangeTable.transaction_time, dates, used_account,
            CurrencyExchangeTable.id_user_account_out)
        cur_exch_in = self._get_transactions_btwn_dates(
            self.currency_exch_crud_repo, CurrencyExchangeTable.transaction_time, dates, used_account,
            CurrencyExchangeTable.id_user_account_in)

        transactions = self._get_transactions_btwn_dates(
            self.transaction_crud_repo, TransactionTable.transaction_time, dates, used_account,
            TransactionTable.id_user_account)
        card_transactions = self._get_transactions_btwn_dates(
            self.card_transaction_crud_repo, CardTransactionTable.transaction_time, dates, used_account,
            CardTransactionTable.id_user_account)

        return cur_exch_out, cur_exch_in, transactions, card_transactions

    @staticmethod
    def _get_transactions_btwn_dates(repo, transaction_time, dates: namedtuple, used_account: namedtuple, parameter):
        """Get the transactions for the indicated dates from the table"""
        return repo.find_btwn_dates(
            (transaction_time, dates.start_date, dates.end_date, parameter, used_account.id))

    def sort_transactions_by_transaction_time(self, elements: tuple) -> list[namedtuple]:
        """The function sorts the transactions by date"""
        return sorted(self._merge_all_transactions(elements), key=lambda x: x.transaction_time, reverse=True)

    @staticmethod
    def _merge_all_transactions(elements: tuple) -> list:
        """Combine all downloaded transactions into one list"""
        cur_exch_out = [currency_exchange_named_tuple(item) for item in elements[0]]
        cur_exch_in = [currency_exchange_named_tuple(item) for item in elements[1]]
        transactions = [transaction_named_tuple(item) for item in elements[2]]
        card_transactions = [card_transaction_named_tuple(item) for item in elements[3]]
        return cur_exch_out + cur_exch_in + transactions + card_transactions


class FilterTransactions:
    def __init__(self, engine):
        self.engine = engine

        self.user_account_crud_repo = CrudRepo(self.engine, UserAccountTable)
        self.card_crud_repo = CrudRepo(self.engine, CardTable)

    def filter_transactions(self, transactions: list[namedtuple], used_account: namedtuple) -> list[namedtuple]:
        """Filter the results you get from different namedtuple to one general type"""
        filtred_transactions = []
        for transaction in transactions:

            if type(transaction).__name__ == 'ExchangeCurrency':

                if used_account.id == transaction.id_user_account_out:
                    filtred_transactions.append(FilterItemsExchangeCurrencyOut().get_named_tuple(
                        transaction, self._get_currency_from_which_money_was_exchanged(transaction)))
                else:
                    filtred_transactions.append(FilterItemsExchangeCurrencyIn().get_named_tuple(
                        transaction, used_account.currency))

            elif type(transaction).__name__ == 'Transaction':
                if transaction.payment == 'YES':
                    filtred_transactions.append(FilterItemsTransactionPayment().get_named_tuple(transaction))
                else:
                    filtred_transactions.append(FilterItemsTransactionPayout().get_named_tuple(transaction))

            elif type(transaction).__name__ == 'CardTransaction':
                card_number = self._get_card_number_from_card_transaction(transaction)
                if transaction.payout == 'YES':
                    filtred_transactions.append(FilterItemsCardTransactionPayout().get_named_tuple(
                        transaction, card_number[2] if card_number else "NOT EXIST"))
                else:
                    filtred_transactions.append(FilterItemsCardTransactionPayment().get_named_tuple(
                        transaction, card_number[2] if card_number else "NOT EXIST"))

        return filtred_transactions

    def _get_card_number_from_card_transaction(self, transaction):
        """Get the card number from which the transation was made"""
        return self.card_crud_repo.find_by_id(transaction.id_card)

    def _get_currency_from_which_money_was_exchanged(self, transaction):
        """Method returns information on the currency from which the user exchanged money to another currency"""
        return self.user_account_crud_repo.find_by_id(transaction.id_user_account_in)[3]


class FilterItems(ABC):
    @abstractmethod
    def get_named_tuple(self, transaction, parameter=''):
        pass


class FilterItemsExchangeCurrencyOut(FilterItems):
    def get_named_tuple(self, t, parameter=''):
        return transactions_for_statement_named_tuple((
            t.transaction_time, f"Exchanged to {parameter}", "", "", t.transfer_amount_out,
            "", t.exchange_rate_out, t.balance_out, t.commission_in_main_user_currency))


class FilterItemsExchangeCurrencyIn(FilterItems):
    def get_named_tuple(self, t, parameter=''):
        return transactions_for_statement_named_tuple((
            t.transaction_time, f"Exchanged to {parameter}", "", "", "", t.transfer_amount_in,
            t.exchange_rate_in, t.balance_in, t.commission_in_main_user_currency))


class FilterItemsTransactionPayment(FilterItems):
    def get_named_tuple(self, t, parameter=''):
        return transactions_for_statement_named_tuple((
            t.transaction_time, f"From {t.payer_name}", t.payer_account_number,
            "", "", t.amount, "", t.balance, ""))


class FilterItemsTransactionPayout(FilterItems):
    def get_named_tuple(self, t, parameter=''):
        return transactions_for_statement_named_tuple((
            t.transaction_time, f"To {t.payer_name}", t.payer_account_number,
            "", t.amount, "", "", t.balance, ""))


class FilterItemsCardTransactionPayment(FilterItems):
    def get_named_tuple(self, t, parameter=''):
        return transactions_for_statement_named_tuple((
            t.transaction_time, t.payer_name, t.payer_account_number, parameter, "", t.amount,
            t.rate_tu_used_account, t.balance, t.commission_in_main_user_currency))


class FilterItemsCardTransactionPayout(FilterItems):
    def get_named_tuple(self, t, parameter=''):
        return transactions_for_statement_named_tuple((
            t.transaction_time, t.payer_name, "", parameter, t.amount, "",
            t.rate_tu_used_account, t.balance, t.commission_in_main_user_currency))
