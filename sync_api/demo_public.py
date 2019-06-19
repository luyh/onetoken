"""
这个demo包含一些公开的接口
"""
from pprint import pprint

import requests
import pandas as pd
import pickle

from demo_private import api_call

class OneToken():
    def __init__(self,debug = False):
        self.debug = debug

        self.exchanges = None
        self.exchanges_spot = {}
        self.contracts = {}
        self.all_exchanges_tickets =  {}

        self.contracts_spot = {}

        try:
            self.load_exchanges()
        except:
            self.get_exchanges()
            self.save_exchanges()

        try:
            self.load_contracts()
        except:
            self.get_contracts()
            self.save_contracts()

    def get_time(self):
        res = requests.get('https://1token.trade/api/v1/basic/time')
        pprint(res.json())

    def get_exchanges(self):
        # 获取交易所信息
        res = requests.get('https://1token.trade/api/v1/basic/support-exchanges-v2')
        # pprint(res.json(), width=240)
        exchanges = pd.DataFrame(res.json(), columns=['exchange', 'alias', 'sub_markets', 'sub_markets_alias', 'type'])
        #print(exchanges)
        self.exchanges =  exchanges
        self.exchanges_spot = exchanges[exchanges['type'] == 'spot']
        if self.debug:
            print( 'exchanges_spot', self.exchanges_spot )

    def save_exchanges(self):
        self.exchanges.to_csv('exchanges.csv')
        self.exchanges_spot.to_csv('exchanges_spot.csv')

    def load_exchanges(self):
        self.exchanges = pd.read_csv('exchanges.csv')
        self.exchanges_spot = pd.read_csv( 'exchanges_spot.csv' )

    def get_contract(self,exchange):
        res = requests.get('https://1token.trade/api/v1/basic/contracts?exchange={}'.format(exchange))
        # pprint(res.json(), width=1000)
        df = pd.DataFrame(res.json(),
                                           columns=['id', 'name', 'symbol', 'unit_amount', 'min_change', 'min_amount'])  #
        #print(contracts[exchange])
        return df

    def get_contracts_spot(self):

        for key, values in self.contracts.items():
            if key in self.exchanges_spot['exchange'].values[:]:
                self.contracts_spot[key] = values

        if self.debug:
            print( 'contracts_spot', self.contracts_spot )

    def get_contracts(self):
        for exchange in self.exchanges['exchange']:
            contract = self.get_contract(exchange)
            self.contracts[exchange] = contract  #

    def save_contracts(self):
        with open('contracts.pk', 'wb') as f:
            pickle.dump(self.contracts, f)

    def load_contracts(self):
        with open('contracts.pk', 'rb') as f:
            self.contracts = pickle.load(f)

    def get_quote_tickets(self,exchange):
        res = requests.get('https://1token.trade/api/v1/quote/ticks?exchange={}'.format(exchange))
        #pprint(res.json()[:3], width=1000)

        tickets = pd.DataFrame(res.json(),columns=['contract','last','asks','bids'])
        tickets['ask_price'] = list(map(lambda x: x[0]['price'], tickets['asks']))
        tickets['ask_volume'] = list(map(lambda x: x[0]['volume'], tickets['asks']))
        tickets['bid_price'] = list(map(lambda x: x[0]['price'], tickets['bids']))
        tickets['bid_volume'] = list(map(lambda x: x[0]['volume'], tickets['bids']))
        del tickets['asks']
        del tickets['bids']
        
        #print(tickets)
        return tickets

    def get_all_exchanges_tickets(self):
        for exchange in self.exchanges['exchange']:
            self.all_exchanges_tickets[exchange] =self.get_quote_tickets(exchange)

    def get_single_ticket(self,exchange,contract):
        res = requests.get('https://1token.trade/api/v1/quote/single-tick/{}/{}'.format(exchange,contract))
        ticket = pd.DataFrame(res.json(),columns=['contract','last','asks','bids'])
        return ticket


def demo():
    onetoken = OneToken()

    #获取支持的交易所
    print(onetoken.exchanges)

    #获取各交易所交易对信息
    print(onetoken.contracts)

    tickets = onetoken.get_quote_tickets('okex')
    print(tickets)

    onetoken.get_all_exchanges_tickets()
    print(onetoken.all_exchanges_tickets)

    ticket = onetoken.get_single_ticket('okef','btc.usd.q')
    print(ticket)

def eos_usdt_usdk_price():
    onetoken = OneToken()
    okex_eos_usdt = onetoken.get_single_ticket('okex','eos.usdt')
    okex_eos_usdk = onetoken.get_single_ticket('okex','eos.usdk')
    okex__usdt_usdk = onetoken.get_single_ticket('okex','usdt.usdk')

    df = pd.concat([okex_eos_usdt, okex_eos_usdk,okex__usdt_usdk])

    df['ask_price'] = list(map(lambda x: x['price'], df['asks']))
    df['ask_volume'] = list(map(lambda x: x['volume'], df['asks']))
    df['bid_price'] = list(map(lambda x: x['price'], df['bids']))
    df['bid_volume'] = list(map(lambda x: x['volume'], df['bids']))
    del df['asks']
    del df['bids']

    print(df)

    buy = pd.DataFrame(index= ['eos'],columns=['usdt','usdk'])
    sell = pd.DataFrame(index= ['eos'],columns=['usdt','usdk'])

    eos_usdt_bid = df['bid_price'][df['contract'] == 'okex/eos.usdt'].values[0]
    usdt_usdk_bid = df['bid_price'][df['contract'] == 'okex/usdt.usdk'].values[0]
    eos_usdk_ask = df['ask_price'][df['contract'] == 'okex/eos.usdk'].values[0]

    eos_usdk_bid = df['bid_price'][df['contract'] == 'okex/eos.usdk'].values[0]
    usdt_usdk_ask = df['ask_price'][df['contract'] == 'okex/usdt.usdk'].values[0]
    eos_usdt_ask = df['ask_price'][df['contract'] == 'okex/eos.usdt'].values[0]

    eos_usdt_usdk_eos = eos_usdt_bid * usdt_usdk_bid /eos_usdk_ask / 1.0002/1.0002/1.0002
    eos_usdk_usdt_eos = eos_usdk_bid / usdt_usdk_ask / eos_usdt_ask / 1.0002/1.0002/1.0002

    print(eos_usdt_usdk_eos,eos_usdk_usdt_eos)
    print('debug')
    if eos_usdt_usdk_eos >= 1:
        print( 'eos_usdt_usdk_eos', eos_usdt_usdk_eos )

        print( '下单' )
        r = api_call( 'POST', '/{}/orders'.format( account ),
                      data={'contract': 'okex/eos.usdt', 'price': eos_usdt_bid, 'bs': 's', 'amount': 10,
                            'options': {'close': False}} )
        #print( r.json() )

        r = api_call( 'POST', '/{}/orders'.format( account ),
                      data={'contract': 'okex/usdt.usdk', 'price': usdt_usdk_bid, 'bs': 's', 'amount': 10*eos_usdt_bid,
                            'options': {'close': False}} )
        print( r.json() )

        r = api_call( 'POST', '/{}/orders'.format( account ),
                      data={'contract': 'okex/eos.usdk', 'price': eos_usdk_ask, 'bs': 'b', 'amount': 10*eos_usdt_bid/eos_usdk_ask,
                            'options': {'close': False}} )
        print( r.json() )

    elif eos_usdk_usdt_eos>=1:
        print( 'eos_usdk_usdt_eos', eos_usdk_usdt_eos )

        print( '下单' )
        r = api_call( 'POST', '/{}/orders'.format( account ),
                      data={'contract': 'okex/eos.usdk', 'price': eos_usdk_bid, 'bs': 's', 'amount': 10,
                            'options': {'close': False}} )
        #print( r.json() )

        r = api_call( 'POST', '/{}/orders'.format( account ),
                      data={'contract': 'okex/usdt.usdk', 'price': usdt_usdk_ask, 'bs': 'b',
                            'amount': 10 * usdt_usdk_ask,
                            'options': {'close': False}} )
        #print( r.json() )

        r = api_call( 'POST', '/{}/orders'.format( account ),
                      data={'contract': 'okex/eos.usdk', 'price': eos_usdk_ask, 'bs': 'b',
                            'amount': 10 * usdt_usdk_ask / eos_usdt_ask,
                            'options': {'close': False}} )
        #print( r.json() )


import time
if __name__ == '__main__':

    account = 'okex/mock-eos-usdt-usdk'

    print( '查看账户信息' )
    r = api_call( 'GET', '/{}/info'.format( account ) )
    print( r.json() )

    eos_usdt_usdk_price()
    print('end')
    # print('start')
    # while True:
    #     eos_usdt_usdk_price()
    #     time.sleep(1)
