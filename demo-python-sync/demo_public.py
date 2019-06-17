"""
这个demo包含一些公开的接口
"""
from pprint import pprint

import requests
import pandas as pd
import pickle

from demo_private import api_call

def get_time():
    res = requests.get('https://1token.trade/api/v1/basic/time')
    pprint(res.json())

def get_exchanges():
    # 获取交易所信息
    res = requests.get('https://1token.trade/api/v1/basic/support-exchanges-v2')
    # pprint(res.json(), width=240)
    exchanges = pd.DataFrame(res.json(), columns=['exchange', 'alias', 'sub_markets', 'sub_markets_alias', 'type'])
    #print(exchanges)
    return exchanges

def get_contract(exchange):
    res = requests.get('https://1token.trade/api/v1/basic/contracts?exchange={}'.format(exchange))
    # pprint(res.json(), width=1000)
    df = pd.DataFrame(res.json(),
                                       columns=['id', 'name', 'symbol', 'unit_amount', 'min_change', 'min_amount'])  #
    #print(contracts[exchange])
    return df

def get_contracts(exchanges):
    t = get_time()
    print(t)

    contracts = {}
    for exchange in exchanges['exchange']:
        contract = get_contract(exchange)
        contracts[exchange] = contract  #
    return contracts

def demo():
    #获取支持的交易所
    exchanges = get_exchanges()
    exchanges.to_csv('exchanges.csv')
    print(exchanges)

    #获取各交易所交易对信息
    contracts = get_contracts(exchanges)
    contracts

    #print(contracts)
    # for exchange in exchanges['exchange']:
    #     print(contracts[exchange])


    res = requests.get('https://1token.trade/api/v1/quote/ticks?exchange=okef')
    #pprint(res.json()[:3], width=1000)

    tickets = pd.DataFrame(res.json(),columns=['contract','last','asks','bids'])
    print(tickets)

    #
    # res = requests.get('https://1token.trade/api/v1/quote/single-tick/okef/btc.usd.q')
    # pprint(res.json(), width=1000)
    #
    # res = requests.get('https://1token.trade/api/v1/quote/single-tick/okex/btc.usdt')
    # pprint(res.json(), width=1000)

    print('demo')

def eos_usdt_usdk_price():
    res = requests.get('https://1token.trade/api/v1/quote/single-tick/okex/eos.usdt')
    #pprint(res.json(), width=1000)

    #卖一价
    eos_usdt_ask = res.json()['asks'][0]['price']
    #print('eos_usdt_ask:',eos_usdt_ask)

    #买一价
    eos_usdt_bid = res.json()['bids'][0]['price']
    #print('eos_usdt_bid:',eos_usdt_bid)

    res = requests.get( 'https://1token.trade/api/v1/quote/single-tick/okex/eos.usdk' )
    #pprint(res.json(), width=1000)

    #卖一价
    eos_usdk_ask = res.json()['asks'][0]['price']
    #print('eos_usdk_ask:',eos_usdk_ask)

    #买一价
    eos_usdk_bid = res.json()['bids'][0]['price']
    #print('eos_usdk_bid:',eos_usdk_bid)


    res = requests.get( 'https://1token.trade/api/v1/quote/single-tick/okex/usdt.usdk' )
    #pprint(res.json(), width=1000)

    #卖一价
    usdt_usdk_ask = res.json()['asks'][0]['price']
    #print('usdt_usdk_ask:',usdt_usdk_ask)

    #买一价
    usdt_usdk_bid = res.json()['bids'][0]['price']
    #print('usdt_usdk_bid:',usdt_usdk_bid)

    eos_usdt_usdk_eos = eos_usdt_bid * usdt_usdk_bid /eos_usdk_ask / 1.0002/1.0002/1.0002
    eos_usdk_usdt_eos = eos_usdk_bid / usdt_usdk_ask / eos_usdt_ask / 1.0002/1.0002/1.0002

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

    demo()
    print('end')
    # print('start')
    # while True:
    #     eos_usdt_usdk_price()
    #     time.sleep(1)
