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

class USDT_USDK():
    def __init__(self):

        if PRODUCTION:
            self.account = os.getenv( 'ACCOUNT' )
        else:
            self.account = os.getenv( 'MOCK' )

        print( self.account )

        self.contract = 'okex/usdt.usdk'

        self.buy_price = 1.0000
        self.sell_price = 1.0010
        self.buy_amount = 0
        self.sell_amount = 0

        self.chajia = 0.0001
        self.max_amount = 200
        self.skip_valumn = 10000  #买一量超 10K 挂单加chajia

        self.last = None
        self.ask = {'price':None,'volume':None}
        self.bid = {'price':None,'volume':None}

        self.position = None  #pd.DataFrame
        self.balance = None

        self.orders = None



    def get_usdt_usdk(self):
        res = requests.get( 'https://1token.trade/api/v1/quote/single-tick/okex/usdt.usdk' )

        #print( '查询报价' )
        #pprint(res.json(), width=100)

        self.last = res.json()['last']
        self.ask = res.json()['asks'][0]
        self.bid = res.json()['bids'][0]


    def cancle_all_orders(self):
        print('撤销所有订单')
        r = api_call('DELETE', '/{}/orders/all'.format(self.account))
        print(r.json())

    def get_balance(self):
        #print( '查看账户信息' )
        r = api_call( 'GET', '/{}/info'.format( self.account ) )
        #pprint(r.json(), width=100)

        #print('查看position')
        position = r.json()['position']
        position = pd.DataFrame(position,columns=['contract','total_amount','available','frozen'])
        position.index = position['contract']
        self.position = position

    def get_usdt_usdk_balance(self):
            self.get_balance()
            self.balance = self.position.loc[self.position.index.isin(['usdt','usdk'])]

    def buy(self,amount):
        r = api_call( 'POST', '/{}/orders'.format( self.account ),
                      data={'contract': self.contract, 'price': self.buy_price, 'bs': 'b', 'amount': self.buy_amount} )
        print( r.json() )

    def sell(self):
        print( 'SELL usdt ,price:{},amount:{}'.format( self.sell_price, self.sell_amount ) )
        r = api_call( 'POST', '/{}/orders'.format( self.account ),
                      data={'contract': self.contract, 'price': self.sell_price, 'bs': 's', 'amount': self.sell_amount} )
        print( r.json() )

    def get_orders(self):
        #print( '查询挂单' )
        r = api_call( 'GET', '/{}/orders'.format( self.account ) )
        #pprint( r.json(), width=100 )

        self.orders = pd.DataFrame(r.json(),columns=['contract','exchange_oid','bs','entrust_amount','entrust_price','status'])


    def get_okex_usdt_usdk_orders(self):
        self.get_orders()
        # print(self.orders)
        self.okex_usdt_usdk_orders = self.orders[self.orders.contract == 'okex/usdt.usdk']
        # print(self.okex_usdt_usdk_orders)

    def cancle_orders(self,exchange_oids):
        for exchange_oid in exchange_oids:
            print('撤销订单：{}'.format(exchange_oid))
            r = api_call( 'DELETE', '/{}/orders'.format( self.account ), params={'exchange_oid': exchange_oid} )
            pprint( r.json(), width=100 )

    def get_balance_price(self):
        self.get_usdt_usdk_balance()
        self.get_usdt_usdk()

        if self.bid['volume'] > self.skip_valumn:
            self.buy_price = self.bid['price'] + 0.0001
        else:
            self.buy_price = self.bid['price']

        if self.ask['price'] > self.buy_price + self.chajia:
            self.sell_price = self.ask['price']
        else:
            self.sell_price = self.buy_price + self.chajia

        # 限制最大下单数量
        self.sell_amount = min(math.floor( self.balance.at['usdt', 'available'] * 100 ) / 100,self.max_amount)

        self.buy_amount = min(math.floor( self.balance.at['usdk', 'available'] / self.buy_price * 100 ) / 100 , self.max_amount)

    def log(self):
        print( self.balance )
        print(self.okex_usdt_usdk_orders)
        print( 'last:{},ask:{},bid:{}'.format( self.last, self.ask, self.bid ) )
        if self.buy_amount > 1:
            print( 'buy_price:{},buy_amount:{}'.format( self.buy_price, self.buy_amount ) )

        if self.sell_amount >1:
            print( 'sell_price:{},sell_amount:{}'.format( self.sell_price, self.sell_amount ) )



    def run(self):
            print( '查询okex/usdt.usdk订单' )
            self.get_okex_usdt_usdk_orders()
            print( self.okex_usdt_usdk_orders )
            exchange_oids = self.okex_usdt_usdk_orders.exchange_oid

            print( '取消okex/usdt.usdk挂单' )
            self.cancle_orders( exchange_oids )

            if PRODUCTION:
                time.sleep( 5 )

            self.get_balance_price()
            self.log()

            while True:
                try:
                    self.get_balance_price()
                    self.get_okex_usdt_usdk_orders()

                    if self.okex_usdt_usdk_orders[self.okex_usdt_usdk_orders.bs == 's'].empty:
                        # 若没有挂卖单
                        if self.last < self.sell_price and self.balance.at['usdt', 'available'] > 1:
                            #print('SELL')
                            self.log()
                            self.sell()

                    if self.okex_usdt_usdk_orders[self.okex_usdt_usdk_orders.bs == 'b'].empty:
                        # 若没有买单
                        if self.last > self.buy_price and self.balance.at['usdk', 'available'] > 1:
                            self.log()
                            self.buy( )
                except:
                    print( 'while thread error' )
                time.sleep( 5 )

if __name__ == '__main__':
    usdt_usdk = USDT_USDK()
    usdt_usdk.run()