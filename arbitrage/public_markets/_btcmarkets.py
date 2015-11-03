import urllib.request
import urllib.error
import urllib.parse
import json
import sys
from .market import Market


# https://github.com/BTCMarkets/API/wiki/Market-data-API
# v3 API is current
class BTCMarkets(Market):
    def __init__(self, currency, instrument):
        super().__init__(currency)
        self.instrument = instrument # BTC, LTC
        self.update_rate = 20

    def update_depth(self):
        url = "https://api.btcmarkets.net/market/%s/%s/orderbook" % (
            self.instrument, self.currency
        )

        req = urllib.request.Request(url, None, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})

        try:
            res = urllib.request.urlopen(req)
        except HTTPError as error:
            sys.stderr.write("HTTPError: Can't open %s.\n" % url)

        try:
            depth = json.loads(res.read().decode('utf8'))
            self.depth = self.format_depth(depth)
        except:
            sys.stderr.write("Can't format depth.\n")

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[0]), 'amount': float(i[1])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(
            depth['bids'], True)
        asks = self.sort_and_format(
            depth['asks'], False)
        return {'asks': asks, 'bids': bids}
