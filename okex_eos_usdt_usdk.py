"""
这个demo包含一些公开的接口
"""
from pprint import pprint

import requests
import usdt_usdk
from demo_private import api_call

import pandas as pd

def eos_usdt_usdk_price():
    res = requests.get('https://1token.trade/api/v1/quote/single-tick/okex/eos.usdt')
    #pprint(res.json(), width=1000)

    df1 = pd.DataFrame(res.json(),columns=['asks','bids','contract','last'])
    #print(df1)

    res = requests.get( 'https://1token.trade/api/v1/quote/single-tick/okex/eos.usdk' )
    #pprint(res.json(), width=1000)
    df2 = pd.DataFrame(res.json(),columns=['asks','bids','contract','last'])
    df = pd.concat([df1,df2])
    #print(df)

    res = requests.get( 'https://1token.trade/api/v1/quote/single-tick/okex/usdt.usdk' )
    #pprint(res.json(), width=1000)

    df3 = pd.DataFrame(res.json(),columns=['asks','bids','contract','last'])
    df = pd.concat([df,df3], ignore_index=True)

    df['ask_price'] = list(map(lambda x: x['price'], df['asks']))
    df['ask_volume'] = list( map( lambda x: x['volume'], df['asks'] ) )
    df['bid_price'] = list( map( lambda x: x['price'], df['bids'] ) )
    df['bid_volume'] = list( map( lambda x: x['volume'], df['bids'] ) )
    del df['asks']
    del df['bids']

    bz = pd.DataFrame

    df['commition'] = 0.0002


    #df['eos_usdt_usdk_eos'] = list(map(lambda x: x['price'], df['ask']))

    eos_usdt_usdk_eos = eos_usdt_bid * usdt_usdk_bid /eos_usdk_ask / 1.0002/1.0002/1.0002
    eos_usdk_usdt_eos = eos_usdk_bid / usdt_usdk_ask / eos_usdt_ask / 1.0002/1.0002/1.0002

    print( df )


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


    count = 0
    profit = 1
    print('start')
    while True:
        eos_usdt_usdk_price()
        time.sleep(1)
