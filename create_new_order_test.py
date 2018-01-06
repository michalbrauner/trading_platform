from oanda.order_api_client import OrderApiClient
import os

try:
    import Queue as queue
except ImportError:
    import queue


def main():
    account_id = os.environ.get('OANDA_API_ACCOUNT_ID')
    access_token = os.environ.get('OANDA_API_ACCESS_TOKEN')

    order_api_client = OrderApiClient(account_id, access_token)
    response = order_api_client.create_new_order(1000, 'EUR_USD')

    print(response)


if __name__ == '__main__':
    main()
