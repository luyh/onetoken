"""
这个demo包含一些公开的接口
"""
from pprint import pprint

import requests
import pandas as pd
import pickle

from demo_private import api_call

class OneToken():
    def __init__(self,exchange = None,debug = False):
        self.debug = debug

        try:
            self.exchanges = pd.read_csv( 'exchanges.csv' )
        except:
            self.exchanges = self.get_exchanges()

    def get_time(self):
        res = requests.get('https://1token.trade/api/v1/basic/time')
        pprint(res.json())

    def get_exchanges(self):
        # 获取交易所信息
        res = requests.get('https://1token.trade/api/v1/basic/support-exchanges-v2')
        # pprint(res.json(), width=240)
        exchanges = pd.DataFrame(res.json(), columns=['exchange', 'alias', 'sub_markets', 'sub_markets_alias', 'type'])
        #print(exchanges)
        exchanges.to_csv('exchanges.csv')
        return exchanges

class Exchange():
    def __init__(self,exchange):
        self.exchange = exchange

        self._contract_file = '{}_contract.csv'.format(exchange)

        try:
            self.contract = pd.read_csv(self._contract_file)
        except FileNotFoundError:
            self.contract = self._get_contract()

    def _get_contract(self):
        res = requests.get( 'https://1token.trade/api/v1/basic/contracts?exchange={}'.format( self.exchange ) )
        # pprint(res.json(), width=1000)
        df = pd.DataFrame( res.json(),
                           columns=['id', 'name', 'symbol', 'unit_amount', 'min_change', 'min_amount'] )  #
        df.to_csv(self._contract_file)
        print('save {} done'.format(self._contract_file))
        return df

    def get_quote_tickets(self):
        res = requests.get( 'https://1token.trade/api/v1/quote/ticks?exchange={}'.format( self.exchange ) )
        # pprint(res.json()[:3], width=1000)

        tickets = pd.DataFrame( res.json(), columns=['contract', 'last', 'asks', 'bids'] )
        tickets['ask_price'] = list( map( lambda x: x[0]['price'], tickets['asks'] ) )
        tickets['ask_volume'] = list( map( lambda x: x[0]['volume'], tickets['asks'] ) )
        tickets['bid_price'] = list( map( lambda x: x[0]['price'], tickets['bids'] ) )
        tickets['bid_volume'] = list( map( lambda x: x[0]['volume'], tickets['bids'] ) )
        del tickets['asks']
        del tickets['bids']

        # print(tickets)
        return tickets

    def get_single_ticket(self,contract):
        res = requests.get('https://1token.trade/api/v1/quote/single-tick/{}/{}'.format(self.exchange,contract))
        ticket = pd.DataFrame(res.json(),columns=['contract','last','asks','bids'])
        return ticket

def demo():
    onetoken = OneToken()

    #获取支持的交易所
    print(onetoken.exchanges)

    okex = Exchange('okex')
    print('okex_contract',okex.contract)
    okex_tickets = okex.get_quote_tickets()
    print('okex_tickets',okex_tickets)

    okef = Exchange('okef')
    okef_btc_usd_q_ticket = okef.get_single_ticket('btc.usd.q')
    print('okef_btc_usd_q_ticket',okef_btc_usd_q_ticket)


if __name__ == '__main__':
    demo()
    print('end')

