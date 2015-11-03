from ._anxpro import ANXPro


class ANXProHKD(ANXPro):
    def __init__(self):
        super().__init__("HKD", "BTCHKD")
