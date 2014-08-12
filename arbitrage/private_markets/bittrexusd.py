"""
@author: Jason Chan <bearish_trader@yahoo.com>

BTC:  1ZAWfGTTyv1HuqJemnDsdQChCpiAAaZYZ
QRK:  QQcy1tMSdK8afj1gckxKJs86izP7emEitP
DOGE: DEdHx4GSjawoiSjbjWwr4BKH9Njx235CeH
MAX:  mf93aDHYqk5MxfAFvMXk8Cn1fQW6S37GYQ
MTC:  miCSJ57pae6XWi3knkmSUZXfHHg3bEEpLe
PRT:  PYdxGCTSc2tGvRbpQjwZpnktbzRqvU4DYR
DTC:  DRTJnJ9CW4WUqhPecfhRahC3SoCgXbQcN4

IMPORTANT: This module requires the mcxnowapi, from below location.
Created a fork of the mcxnowapi by mbuech <longbuech@gmail.com> 
to make it python3 compatible (and added MaxCoin plus bug fixes) get it here:

git clone https://github.com/bearishtrader/mcxnowapi.git
"""
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
#from util import CryptsyUtil

class PrivateBittrexUSD(Market):
    
    auth_api_url = "https://bittrex.com/api/v1.1/"
    
    def __init__(self):
        super().__init__()
        self.proxydict = None
        self.api_key = config.bittrex_api_key
        self.api_secret = config.bittrex_api_secret
        self.currency = "USD"
        self.get_info()        
        
    def _create_nonce(self):
        return int(time.time())

    def _send_request(self, api_url, params={}, extra_headers=None):
        nonce = str(self._create_nonce())        
        params['apikey'] = self.api_key
        params['nonce'] = nonce
        message = urllib.parse.urlencode(params)
        if sys.version_info.major == 2:
            signature = hmac.new(self.api_secret, msg=api_url+"?"+message, digestmod=hashlib.sha512).hexdigest()
        else:
            signature = hmac.new(str.encode(self.api_secret), msg=str.encode(api_url+"?"+message), digestmod=hashlib.sha512).hexdigest()
            
        headers = {
            #'Content-type': "application/x-www-form-urlencoded",
            'apisign': signature
            #'apikey': self.api_key            
        }
        if extra_headers is not None:
            for k, v in extra_headers.items():
                headers[k] = v
        response = requests.get(api_url, params=message, headers=headers)        
        code = response.status_code
        #logging.debug("_send_request:msg=%s" % (str(msg)) )
        if code == 200:            
            return response.json()
        return None

    def _buy(self, amount, price):
        """Create a buy limit order"""
        params = {"market": self.pair2_name+"-"+self.pair1_name, "quantity" : amount, "rate" : price}
        response = self._send_request(self.auth_api_url+"market/buylimit", params)
        if response:
            if "success" in response:
                if bool(response["success"]) != True:
                    err_msg = "_buy:error, response=%s" % (str(response))
                    logging.error(err_msg)
                    raise TradeException(err_msg)
            else:
                raise TradeException("JSON error, 'success' tag missing")
        else:
            raise TradeException("JSON error")

    def _sell(self, amount, price):
        """Create a sell limit order"""
        params = {"market": self.pair2_name+"-"+self.pair1_name, "quantity" : amount, "rate" : price}
        response = self._send_request(self.auth_api_url+"market/selllimit", params)
        if response:
            if "success" in response:
                if bool(response["success"]) != True:
                    err_msg = "_sell:error, response=%s" % (str(response)) 
                    logging.error(err_msg)
                    raise TradeException(err_msg)
            else:
                raise TradeException("JSON error, 'success' tag missing")
        else:
            raise TradeException("JSON error")

    def get_info(self):
        """Get balance"""
        params = {}
        response = self._send_request("https://bittrex.com/api/v1.1/account/getbalances", params)
        if response:
            logging.debug("get_info:JSON=%s" % (json.dumps(response)))
            if "success" in response:
                if bool(response["success"]) != True:
                    logging.debug("%s - get_info:JSON=%s" % (self.name, json.dumps(response)))
                    raise GetInfoException(response["error"])
            balances_list = response["result"]
            for current_balance in balances_list:
                if current_balance["Currency"] == "BTC":
                    self.btc_balance = float(current_balance["Available"])
                if current_balance["Currency"] == "USD":
                    self.usd_balance = float(current_balance["Available"])
                if current_balance["Currency"] == self.pair1_name:
                    self.pair1_balance = float(current_balance["Available"])
                if current_balance["Currency"] == self.pair2_name:
                    self.pair2_balance = float(current_balance["Available"])
        else:
            raise GetInfoException("JSON error")
