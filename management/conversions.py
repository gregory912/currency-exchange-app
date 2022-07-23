from collections import namedtuple


def user_data_named_tuple(items):
    UserData = namedtuple("UserData", "id name surname country address email phone login password creation_date")
    return UserData(*items)


def user_account_named_tuple(items):
    UserAccount = namedtuple("UserAccount", "id id_user_data account_number currency balance")
    return UserAccount(*items)


def dates_named_tuple(items):
    Dates = namedtuple("Dates", "start_date end_date ")
    return Dates(*items)


def card_named_tuple(items):
    Card = namedtuple("Card", "id card_number valid_thru card_name card_type")
    return Card(*items)


def card_all_named_tuple(items):
    CardAll = namedtuple(
        "CardAll",
        "id "
        "id_user_data "
        "card_number "
        "valid_thru "
        "cvv blocked "
        "daily_limit "
        "internet_limit "
        "contactless_limit "
        "card_pin "
        "sec_online_transactions "
        "sec_location "
        "sec_magnetic_strip "
        "sec_withdrawals_atm "
        "sec_contactless "
        "card_name card_type main_currency")
    return CardAll(*items)


def currency_exchange_named_tuple(items):
    ExchangeCurrency = namedtuple(
        "ExchangeCurrency",
        "id "
        "id_user_account_out "
        "transfer_amount_out "
        "exchange_rate_out "
        "balance_out "
        "id_user_account_in "
        "transfer_amount_in "
        "exchange_rate_in "
        "balance_in "
        "transaction_time")
    return ExchangeCurrency(*items)


def card_transaction_named_tuple(items):
    CardTransaction = namedtuple(
        "CardTransaction",
        "id "
        "id_user_account "
        "transaction_time "
        "amount "
        "commission "
        "balance "
        "payer_name "
        "id_card "
        "payout "
        "payment "
        "rate_to_main_currency "
        "transaction_type "
        "rate")
    return CardTransaction(*items)


def transaction_named_tuple(items):
    Transaction = namedtuple(
        "Transaction",
        "id "
        "id_user_account "
        "payment "
        "payout "
        "transfer_title "
        "transaction_time "
        "amount "
        "balance "
        "payer_name "
        "payer_account_number")
    return Transaction(*items)


def all_transactions_named_tuple(items):
    AllTransactions = namedtuple(
        "AllTransactions",
        "date "
        "customer "
        "acc_number "
        "card_nb "
        "payout "
        "payment "
        "rate "
        "saldo "
        "commission")
    return AllTransactions(*items)


def card_transactions_named_tuple(items):
    CardTransactions = namedtuple(
        "CardTransaction",
        "id "
        "id_user_account "
        "transaction_time "
        "amount commission "
        "balance "
        "payer_name "
        "id_card "
        "payout "
        "payment "
        "rate_to_main_currency "
        "transaction_type "
        "rate"
    )
    return CardTransactions(*items)

