# Copyright (C) 2013, Maxime Biais <maxime@biais.org>

from .market import Market
import time
import base64
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
import re
import logging
import config


class PrivateANXPro(Market):
    def __init__(self):
        super().__init__()
        self.base_url = "https://anxpro.com/api/2/"
        self.order_path = {"method": "POST", "path": "generic/private/order/result"}
        self.open_orders_path = {"method": "POST", "path": "generic/private/orders"}
        self.info_path = {"method": "POST", "path": "money/info"}
        self.withdraw_path = {"method": "POST", "path": "generic/bitcoin/send_simple"}
        self.deposit_path = {"method": "POST", "path": "generic/bitcoin/address"}

        self.key = config.anxpro_api_key
        self.secret = config.anxpro_api_secret
        self.get_info()

    def _create_nonce(self):
        return int(time.time() * 1000000)

    def _change_currency_url(self, url, currency):
        return re.sub(r'BTC\w{3}', r'BTC' + currency, url)

    def _to_int_price(self, price, currency):
        ret_price = None
        if currency in ["USD", "EUR", "GBP", "PLN", "CAD", "AUD", "CHF", "CNY",
                        "NZD", "RUB", "DKK", "HKD", "SGD", "THB"]:
            ret_price = price
            ret_price = int(price * 100000)
        elif currency in ["JPY", "SEK"]:
            ret_price = price
            ret_price = int(price * 1000)
        return ret_price

    def _to_int_amount(self, amount):
        amount = amount
        return int(amount * 100000000)

    def _from_int_amount(self, amount):
        return amount / 100000000.

    def _from_int_price(self, amount):
        # FIXME: should take JPY and SEK into account
        return amount / 100000.

    def _send_request(self, url, params, extra_headers=None):
        urlparams = urllib.parse.urlencode(dict(params))
        secret_message = url["path"] + chr(0) + urlparams
        secret_from_b64 = base64.b64decode(bytes(self.secret, "UTF-8"))
        hmac_secret = hmac.new(secret_from_b64, secret_message.encode("UTF-8"), hashlib.sha512)
        hmac_sign = base64.b64encode(hmac_secret.digest())

        headers = {
            'Rest-Key': self.key,
            'Rest-Sign': hmac_sign.decode("UTF-8"),
            'Content-type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        }
        if extra_headers is not None:
            for k, v in extra_headers.items():
                headers[k] = v
        try:
            req = urllib.request.Request(self.base_url + url['path'],
                                         bytes(urlparams,
                                               "UTF-8"), headers)
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                jsonstr = response.read()
                return json.loads(str(jsonstr, "UTF-8"))
        except Exception as err:
            logging.error('Can\'t request ANXPro, %s' % err)
        return None

    def trade(self, amount, ttype, price=None):
        if price:
            price = self._to_int_price(price, self.currency)
        amount = self._to_int_amount(amount)

        self.buy_path["path"] = self._change_currency_url(
            self.buy_path["path"], self.currency)

        params = [("nonce", self._create_nonce()),
                  ("amount_int", str(amount)),
                  ("type", ttype)]
        if price:
            params.append(("price_int", str(price)))

        response = self._send_request(self.buy_path, params)
        if response and "result" in response and \
           response["result"] == "success":
            return response["return"]
        return None

    def _buy(self, amount, price):
        return self.trade(amount, "bid", price)

    def _sell(self, amount, price):
        return self.trade(amount, "ask", price)

    def withdraw(self, amount, address):
        params = [("nonce", self._create_nonce()),
                  ("amount_int", str(self._to_int_amount(amount))),
                  ("address", address)]
        response = self._send_request(self.withdraw_path, params)
        if response and "result" in response and \
           response["result"] == "success":
            return response["return"]
        return None

    def deposit(self):
        params = [("nonce", self._create_nonce())]
        response = self._send_request(self.deposit_path, params)
        if response and "result" in response and \
           response["result"] == "success":
            return response["return"]
        return None

class PrivateANXProAUD(PrivateANXPro):
    def __init__(self):
        super().__init__()
        self.ticker_path = {"method": "GET", "path": "BTCAUD/public/ticker"}
        self.buy_path = {"method": "POST", "path": "BTCAUD/private/order/add"}
        self.sell_path = {"method": "POST", "path": "BTCAUD/private/order/add"}
        self.currency = "AUD"

    def get_info(self):
        params = [("nonce", self._create_nonce())]
        response = self._send_request(self.info_path, params)
        if response and "result" in response and response["result"] == "success":
            self.btc_balance = self._from_int_amount(int(
                response["data"]["Wallets"]["BTC"]["Balance"]["value_int"]))
            self.aud_balance = self._from_int_price(int(
                response["data"]["Wallets"]["AUD"]["Balance"]["value_int"]))
            self.usd_balance = self.fc.convert(self.aud_balance, "AUD", "USD")
            self.eur_balance = self.fc.convert(self.aud_balance, "AUD", "EUR")

            funds = response["data"]["Wallets"]
            if self.pair1_name in funds:
                self.pair1_balance = self._from_int_amount(
                    int(funds[self.pair1_name]["Balance"]["value_int"])
                    )
            if self.pair2_name in funds:
                self.pair2_balance = self._from_int_amount(
                    int(funds[self.pair2_name]["Balance"]["value_int"])
                    )
            return 1
        return None

class PrivateANXProUSD(PrivateANXPro):
    def __init__(self):
        super().__init__()
        self.ticker_path = {"method": "GET", "path": "BTCUSD/public/ticker"}
        self.buy_path = {"method": "POST", "path": "BTCUSD/private/order/add"}
        self.sell_path = {"method": "POST", "path": "BTCUSD/private/order/add"}
        self.currency = "USD"

    def get_info(self):
        params = [("nonce", self._create_nonce())]
        response = self._send_request(self.info_path, params)
        if response and "result" in response and response["result"] == "success":
            self.btc_balance = self._from_int_amount(int(
                response["data"]["Wallets"]["BTC"]["Balance"]["value_int"]))
            self.usd_balance = self._from_int_price(int(
                response["data"]["Wallets"]["USD"]["Balance"]["value_int"]))

            funds = response["data"]["Wallets"]
            if self.pair1_name in funds:
                self.pair1_balance = self._from_int_amount(
                    int(funds[self.pair1_name]["Balance"]["value_int"])
                    )
            if self.pair2_name in funds:
                self.pair2_balance = self._from_int_amount(
                    int(funds[self.pair2_name]["Balance"]["value_int"])
                    )
            return 1
        return None
