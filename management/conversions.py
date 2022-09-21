from collections import namedtuple


def user_data_named_tuple(items):
    UserData = namedtuple("UserData",
                          "id name surname country address email phone login password creation_date main_currency")
    return UserData(*items)


def user_account_named_tuple(items):
    UserAccount = namedtuple("UserAccount", "id id_user_data account_number currency balance")
    return UserAccount(*items)


def dates_named_tuple(items):
    Dates = namedtuple("Dates", "start_date end_date")
    return Dates(*items)


def used_card_named_tuple(items):
    UsedCard = namedtuple("UsedCard", "id card_number valid_thru card_name card_type main_currency")
    return UsedCard(*items)


def card_named_tuple(items):
    Card = namedtuple(
        "Card",
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
        "card_name "
        "card_type "
        "main_currency")
    return Card(*items)


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
        "transaction_time "
        "amount_in_main_user_currency "
        "commission_in_main_user_currency")
    return ExchangeCurrency(*items)


def card_transaction_named_tuple(items):
    CardTransaction = namedtuple(
        "CardTransaction",
        "id "
        "id_user_account "
        "transaction_time "
        "amount "
        "commission_in_main_user_currency "
        "balance "
        "payer_name "
        "id_card "
        "payout "
        "payment "
        "rate_to_main_card_currency "
        "transaction_type "
        "rate_tu_used_account "
        "payer_account_number "
        "amount_in_main_user_currency")
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


def transactions_for_statement_named_tuple(items):
    TransactionsToStatement = namedtuple(
        "TransactionsToStatement",
        "date "
        "customer "
        "acc_number "
        "card_nb "
        "payout "
        "payment "
        "rate "
        "saldo "
        "commission")
    return TransactionsToStatement(*items)


