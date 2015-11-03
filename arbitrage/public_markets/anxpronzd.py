from ._anxpro import ANXPro


class ANXProNZD(ANXPro):
    def __init__(self):
        super().__init__("NZD", "BTCNZD")
