"""
这个demo包含一些公开的接口
"""
from pprint import pprint

import requests
import pandas as pd
from demo_private import api_call
import time,os,math

PRODUCTION = os.getenv( 'PRODUCTION' )

print( 'PRODUCTION:', PRODUCTION )

if PRODUCTION:
    account = os.getenv( 'ACCOUNT' )
else:
    account = os.getenv( 'MOCK' )

print( account )

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

def get_balance(account):
    #print( '查看账户信息' )
    r = api_call( 'GET', '/{}/info'.format( account ) )
    #pprint(r.json(), width=100)



    #print('查看position')
    position = r.json()['position']
    position = pd.DataFrame(position,columns=['contract','total_amount','available','frozen'])
    position.index = position['contract']
    return position

def buy(price ,amount,contract='okex/usdt.usdk'):
    r = api_call( 'POST', '/{}/orders'.format( account ),
                  data={'contract': contract, 'price': price, 'bs': 'b', 'amount': amount} )
    print( r.json() )

def sell(price ,amount,contract='okex/usdt.usdk'):
    r = api_call( 'POST', '/{}/orders'.format( account ),
                  data={'contract': contract, 'price': price, 'bs': 's', 'amount': amount} )
    print( r.json() )

def get_orders():
    #print( '查询挂单' )
    r = api_call( 'GET', '/{}/orders'.format( account ) )
    #pprint( r.json(), width=100 )

    orders = pd.DataFrame(r.json(),columns=['contract','exchange_oid','bs','entrust_amount','entrust_price','status'])
    return orders

def get_okex_usdt_usdk_orders():
    orders = get_orders()
    # print(orders)
    okex_usdt_usdk_orders = orders[orders.contract == 'okex/usdt.usdk']
    # print(okex_usdt_usdk_orders)
    return okex_usdt_usdk_orders

def cancle_orders(exchange_oids):
    for exchange_oid in exchange_oids:
        print('撤销订单：{}'.format(exchange_oid))
        r = api_call( 'DELETE', '/{}/orders'.format( account ), params={'exchange_oid': exchange_oid} )
        pprint( r.json(), width=100 )


def main():

    buy_price = 1.0005
    sell_price = 1.0010
    max_amount = 20

    print( '查询okex/usdt.usdk订单' )
    okex_usdt_usdk_orders = get_okex_usdt_usdk_orders()
    print( okex_usdt_usdk_orders )
    exchange_oids = okex_usdt_usdk_orders.exchange_oid

    print( '取消okex/usdt.usdk挂单' )
    cancle_orders( exchange_oids )

    if PRODUCTION:
        time.sleep( 5 )

    balance = get_balance( account )
    print( balance )

    while True:
        balance = get_balance( account )
        # print(available)

        last, ask, bid = usdt_usdk()
        # print(last,ask,bid)

        okex_usdt_usdk_orders = get_okex_usdt_usdk_orders()

        if okex_usdt_usdk_orders[okex_usdt_usdk_orders.bs == 's'].empty:
            # 若没有挂卖单
            if last < sell_price and balance.at['usdt', 'available'] > 1:
                amount = math.floor( balance.at['usdt', 'available'] * 100 ) / 100
                # 限制最大下单数量
                if amount > max_amount:
                    amount = max_amount
                print( 'SELL usdt ,price:{},amount:{}'.format( sell_price, amount ) )
                sell( sell_price, amount )

        if okex_usdt_usdk_orders[okex_usdt_usdk_orders.bs == 'b'].empty:
            # 若没有买单
            if last >= buy_price and balance.at['usdk', 'available'] > 1:
                amount = math.floor( balance.at['usdk', 'available'] / buy_price * 100 ) / 100
                # 限制最大下单数量
                if amount > max_amount:
                    amount = max_amount
                print( 'BUY usdt ,price:{},amount:{}'.format( buy_price, amount ) )
                buy( buy_price, amount )

        time.sleep( 5 )


if __name__ == '__main__':
    main()