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
import logging
from util import CryptsyUtil

class PrivateCryptsyUSD(Market):
    
    auth_api_url = "https://www.cryptsy.com/api"    
    
    def __init__(self):
        super().__init__()
        self.proxydict = None
        self.api_key = config.cryptsy_api_key
        self.api_secret = config.cryptsy_api_secret
        cu = CryptsyUtil()
        self.pair_id = cu.get_Pair_Id_Mapping(self.pair1_name, self.pair2_name)
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
            'Sign': signature,
            'Key': self.api_key            
        }
        if extra_headers is not None:
            for k, v in extra_headers.items():
                headers[k] = v
        response = requests.post(api_url, data=message, headers=headers)        
        code = response.status_code
        if code == 200:            
            return response.json()
        return None

    def _buy(self, amount, price):
        """Create a buy limit order"""
        params = {"method": "createorder", "marketid": self.pair_id, "ordertype" : "Buy", "quantity" : amount, "price" : price}
        response = self._send_request(self.auth_api_url, params)        
        if "success" in response:
            if int(response["success"]) == 0:
               raise TradeException(response["error"])
        else:
            raise TradeException("JSON error")

    def _sell(self, amount, price):
        """Create a sell limit order"""
        params = {"method": "createorder", "marketid": self.pair_id, "ordertype" : "Sell", "quantity" : amount, "price" : price}
        response = self._send_request(self.auth_api_url, params)
        if "success" in response:
            if int(response["success"]) == 0:
                raise TradeException(response["error"])
        else:
            raise TradeException("JSON error")

    def get_info(self):
        """Get balance"""
        params = {"method": "getinfo"}
        response = self._send_request(self.auth_api_url, params)
        if response:
            #logging.debug("get_info:JSON=%s" % (json.dumps(response)))
            if "success" in response:
                if int(response["success"]) != 1:
                    raise GetInfoException(response["error"])
            data = response["return"]
            if "balances_available" in data:
                funds = data["balances_available"]
                if funds:
                    if "BTC" in funds:
                        self.btc_balance = float(funds["BTC"])
                    # USD is not supported (yet) by Coins-e
                    self.usd_balance = float(0.0)
                    if self.pair1_name in funds:
                        self.pair1_balance = float(funds[self.pair1_name])
                    if self.pair2_name in funds:
                        self.pair2_balance = float(funds[self.pair2_name])
                else:
                    raise GetInfoException("Critical error no balances received")
        else:
            raise GetInfoException("JSON error")