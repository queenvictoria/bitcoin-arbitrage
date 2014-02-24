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
import config
import logging
from mcxnowapi import McxNowSession

class PrivateMcxNowUSD(Market):
    
    retry_logins = 2
    
    def __init__(self):
        super().__init__()
        self.username = config.mcxnow_username
        self.password = config.mcxnow_password
        self.currency = "USD"        
        self.S = McxNowSession(self.username, self.password) # See comments at top
        self.get_info()

    def __del__(self):
        self.S.Logout()
        pass
 
    def _buy(self, amount, price):
        """Create a buy limit order"""        
        for i in range(1, self.retry_logins):
            ret = self.S.SendBuyOrder(self.pair1_name, amount*price, price, 1) # mcxnowapi/api.py defaults to type=1 or btc for buys
            if ret == 1: # success
                break            
            if ret == 0:
                errno = self.S.ErrorCode
                if errno == 110: # Session timed out or was logged out so retry with login
                    self.S.Login(self.username, self.password)
                    continue
                if self.log_mcx_error("_buy", self.S.ErrorCode) == 1:
                    raise TradeException(self.name + ": _buy() S.ErrorCode="+str(self.S.ErrorCode))
                break

    def _sell(self, amount, price):
        """Create a sell limit order"""        
        for i in range(1, self.retry_logins):
            ret = self.S.SendSellOrder(self.pair1_name, amount, price, 1)
            if ret == 1: # success
                break            
            if ret == 0:
                errno = self.S.ErrorCode
                if errno == 110: # Session timed out or was logged out so retry with login
                    self.S.Login(self.username, self.password)
                    continue
                if self.log_mcx_error("_sell", self.S.ErrorCode) == 1:
                    raise TradeException(self.name + ": _sell() S.ErrorCode="+str(self.S.ErrorCode))
                break

    def get_info(self):
        """Get balance"""
        for i in range(1, self.retry_logins):
            response = self.S.GetUserDetails()
            if response: # success
                for row in response:
                    currency = str.upper(row[0])
                    if currency == "BTC":
                        self.btc_balance = float(row[1])
                    if currency == "USD":
                        self.usd_balance = float(row[1])
                    if currency == self.pair1_name:
                        self.pair1_balance = float(row[1])
                    if currency == self.pair2_name:
                        self.pair2_balance = float(row[1])
                break
            else:
                errno = self.S.ErrorCode
                if errno == 110: # Session timed out or was logged out so retry with login
                   self.S.Login(self.username, self.password)
                   continue
                if self.log_mcx_error("get_info", self.S.ErrorCode) == 1:
                    raise GetInfoException(self.name+": S.GetUserDetails() ErrorCode="+str(self.S.ErrorCode))
                break
            
    def log_mcx_error(self, function, error_code):
        if error_code == 0:
            errmsg = "Unknown"
        elif error_code == 1:
            errmsg = "No UserName"        
        elif error_code == 101:
            errmsg = "No UserName"
        elif error_code == 102:
            errmsg = "No Password"
        elif error_code == 20000:
            errmsg = "Trade Error No Enough Coins"
        elif error_code == 20001:
            errmsg = "Trade Error Minimum Request"
        elif error_code == 20002:
            errmsg = "Trade Error Price below minimum"
        elif error_code == 20003:
            errmsg = "Trade Error Order not send"
        elif error_code == 20004:
            errmsg = "Trade Error Ten Order already"
        elif error_code == 20005:
            errmsg = "Trade Error Type Error"
        elif error_code == 20006:
            errmsg = "Trade Error Currency not accepted"
        elif error_code == 20007:
            errmsg = "Trade Error Confirm"
        elif error_code == 30001:
            errmsg = "Confirm Error Already Confirmed"
        elif error_code == 30002:
            errmsg = "Confirm Error No order with this id"            
        logging.error("%s - %s: %s:%s" % (self.name, function, errmsg, error_code))
        if error_code in range(20000, 20007):
            return 0 # Continue processing non-critical error
        return 1 # Critical error stop processing