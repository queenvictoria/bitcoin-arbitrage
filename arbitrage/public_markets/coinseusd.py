"""
@author: Jason Chan <bearish_trader@yahoo.com>

BTC:  1ZAWfGTTyv1HuqJemnDsdQChCpiAAaZYZ
QRK:  QQcy1tMSdK8afj1gckxKJs86izP7emEitP
DOGE: DEdHx4GSjawoiSjbjWwr4BKH9Njx235CeH
MAX:  mf93aDHYqk5MxfAFvMXk8Cn1fQW6S37GYQ
MTC:  miCSJ57pae6XWi3knkmSUZXfHHg3bEEpLe
PRT:  PYdxGCTSc2tGvRbpQjwZpnktbzRqvU4DYR
DTC:  DRTJnJ9CW4WUqhPecfhRahC3SoCgXbQcN4
"""
import urllib.request
import urllib.error
import urllib.parse
import json
import logging
from .market import Market

class CoinsEUSD(Market):
    def __init__(self):
        super(CoinsEUSD, self).__init__("USD")
        self.update_rate = 20
        self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
            {'price': 0, 'amount': 0}]}

    def update_depth(self):
        res = urllib.request.urlopen(
            'https://www.coins-e.com/api/v2/market/' + self.pair + '/depth/')
        jsonstr = res.read().decode('utf8')
        try:
            data = json.loads(jsonstr)
        except Exception:
            logging.error("%s - Can't parse json: %s" % (self.name, jsonstr))
        if data["message"] == "success":
            self.depth = self.format_depth(data["marketdepth"])
        else:
            logging.error("%s - fetched data error" % (self.name))

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x["r"]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[
                     "r"]), 'amount': float(i["q"])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        while asks[0]["price"] < bids[0]["price"]: # Coins-e occassionally has data anomaly with asks lower than bids
            asks.pop(0)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = CoinsEUSD()
    print(market.get_depth())
