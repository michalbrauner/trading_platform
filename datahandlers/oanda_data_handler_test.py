from datahandlers.oanda_data_handler import OandaDataHandler
import os

try:
    import Queue as queue
except ImportError:
    import queue


def main():
    account_id = os.environ.get('OANDA_API_ACCOUNT_ID')
    access_token = os.environ.get('OANDA_API_ACCESS_TOKEN')

    events = queue.Queue()

    data_handler = OandaDataHandler(events, ['EUR_USD'], account_id, access_token)

    while True:
        data_handler.update_bars()
        price = data_handler.get_latest_bar('EUR_USD')
        print(price)




if __name__ == '__main__':
    main()
