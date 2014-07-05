from ._btcmarkets import BTCMarkets


class BTCMarketsAUD(BTCMarkets):
    def __init__(self):
        super().__init__("AUD", "BTC")
