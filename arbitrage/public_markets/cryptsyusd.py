import urllib.request
import urllib.error
import urllib.parse
import json
import logging
from .market import Market, GetDepthException
from util import CryptsyUtil

class CryptsyUSD(Market):   
    
    def __init__(self):
        super(CryptsyUSD, self).__init__("USD")
        self.update_rate = 20
        self.depth = {'asks': [{'price': 0, 'amount': 0}], 'bids': [
            {'price': 0, 'amount': 0}]}
        cu = CryptsyUtil()
        self.pair_id = cu.get_Pair_Id_Mapping(self.pair1_name, self.pair2_name)
                    
    def update_depth(self):
        params = {"method": "singleorderdata", "marketid": str(self.pair_id) }
        res = urllib.request.urlopen(
            'http://pubapi.cryptsy.com/api.php', data=bytes(urllib.parse.urlencode(params),"UTF-8"))
        jsonstr = res.read().decode('utf8')
        try:
            data = json.loads(jsonstr)
        except Exception:
            logging.error("%s - Can't parse json: %s" % (self.name, jsonstr))
        if "success" in data:
            if int(data["success"]) == 1:
                ret = data["return"]
                if self.pair1_name in ret:
                    pair_data = ret[self.pair1_name]                    
                    self.depth = self.format_depth(pair_data)
                    return
        logging.error("%s - fetched data error" % (self.name))
        raise GetDepthException("update_depth failed json=" + json.dumps(data))

    def sort_and_format(self, l, reverse=False):
        l.sort(key=lambda x: float(x["price"]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i["price"]), 'amount': float(i["quantity"])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['buyorders'], True)
        asks = self.sort_and_format(depth['sellorders'], False)
        return {'asks': asks, 'bids': bids}

if __name__ == "__main__":
    market = CryptsyUSD()
    print(market.get_depth())
