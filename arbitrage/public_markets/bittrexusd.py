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
from .market import Market, GetDepthException

class BittrexUSD(Market):   
    
    def __init__(self):
        super(BittrexUSD, self).__init__("USD")
        self.update_rate = 20
        self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
            {'price': 0, 'amount': 0}]}
                    
    def update_depth(self):
        params = {"market": self.pair2_name+"-"+self.pair1_name, "type": "both", "depth" : 20}
        # Fore bittrex API everything is a GET, no POST methods accepted/allowed
        res = urllib.request.urlopen(
            'https://bittrex.com/api/v1/public/getorderbook?'+urllib.parse.urlencode(params))
        jsonstr = res.read().decode('utf8')
        try:
            data = json.loads(jsonstr)
        except Exception:
            logging.error("%s - Can't parse json: %s" % (self.name, jsonstr))
        try:
            if bool(data["success"]) == True:
                pair_data = data["result"]
                self.depth = self.format_depth(pair_data)
                return
        except Exception:
            logging.error("%s - response received but error: %s" % (self.name, data))

        logging.error("%s - fetched data error" % (self.name))
        raise GetDepthException("update_depth failed json=" + json.dumps(data))

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x["Rate"]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i["Rate"]), 'amount': float(i["Quantity"])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['buy'], True)
        asks = self.sort_and_format(depth['sell'], False)
        while bids[0]["price"] > asks[0]["price"]:
            bids.pop(0)
        while asks[0]["price"] < bids[0]["price"]:
            asks.pop(0)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = BittrexUSD()
    print(market.get_depth())
