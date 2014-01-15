# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException, GetInfoException
import time
import hmac
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import sys
import json
import config
import requests

class PrivateBterUSD(Market):
    placeorder_url = "https://bter.com/api/1/private/placeorder"
    getfunds_url = "https://bter.com/api/1/private/getfunds"
    def __init__(self):
        super().__init__()
        self.proxydict = None
        self.api_key = config.bter_api_key
        self.api_secret = config.bter_api_secret
        self.currency = "USD"
        self.get_info()        
        
    def _create_nonce(self):
        return int(time.time())

    def _send_request(self, api_url, params={}, extra_headers=None):
        nonce = str(self._create_nonce())        
        params['nonce'] = nonce
        message = urllib.parse.urlencode(params)
        
        if sys.version_info.major == 2:
            signature = hmac.new(self.api_secret, msg=message, digestmod=hashlib.sha512).hexdigest()
        else:
            signature = hmac.new(str.encode(self.api_secret), msg=str.encode(message), digestmod=hashlib.sha512).hexdigest()
            
        headers = {
            'Content-type': "application/x-www-form-urlencoded",
            'Key': self.api_key,
            'Sign': signature
        }
        if extra_headers is not None:
            for k, v in extra_headers.items():
                headers[k] = v
        response = requests.post(api_url, data=message, headers=headers)        
        code = response.status_code
        if code == 200:            
            if 'error' in response.json():
                return False, response.json()['error']
            else:
                return response.json()
        return None

    def _buy(self, amount, price):
        """Create a buy limit order"""
        params = {"pair": str.lower(self.pair), "type" : "BUY", "rate" : price, "amount" : amount}
        response = self._send_request(self.placeorder_url, params)        
        if "false" in response:
            raise TradeException(response["msg"])

    def _sell(self, amount, price):
        """Create a sell limit order"""
        params = {"pair": str.lower(self.pair), "type" : "SELL", "rate" : price, "amount" : amount}
        response = self._send_request(self.placeorder_url, params)
        if "false" in response:
            raise TradeException(response["msg"])

    def get_info(self):
        """Get balance"""
        response = self._send_request(self.getfunds_url)
        if response:
            #print(json.dumps(response))
            if "false" in response:
                raise GetInfoException(response["msg"])
            funds = response["available_funds"]
            if funds:
                if funds["BTC"]:
                    self.btc_balance = float(funds["BTC"])
                # USD is not supported (yet) by Bter
                self.usd_balance = float(0.0)
            else:
                self.btc_balance = 0.0
                self.usd_balance = 0.0
