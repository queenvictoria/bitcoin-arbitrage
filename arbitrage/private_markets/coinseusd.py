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

class PrivateCoinsEUSD(Market):
    placeorder_url = "https://www.coins-e.com/api/v2/market/"
    getfunds_url = "https://www.coins-e.com/api/v2/wallet/all/"
    def __init__(self):
        super().__init__()
        self.proxydict = None
        self.api_key = config.coinse_api_key
        self.api_secret = config.coinse_api_secret
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
            'key': self.api_key,
            'sign': signature
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
        params = {"method": "neworder", "order_type" : "buy", "rate" : price, "quantity" : amount}
        response = self._send_request(self.placeorder_url + self.pair + "/", params)        
        if False in response:
            raise TradeException(response["message"])

    def _sell(self, amount, price):
        """Create a sell limit order"""
        params = {"method": "neworder", "order_type" : "sell", "rate" : price, "quantity" : amount}
        response = self._send_request(self.placeorder_url + self.pair + "/", params)
        if False in response:
            raise TradeException(response["message"])

    def get_info(self):
        """Get balance"""
        params = {"method": "getwallets"}        
        response = self._send_request(self.getfunds_url, params)
        if response:
            print(json.dumps(response))
            if response["message"] != "success":
                raise GetInfoException(response["message"])
            funds = response["wallets"]
            if funds:
                if "BTC" in funds:
                    self.btc_balance = float((funds["BTC"])["a"])
                # USD is not supported (yet) by Coins-e
                self.usd_balance = float(0.0)
                if self.pair1_name in funds:
                    self.pair1_balance = float((funds[self.pair1_name])["a"])
                if self.pair2_name in funds:
                    self.pair2_balance = float((funds[self.pair2_name])["a"])
            else:
                raise GetInfoException("Critical error no balances received")