from __future__ import print_function
from oanda.stream import Stream
import os
import sys


def main():
    account_id = os.environ.get('OANDA_API_ACCOUNT_ID')
    access_token = os.environ.get('OANDA_API_ACCESS_TOKEN')

    stream = Stream(account_id, access_token, ['EUR_USD'])
    stream.connect_to_stream()

    for price in stream.get_price():
        print('{}'.format(price), end='\r')
        sys.stdout.flush()

    print('')
    sys.stdout.flush()



if __name__ == '__main__':
    main()
