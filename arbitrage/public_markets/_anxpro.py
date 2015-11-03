import urllib.request
import urllib.error
import urllib.parse
import json
import sys
from .market import Market


# http://docs.anxv2.apiary.io/#marketdata
# v2 API is compatible with MtGox v2 API
# http://docs.anxv3.apiary.io/
# v3 API is current
class ANXPro(Market):
    def __init__(self, currency, code):
        super().__init__(currency)
        self.code = code    # code is a currencypair
        self.update_rate = 30

    def update_depth(self):
        # Currency Pairs http://docs.anxv2.apiary.io/#currency_pair
        # BTCUSD,BTCHKD,BTCEUR,BTCCAD,BTCAUD,BTCSGD,BTCJPY,BTCCHF,BTCGBP,
        # BTCNZD,LTCBTC, LTCUSD, LTCHKD,LTCEUR,LTCCAD,LTCAUD,LTCSGD,LTCJPY,
        # LTCCHF,LTCGBP,LTCNZD,PPCBTC, PPCLTC,PPCUSD, PPCHKD,PPCEUR,PPCCAD,
        # PPCAUD,PPCSGD,PPCJPY,PPCCHF,PPCGBP,PPCNZD,NMCBTC, NMCLTC,NMCUSD,
        # NMCHKD,NMCEUR,NMCCAD,NMCAUD,NMCSGD,NMCJPY,NMCCHF,NMCGBP,NMCNZD,
        # DOGEBTC, DOGEUSD, DOGEHKD,DOGEEUR,DOGECAD,DOGEAUD,DOGESGD,DOGEJPY,
        # DOGECHF,DOGEGBP,DOGENZD,
        url = "https://anxpro.com/api/2/%s/money/depth/full" % self.code

        req = urllib.request.Request(url, None, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "User-Agent": "curl/7.24.0 (x86_64-apple-darwin12.0)"})

        try:
            res = urllib.request.urlopen(req)
        except HTTPError as error:
            sys.stderr.write("HTTPError: Can't open %s.\n" % url)

        try:
            depth = json.loads(res.read().decode('utf8'))
            self.depth = self.format_depth(depth)
        except:
            sys.stderr.write("Can't format depth.\n")

    def sort_and_format(self, l, reverse=False):
        # [{"amount_int": "11229900", "price": "690.05373",
        # "amount": "0.11229900", "price_int": "69005373"},
        # l.sort(key=lambda x: float(x['price']), reverse=reverse)
        l = sorted(l, key=lambda k: k['price'], reverse=reverse)

        # l.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in l:
            # sys.stderr.write("%f\n" % float(i['price']))
            r.append({'price': float(i['price']), 'amount': float(i['amount'])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(
            depth['data']['bids'], True)
        asks = self.sort_and_format(
            depth['data']['asks'], False)
        return {'asks': asks, 'bids': bids}
