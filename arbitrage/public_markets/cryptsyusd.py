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

import time
import hmac
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import sys
import json
import logging
import config
import requests
from .market import Market, GetDepthException
from util import CryptsyUtil

class CryptsyUSD(Market):   
    
    def __init__(self):
        super(CryptsyUSD, self).__init__("USD")
        self.update_rate = 20
        self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
            {'price': 0, 'amount': 0}]}
        cu = CryptsyUtil()
        self.pair_id = cu.get_Pair_Id_Mapping(self.pair1_name, self.pair2_name)
        self.api_key = config.cryptsy_api_key        
        self.api_secret = config.cryptsy_api_secret
        self.use_private_orderbook = config.cryptsy_use_private_orderbook

    def _create_nonce(self):
        return int(time.time())
                    
    def update_depth(self):
        method = "singleorderdata"
        if self.use_private_orderbook == True:
            method = "depth"
        params = {"method": str(method), "marketid": str(self.pair_id) }
        if self.use_private_orderbook == True: # Use private API to get depth
            api_url = "https://api.cryptsy.com/api"
            nonce = str(self._create_nonce())
            params['nonce'] = nonce
            message = urllib.parse.urlencode(params)

            if sys.version_info.major == 2:
                signature = hmac.new(self.api_secret, msg=message, digestmod=hashlib.sha512).hexdigest()
            else:
                signature = hmac.new(str.encode(self.api_secret), msg=str.encode(message), digestmod=hashlib.sha512).hexdigest()

            headers = {
                'Content-type': "application/x-www-form-urlencoded",
                'Sign': signature,
                'Key': self.api_key
            }
        else: # use public API to get depth 
            # Replaces pubapi1 with pubapi2 for Netherlands
            api_url = "http://pubapi1.cryptsy.com/api.php"
            message = urllib.parse.urlencode(params)
            headers = {}
        response = requests.post(api_url, data=message, headers=headers);
        code = response.status_code 
        if code == 200:
            try:
                data = response.json() 
            except Exception:
                logging.error("%s - Can't parse json: %s" % (self.name, data))
            try:
                if int(data["success"]) == 1:
                    ret = data["return"]
                if self.use_private_orderbook == True:
                    pair_data = ret
                else:
                    pair_data = ret[self.pair1_name]
                self.depth = self.format_depth(pair_data)
                return
            except Exception:
                logging.error("%s - response received but error: %s" % (self.name, data))
        else:
            logging.error("%s - fetched data error" % (self.name))
            raise GetDepthException("update_depth failed, response.status_code="+code)

    def sort_and_format(self, l, reverse=False):
        if self.use_private_orderbook == True:
            l.sort(key=lambda x: float(x[0]), reverse=reverse)
        else:
            l.sort(key=lambda x: float(x["price"]), reverse=reverse)
        r = []
        for i in l:
            if self.use_private_orderbook == True:
                r.append({'price': float(i[0]), 'amount': float(i[1])})
            else:
                r.append({'price': float(i["price"]), 'amount': float(i["quantity"])})
        return r

    def format_depth(self, depth):
        if self.use_private_orderbook == True:
            buys_name  = 'buy'
            sells_name = 'sell'
        else:
            buys_name  = 'buyorders'
            sells_name = 'sellorders'
        bids = self.sort_and_format(depth[str(buys_name)], True)
        asks = self.sort_and_format(depth[str(sells_name)], False)
        while bids[0]["price"] > asks[0]["price"]:
            bids.pop[0]
        while asks[0]["price"] < bids[0]["price"]:
            asks.pop(0)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = CryptsyUSD()
    print(market.get_depth())
