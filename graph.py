import requests
import itertools
import pandas as pd
from sync_api.demo_public import OneToken
import math
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

# 图结构
class Graph:
    def __init__(self):
        self.nodes = {}     # 图的所有节点集合  字典形式：{节点编号：节点}
        self.edges = pd.DataFrame()    # 图的边集合

        self.path = pd.DataFrame(columns=['fro_contract','to0_contract','to0_price','to1_contract','to1_price','to2_contract','to2_price'])


def demo():
    DEBUG = True
    onetoken = OneToken()

    exchanges = onetoken.exchanges
    print(exchanges)

    exchanges_spot = exchanges[exchanges['type'] == 'spot']
    print(exchanges_spot['exchange'])

    # okex_contracts = onetoken.contracts['okex']['name']
    # print(okex_contracts)

    graph = Graph()

    contracts_spot = {}
    for key, values in onetoken.contracts.items():
        if key in exchanges_spot['exchange'].values[:]:
            contracts_spot[key] = values

    print(contracts_spot)

    # okex_tickets = onetoken.get_quote_tickets('okex')
    # print(okex_tickets)

    for exchange,contracts in contracts_spot.items():
        tickets = onetoken.get_quote_tickets(exchange)
        print(tickets)

        #for contract in okex_contracts[:10]:
        for contract in contracts['name']:
            pair = contract.split( '.' )

            ask_price = tickets['ask_price'][tickets['contract'] == (exchange+'/'+contract )]
            bid_price = tickets['bid_price'][tickets['contract'] ==(exchange+'/'+contract ) ]

            if not pair[0] in graph.nodes.keys():
                graph.nodes[pair[0]] = Node(exchange, pair[0] )
            if not pair[1] in graph.nodes.keys():
                graph.nodes[pair[1]] = Node(exchange, pair[1])

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
            #print(newEdge0.df)

            dict1 = {
                'fro': pair[1],
                'to':  pair[0],
                'ask_price':1 / bid_price,
                'bid_price':1 / ask_price
            }
            newEdge1.df = pd.DataFrame(dict1)
            #print(newEdge1.df)
            graph.edges = pd.concat([graph.edges, newEdge0.df, newEdge1.df])

            contract_df0 = pd.DataFrame(newEdge0.df)
            #print(contract_df0)
            Node0.contract = pd.concat([Node0.contract,contract_df0])
            #print(Node0.contract)

            contract_df1 = pd.DataFrame(newEdge1.df)
            #print(contract_df1)
            Node1.contract = pd.concat([Node1.contract,contract_df1])
            #print(Node1.contract)

        for node in graph.nodes:
            #print(node)
            Node0 = graph.nodes[node]
            df = Node0.contract
            #print(df)

            fro = graph.edges[graph.edges['fro'].isin(df['to'])]
            Node0.mid = fro[fro['to'].isin(df['to'])]
            #print(Node0.mid)

            for to in df['to']:
                #print(to)
                path = pd.DataFrame()
                bid1 = Node0.mid[Node0.mid['fro']==to]
                path['to1_contract'] = bid1['to']
                path['to1_price'] = bid1['bid_price']

                bid0 = Node0.contract[Node0.contract['to'] == to]
                path['to0_contract'] = to
                path['fro_contract'] = node
                path['to0_price'] = bid0['bid_price'].values[0]
                #print(path)

                fros = bid1['to'].values[:]
                #print(fros)
                #print(Node0.contract.fro.isin(fros))
                bid2 = Node0.contract[Node0.contract.to.isin(fros)]
                temp = bid2
                temp['to2_price'] = 1 / bid2['ask_price'].values[:]
                temp['to2_contract'] = node
                path = pd.merge(path,temp[['to','to2_contract','ask_price','to2_price']],left_on='to1_contract',right_on = 'to')
                #print(path)

                graph.path = pd.concat([graph.path,path])

            commition = 0.0003
            graph.path['value'] = graph.path['to0_price'] * graph.path['to1_price'] * graph.path['to2_price'] * math.pow((1 - commition), 3)
            #print('debug')


        profit = graph.path[graph.path['value']>1]
        profit['profit'] = profit['value'] -1
        profit = profit[['fro_contract','to0_contract','to1_contract','value','profit']].sort_values(by = ['value'],ascending=[False])
        print(profit)
        print( 'End' )


if __name__ == '__main__':
    demo()