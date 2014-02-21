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
import json
import logging

class GetCryptsyPairIDException(Exception):
   pass
    
class CryptsyUtil:   
    
    def __init__(self): 
        self.name = self.name = self.__class__.__name__
        self.marketdata_url = "http://pubapi.cryptsy.com/api.php"
        self.filename = "pair_id_map.txt"
        
    def get_Pair_Id_Mapping(self, pair1_name, pair2_name):
        pair_fmt = pair1_name + "/" + pair2_name
        try:
            data = json.load(open(self.filename, "r"))
        except IOError:
            params = {"method": "marketdatav2"}
            marketdata = urllib.request.urlopen(self.marketdata_url, data=bytes(urllib.parse.urlencode(params),"UTF-8"))
            jsonstr = marketdata.read().decode('utf8')        
            try:
                data = json.loads(jsonstr)
            except Exception:
                logging.error("%s - Can't parse json: %s" % (self.name, jsonstr))
                return 0
            if "success" in data:
                if int(data["success"]) == 1:
                    json.dump(data, open(self.filename, "w"))    
        #logging.debug( "JSON=%s" % (data) )
        if "success" in data:
            if int(data["success"]) == 1:        
                if "return" in data:
                    ret = data["return"]
                    if "markets" in ret:
                        markets = ret["markets"]
                        if pair_fmt in markets:
                            return int((markets[pair_fmt])["marketid"])
        raise GetCryptsyPairIDException(pair_fmt + " has no matching marketid")
        return 0