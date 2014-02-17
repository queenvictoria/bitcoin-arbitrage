import logging
from .observer import Observer
import config

class Logger(Observer):
    def __init__(self):
        self.pair = config.pair
        pair_names = str.split(config.pair, "_")
        self.pair1_name = pair_names[0]
        self.pair2_name = pair_names[1]
        
    def opportunity(self, profit, volume, buyprice, kask, sellprice, kbid, perc,
                    weighted_buyprice, weighted_sellprice):
        logging.info("profit: %.8f %s with volume: %.8f %s - buy at %.8f (%s) sell at %.8f (%s) ~%.2f%%" % (profit, self.pair2_name, volume, self.pair1_name, buyprice, kask, sellprice, kbid, perc))
