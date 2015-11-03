from ._anxpro import ANXPro


class ANXProEUR(ANXPro):
    def __init__(self):
        super().__init__("EUR", "BTCEUR")
