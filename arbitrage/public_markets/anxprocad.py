from ._anxpro import ANXPro


class ANXProCAD(ANXPro):
    def __init__(self):
        super().__init__("CAD", "BTCCAD")
