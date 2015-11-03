from ._anxpro import ANXPro


class ANXProCNY(ANXPro):
    def __init__(self):
        super().__init__("CNY", "BTCCNY")
