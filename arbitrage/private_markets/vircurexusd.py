from .market import Market, TradeException, GetInfoException
import time
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import json
import config
import logging
import http.client
import random

class PrivateVircurexUSD(Market):
    domain = "api.vircurex.com"
    auth_api_url = "https://api.vircurex.com/api/"
    
    def __init__(self):
        super().__init__()
        self.proxydict = None
        self.api_key = "" #Not used
        self.api_secret = config.vircurex_api_secret
        self.username = config.vircurex_username
        self.currency = "USD"
        self.get_info()        
        
    def _create_nonce(self):
        return int(time.time())

    def _send_request(self, api_url, command=None, token_param_names=[], params={}, extra_headers=None):
        #nonce = str(self._create_nonce())        
        # Thanks to hunterbunter for his cool code that made my life easier, see https://github.com/hunterbunter/vircurex-python-shotgunbot/blob/master/vircurex.py
        # for a full vircurex trading API, didn't need the whole thing just a few lines        
        t = time.strftime("%Y-%m-%dT%H:%M:%S",time.gmtime()) #UTC time        
        #txid = hashlib.sha256(str.encode("%s-%f"%(t,float(nonce)))).hexdigest(); #unique trasmission ID using nonce
        txid = hashlib.sha256(str.encode("%s-%f"%(t,random.randint(0,1<<31)))).hexdigest(); #unique trasmission ID using random integer        
        #token computation
        vp=[command]        
        params_list=[]        
        for param_name in token_param_names:
            vp.append(params[param_name])
            params_list.append(params[param_name])
        token_input="%s;%s;%s;%s;%s"%(self.api_secret,self.username,t,txid,';'.join(map(str,vp)))
        token = hashlib.sha256(str.encode(token_input)).hexdigest()        
        
        reqp=[("account",self.username),("id",txid),("token",token),("timestamp",t)]
        for param_name in token_param_names:
            reqp.append((param_name, params[param_name]))        
        message = urllib.parse.urlencode(reqp)        
        #headers = {
        #    'Content-type': 'application/x-www-form-urlencoded',
        #    'Accept': 'application/json, text/javascript, */*; q=0.01',
        #    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'            
        #}
        #if extra_headers is not None:
        #    for k, v in extra_headers.items():
        #        headers[k] = v
        post_url = api_url + "?" + message
        #print("post_url=" + post_url)
        #print("message=" + message)
        # Very strange, the other http API's from python would not work with vircurex site, giving 404 error,
        # but this one does as does pasting the URL manually in to web browser...
        # Not sure what is going on, even had set headers (commented out now) to mimic web browser.
        # In any case below code hacked from https://github.com/christopherpoole/pyvircurex/blob/master/vircurex/common.py works!
        connection = http.client.HTTPSConnection(self.domain)
        connection.request("GET", post_url, {}, {})
        response = connection.getresponse()
        logging.info(self.name + ": HTTPSConnection::request(GET...")
        if response.status == 200:
            jsonstr = response.read()
            connection.close()
            return json.loads(str(jsonstr, "UTF-8"))
        connection.close()        
        return None

    def _buy(self, amount, price):
        """Create a buy limit order"""
        token_param_names = [ "ordertype", "amount", "currency1", "unitprice", "currency2" ]
        params = {"ordertype": "BUY", "amount": amount, "currency1": self.pair1_name, "unitprice": price, "currency2": self.pair2_name} 
        response = self._send_request(self.auth_api_url+"create_released_order.json", command="create_order", token_param_names=token_param_names, params=params)
        if "status" in response:
            if int(response["status"]) != 0:
               raise TradeException("params=" + str(params) + " response=" + str(response))
        else:
            raise TradeException("JSON error")

    def _sell(self, amount, price):
        """Create a sell limit order"""
        token_param_names = [ "ordertype", "amount", "currency1", "unitprice", "currency2" ]
        params = {"ordertype": "SELL", "amount": amount, "currency1": self.pair1_name, "unitprice": price, "currency2": self.pair2_name}
        response = self._send_request(self.auth_api_url+"create_released_order.json", command="create_order", token_param_names=token_param_names, params=params)
        if "status" in response:
            if int(response["status"]) != 0:
                raise TradeException("params=" + str(params) + " response=" + str(response))
        else:
            raise TradeException("JSON error")

    def get_info(self):
        """Get balance"""        
        response = self._send_request(self.auth_api_url+"get_balances.json", command="get_balances")
        if response:
            #logging.debug("%s::get_info:JSON=%s" % (self.name, json.dumps(response)))
            if "status" in response:
                if int(response["status"]) != 0:
                    raise GetInfoException(response["statustext"])
            if "balances" in response:
                balances = response["balances"]
                if "BTC" in balances:
                    self.btc_balance = float(balances["BTC"]["availablebalance"])
                if "USD" in balances:
                    self.usd_balance = float(balances["USD"]["availablebalance"])
                if self.pair1_name in balances:
                    self.pair1_balance = float(balances[self.pair1_name]["availablebalance"])
                if self.pair2_name in balances:
                    self.pair2_balance = float(balances[self.pair2_name]["availablebalance"])
        else:
            raise GetInfoException(self.name+": JSON error")