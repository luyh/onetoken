"""
这个demo包含一些公开的接口
"""
from pprint import pprint

import requests

from demo_private import api_call

def usdt_usdk():
    res = requests.get( 'https://1token.trade/api/v1/quote/single-tick/okex/usdt.usdk' )

    #print( '查询报价' )
    #pprint(res.json(), width=100)

    last = res.json()['last']
    ask = res.json()['asks'][0]['price']
    bid = res.json()['bids'][0]['price']


    #print(last,ask,bid)
    return last,ask,bid

def cancle_all_orders():
    print('撤销所有订单')
    r = api_call('DELETE', '/{}/orders/all'.format(account))
    print(r.json())

def get_account(account):
    #print( '查看账户信息' )
    r = api_call( 'GET', '/{}/info'.format( account ) )
    #pprint(r.json(), width=100)

    # print('查看market_value_detail')
    # usdt_balance = r.json()['market_value_detail']['usdt']
    # usdk_balance = r.json()['market_value_detail']['usdk']
    # eos_balance = r.json()['market_value_detail']['eos']
    #
    # print('usdk_balance',usdk_balance)
    # print('usdt_balance',usdt_balance)

    #print('查看position')
    positions = r.json()['position']
    #pprint(positions)

    pos = {}
    for position in positions:
        contract = position['contract']
        available = position['available']

        pos[contract] = available

    #print(pos)

    return pos

def buy(price ,amount):
    r = api_call( 'POST', '/{}/orders'.format( account ),
                  data={'contract': 'okex/usdt.usdk', 'price': price, 'bs': 'b', 'amount': amount} )
    print( r.json() )

def sell(price ,amount):
    r = api_call( 'POST', '/{}/orders'.format( account ),
                  data={'contract': 'okex/usdt.usdk', 'price': price, 'bs': 's', 'amount': amount} )
    print( r.json() )

import time,os,math
if __name__ == '__main__':
    PRODUCTION = os.getenv('PRODUCTION')
    print('PRODUCTION:',PRODUCTION)

    if PRODUCTION:
        account = os.getenv('ACCOUNT')
        print(account)
    else:
        account = os.getenv('MOCK')

    cancle_all_orders()
    time.sleep(5)

    available = get_account( account )
    print(available)


    while True:

        available = get_account(account)
        #print(available)

        last,ask,bid = usdt_usdk()

        #print(last,ask,bid)
        buy_price = 1.0005
        sell_price = 1.0009

        if last >=buy_price and available['usdk']>1:
            amount = math.floor(available['usdk']/buy_price *100)/100
            print( 'BUY usdt ,price:{},amount:{}'.format(buy_price,amount))
            buy(buy_price,amount)

        elif last<sell_price and available['usdt']>1:
            amount = math.floor(available['usdt'] *100)/100
            print('SELL usdt ,price:{},amount:{}'.format(sell_price, amount))
            sell(sell_price,amount)

        time.sleep(5)
