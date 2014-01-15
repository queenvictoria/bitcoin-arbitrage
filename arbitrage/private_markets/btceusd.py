# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market, TradeException
import time
import hmac
import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
import hashlib
import sys
import json
import config
import requests

class PrivateBtceUSD(Market):

    def __init__(self):
        super().__init__()
        self.proxydict = None
        self.api_key = config.btce_api_key
        self.api_secret = config.btce_api_secret
        self.currency = "USD"
        self.get_info()        
        
    def _create_nonce(self):
        return int(time.time())

    def _send_request(self, method, params={}, extra_headers=None):
        nonce = str(self._create_nonce())
        params['method'] = method
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
        response = requests.post("https://btc-e.com/tapi", data=message, headers=headers)        
        code = response.status_code
        if code == 200:            
            if 'error' in response.json():
                return False, response.json()['error']
            else:
                return response.json()
        return None

    def _buy(self, amount, price):
        """Create a buy limit order"""
        params = {"pair": self.pair, "type" : "buy", "rate" : price, "amount" : amount}
        response = self._send_request("Trade", params)
        if "error" in response:
            raise TradeException(response["error"])

    def _sell(self, amount, price):
        """Create a sell limit order"""
        params = {"pair": self.pair, "type" : "sell", "rate" : price, "amount" : amount}
        response = self._send_request("Trade", params)
        if "error" in response:
            raise TradeException(response["error"])

    def get_info(self):
        """Get balance"""
        response = self._send_request("getInfo")
        if response:
            #print(json.dumps(response))
            return_ = response["return"]
            funds = return_["funds"]
            self.btc_balance = float(funds["btc"])
            self.usd_balance = float(funds["usd"])