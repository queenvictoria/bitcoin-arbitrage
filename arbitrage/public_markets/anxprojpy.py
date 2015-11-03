from ._anxpro import ANXPro


class ANXProJPY(ANXPro):
    def __init__(self):
        super().__init__("JPY", "BTCJPY")
