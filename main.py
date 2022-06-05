from management.bussines_logic import BussinesLogic


if __name__ == '__main__':
    # try:
        currency_exchange_app = BussinesLogic()
        while True:
            currency_exchange_app.cycle()
    # except Exception as e:
    #     print(e.args[0])
