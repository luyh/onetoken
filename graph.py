import requests
import itertools
import pandas as pd
from sync_api.demo_public import OneToken
# 图的节点结构
class Node:
    def __init__(self, exchange,name):
        self.exchange = exchange
        self.name = name      # 节点值

        self.contract = pd.DataFrame()      #DataFrame入节点，边：dict:名称:节点，边 ,入度

        self.mid = pd.DataFrame()

        self.path = pd.DataFrame()



# 图的边结构
class Edge:
    def __init__(self,fro, to,rate = {}):
        self.fro = fro              # 边的from节点
        self.to = to                # 边的to节点

        self.rate = rate

        self.df = pd.DataFrame()

def get_price(contract):
    print(contract)
    res = requests.get( 'https://1token.trade/api/v1/quote/single-tick/okex/{}'.format(contract) )
    #print(res.json())

    bid = res.json()['bids'][0]['price']
    ask = res.json()['asks'][0]['price']

    return bid,ask
    #
    # if not self.invert:
    #     self.price = res.json()['bids'][0]['price']
    # else:
    #     self.price = 1 / res.json()['asks'][0]['price']
    #
    # self.value = self.price * (1 - self.taker_commition)

# 图结构
class Graph:
    def __init__(self):
        self.nodes = {}     # 图的所有节点集合  字典形式：{节点编号：节点}
        self.edges = pd.DataFrame()    # 图的边集合

        self.pah = {}


def demo():
    DEBUG = True
    onetoken = OneToken()

    exchange = onetoken.exchanges
    okex_contracts = onetoken.contracts['okex']['name']
    okex_tickets = onetoken.get_quote_tickets('okex')
    print(okex_tickets)
    okex_tickets['ask_price'] = list(map(lambda x: x[0]['price'], okex_tickets['asks']))
    okex_tickets['ask_volume'] = list(map(lambda x: x[0]['volume'], okex_tickets['asks']))
    okex_tickets['bid_price'] = list(map(lambda x: x[0]['price'], okex_tickets['bids']))
    okex_tickets['bid_volume'] = list(map(lambda x: x[0]['volume'], okex_tickets['bids']))
    del okex_tickets['asks']
    del okex_tickets['bids']
    print(okex_tickets)

    graph = Graph()

    for contract in okex_contracts:
        pair = contract.split( '.' )

        ask_price = okex_tickets['ask_price'][okex_tickets['contract'] == ('okex/'+contract )]
        bid_price = okex_tickets['bid_price'][okex_tickets['contract'] ==('okex/'+contract) ]

        if not pair[0] in graph.nodes.keys():
            graph.nodes[pair[0]] = Node('okex', pair[0] )
        if not pair[1] in graph.nodes.keys():
            graph.nodes[pair[1]] = Node('okex', pair[1])

        Node0 = graph.nodes[pair[0]]
        Node1 = graph.nodes[pair[1]]

        newEdge0 = Edge( Node0, Node1)
        newEdge1 = Edge(Node1, Node0)
        dict0 = {
            'fro': pair[0],
            'to':  pair[1],
            'ask_price':ask_price,
            'bid_price':bid_price
        }
        newEdge0.df = pd.DataFrame(dict0)
        print(newEdge0.df)

        dict1 = {
            'fro': pair[1],
            'to':  pair[0],
            'ask_price':1 / bid_price,
            'bid_price':1 / ask_price
        }
        newEdge1.df = pd.DataFrame(dict1)
        print(newEdge1.df)
        graph.edges = pd.concat([graph.edges, newEdge0.df, newEdge1.df])

        contract_df0 = pd.DataFrame(newEdge0.df[['to','ask_price','bid_price']])
        print(contract_df0)
        Node0.contract = pd.concat([Node0.contract,contract_df0])
        #print(Node0.contract)

        contract_df1 = pd.DataFrame(newEdge1.df[['to','ask_price','bid_price']])
        print(contract_df1)
        Node1.contract = pd.concat([Node1.contract,contract_df1])
        #print(Node1.contract)

    for node in graph.nodes:
        print(node)
        Node0 = graph.nodes[node]
        df = Node0.contract
        print(df)

        fro = graph.edges[graph.edges['fro'].isin(df['to'])]
        Node0.mid = fro[fro['to'].isin(df['to'])]
        print(Node0.mid)

        for to in df['to']:
            print(to)
            fro = Node0.mid[Node0.mid['fro']==to]
            Node0.path = fro
            print(Node0.path)
            print('debug')

    print( 'End' )


if __name__ == '__main__':
    demo()