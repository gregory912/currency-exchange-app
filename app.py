from management.user_operations import UserOperations


if __name__ == '__main__':
    try:
        currency_exchange_app = UserOperations()
        while True:
            currency_exchange_app.cycle()
    except Exception as e:
        print(e.args[0])
