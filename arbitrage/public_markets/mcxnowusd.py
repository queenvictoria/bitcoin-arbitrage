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
import urllib.request
import urllib.error
import urllib.parse
import http.client
import logging
from .market import Market
from xmlread import Xml2Dict

class McxNowUSD(Market):
    domain = "mcxnow.com"    
    api_url = 'https://mcxnow.com/orders'
    
    def __init__(self):
        super(McxNowUSD, self).__init__("USD")
        self.update_rate = 20
        self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
            {'price': 0, 'amount': 0}]}
        self.xml2dict = Xml2Dict()

    def update_depth(self):
        params = {"cur": self.pair1_name}
        post_url = self.api_url+"?"+urllib.parse.urlencode(params)
        connection = http.client.HTTPSConnection(self.domain)
        connection.request("GET", post_url, {}, {})
        response = connection.getresponse()        
        if response.status == 200:
            xmlstr = str(response.read(), "UTF-8")
        connection.close()        
        try:            
            data = self.xml2dict.getDictFromXml(xmlstr)
        except Exception:
            logging.error("%s - Can't parse XML: %s" % (self.name, str(Exception)))        
        if "doc" in data:
            self.depth = self.format_depth(data["doc"])
        else:
            logging.error("%s - fetched data error XML=%s" % (self.name, str(data)) )

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x['p']), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i['p']), 'amount': float(i['c1'])})
        return r

    def format_depth(self, depth):        
        bids = self.sort_and_format(depth['buy'], True)
        asks = self.sort_and_format(depth['sell'], False)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = McxNowUSD()
    print(market.get_depth())