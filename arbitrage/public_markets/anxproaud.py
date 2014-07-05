from ._anxpro import ANXPro


class ANXProAUD(ANXPro):
    def __init__(self):
        super().__init__("AUD", "BTCAUD")
