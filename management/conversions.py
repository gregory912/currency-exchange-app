from collections import namedtuple


def user_data_named_tuple(item: tuple) -> namedtuple:
    UserData = namedtuple("UserData",
                          "id name surname country address email phone login password creation_date main_currency")
    return UserData(*item)


def user_account_named_tuple(item: tuple) -> namedtuple:
    UserAccount = namedtuple("UserAccount", "id id_user_data account_number currency balance")
    return UserAccount(*item)


def dates_named_tuple(items: tuple) -> namedtuple:
    Dates = namedtuple("Dates", "start_date end_date")
    return Dates(*items)


def used_card_named_tuple(item: tuple) -> namedtuple:
    UsedCard = namedtuple("UsedCard", "id card_number valid_thru card_name card_type main_currency")
    return UsedCard(*item)


def card_named_tuple(item: tuple) -> namedtuple:
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
    return Card(*item)


def currency_exchange_named_tuple(item: tuple) -> namedtuple:
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
    return ExchangeCurrency(*item)


def card_transaction_named_tuple(item: tuple) -> namedtuple:
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
    return CardTransaction(*item)


def transaction_named_tuple(item: tuple) -> namedtuple:
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
    return Transaction(*item)


def transactions_for_statement_named_tuple(item: tuple) -> namedtuple:
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
    return TransactionsToStatement(*item)
