import requests
import itertools
import pandas as pd
from sync_api.demo_public import OneToken
# 图的节点结构
class Node:
    def __init__(self, exchange,name):
        self.exchange = exchange
        self.name = name      # 节点值

        self.come= {}      #入节点，边：dict:名称:节点，边 ,入度
        self.out = {}      #出节点，边：dict:名称:节点，边 ,入度
        self.come['count'] = 0
        self.out['count'] = 0




# 图的边结构
class Edge:
    def __init__(self,fro, to ,rate):
        self.fro = fro              # 边的from节点
        self.to = to                # 边的to节点

        self.rate = rate


def get_price(contract):
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
        self.edges = {}    # 图的边集合


# 生成图结构
# matrix = [
#   [1,2,3],        ==>   里面分别代表权重, from节点, to节点
#   [...]
# ]

'''
def createGraph(matrix):
    graph = Graph()
    for edge in matrix:
        weight = edge[0]
        fro = edge[1]
        to = edge[2]
        if fro not in graph.nodes:
            graph.nodes[fro] = Node(fro)
        if to not in graph.nodes:
            graph.nodes[to] = Node(to)
        fromNode = graph.nodes[fro]
        toNode = graph.nodes[to]
        newEdge = Edge(weight, fromNode, toNode)
        fromNode.nexts.append(toNode)
        fromNode.out += 1
        toNode.come += 1
        fromNode.edges.append(newEdge)
        graph.edges.append(newEdge)
    return graph
'''
def createGraph():
    pass

def demo():
    DEBUG = True
    onetoken = OneToken()

    exchange = onetoken.exchanges
    okex_contracts = onetoken.contracts['okex']['name']

    #contracts = ['eos.usdt', 'eos.usdk', 'usdt.usdk','eos.btc']

    graph = Graph()

    for contract in okex_contracts:
        pair = contract.split( '.' )
        bid, ask = get_price( contract )
        print('contract:{},bid:{},ask:{}'.format(contract,bid,ask))
        rates = {}
        rates['{}.{}'.format( pair[0], pair[1] )] = bid * (1 - 0.00002)
        rates['{}.{}'.format( pair[1], pair[0] )] = 1 / ask * (1 - 0.00002)

        graph.nodes[pair[0]] = Node('okex', pair[0] )
        graph.nodes[pair[1]] = Node( 'okex',pair[1] )

        Node1 = graph.nodes[pair[0]]
        Node2 = graph.nodes[pair[1]]


        for edge in itertools.permutations( pair, 2 ):
            Node0 = graph.nodes[edge[0]]
            Node1 = graph.nodes[edge[1]]
            rate = rates['{}.{}'.format(edge[0], edge[1])]

            newEdge = Edge( Node0, Node1, rate )

            Node0.out[edge[1]] = {}
            Node0.out[edge[1]]['node'] = Node1
            Node0.out[edge[1]]['rate'] = rate
            Node0.out[edge[1]]['edge'] = newEdge
            Node0.out['count'] +=1

            Node1.come[edge[0]] = {}
            Node1.come[edge[0]]['node'] = Node0
            Node1.come[edge[0]]['edge'] = newEdge
            Node1.come['count'] +=1

            graph.edges[edge[0], edge[1]] = ( newEdge )

    print( 'End' )


if __name__ == '__main__':
    demo()