import urllib.request
import urllib.error
import urllib.parse
import http.client
import json
import logging
from .market import Market

class VircurexUSD(Market):
    domain = "api.vircurex.com"    
    api_url = 'https://api.vircurex.com/api/orderbook.json'
    
    def __init__(self):
        super(VircurexUSD, self).__init__("USD")
        self.update_rate = 20
        self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
            {'price': 0, 'amount': 0}]}

    def update_depth(self):
        params = {"base": self.pair1_name, "alt": self.pair2_name}        
        post_url = self.api_url+"?"+urllib.parse.urlencode(params)
        connection = http.client.HTTPSConnection(self.domain)
        connection.request("GET", post_url, {}, {})
        response = connection.getresponse()
        #logging.info(self.name + "::update_depth:HTTPSConnection::request(GET...status=%d" % (response.status))
        if response.status == 200:
            jsonstr = response.read()            
        connection.close()        
        try:            
            data = json.loads(str(jsonstr, "UTF-8"))
        except Exception:
            logging.error("%s - Can't parse json: %s" % (self.name, jsonstr))
        if "status" in data:
            if int(data["status"]) == 0:        
                self.depth = self.format_depth(data)
            else:                    
                logging.error("%s - fetched data error JSON=%s" % (self.name, str(data)) )

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i[0]), 'amount': float(i[1])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True)
        asks = self.sort_and_format(depth['asks'], False)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = VircurexUSD()
    print(market.get_depth())
