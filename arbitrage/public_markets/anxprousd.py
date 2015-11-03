from ._anxpro import ANXPro


class ANXProUSD(ANXPro):
    def __init__(self):
        super().__init__("USD", "BTCUSD")
