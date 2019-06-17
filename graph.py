import requests
import itertools
import pandas as pd
# 图的节点结构
class Node:
    def __init__(self, quote):
        self.quote = quote      # 节点值

        self.come = 0           # 节点入度
        self.out = 0            # 节点出度
        self.nexts = []         # 节点的邻居节点
        self.edges = []         # 在节点为from的情况下，边的集合



# 图的边结构
class Edge:
    def __init__(self,fro, to,contract,invert):
        self.weight = weight        # 边的权重
        self.fro = fro              # 边的from节点
        self.to = to                # 边的to节点

        self.contract = contract
        self.invert = invert

        self.taker_commition = 0.0002 #吃单手续费
        self.maker_commition = 0.0001 #挂单手续费

        self.price = None

        self.value = None


    def get_price(self):
        res = requests.get( 'https://1token.trade/api/v1/quote/single-tick/okex/{}'.format(self.contract) )
        print(res.json())

        df = pd.DataFrame()


        if not self.invert:
            self.price = res.json()['bids'][0]['price']
        else:
            self.price = 1 / res.json()['asks'][0]['price']

        self.value = self.price * (1 - self.taker_commition)

# 图结构
class Graph:
    def __init__(self):
        self.nodes = {}     # 图的所有节点集合  字典形式：{节点编号：节点}
        self.edges = {}     # 图的边集合


# 生成图结构
# matrix = [
#   [1,2,3],        ==>   里面分别代表权重, from节点, to节点
#   [...]
# ]

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

if __name__ == '__main__':
    DEBUG = True
    exchange = ['okex',]
    nodes = ['eos','btc']
    currency = ['usdt','usdk']
    contracts = ['eos.usdt', 'eos.usdk', 'usdt.usdk']

    print('nodes:',nodes)
    print('contracts:',contracts)


    pairs = {}
    for contract in contracts:
        pairs[contract] = contract.split('.')
    #print('pairs:',pairs)
    #print(pairs.values())

    graph = Graph()

    for node in nodes:
        graph.nodes[node] = Node(node)

    '''
    product 笛卡尔积　　（有放回抽样排列）

    permutations 排列　　（不放回抽样排列）
    
    combinations 组合,没有重复　　（不放回抽样组合）
    
    combinations_with_replacement 组合,有重复　　（有放回抽样组合）
    '''
    for edge in itertools.permutations( nodes, 2 ):
        #print('edge:',edge)
        fro = edge[0]
        to = edge[1]
        #print(fro,to)
        if [fro,to] in pairs.values():
            weight = 1
            contract = list(pairs.keys())[list(pairs.values()).index([fro,to])]
            invert = False

        elif [to,fro] in pairs.values():
            weight = 1
            contract = list( pairs.keys() )[list( pairs.values() ).index( [to, fro] )]
            invert = True

        else:
            weight = 0
            contract = None
            invert = None

        #print('fro:{},to:{},weight:{},contract:{},invert:{}'.format(fro,to,weight,contract,invert))

        if weight == 1:
            fromNode = graph.nodes[fro]
            toNode = graph.nodes[to]

            newEdge = Edge( fromNode, toNode,contract,invert )
            fromNode.nexts.append( toNode )
            fromNode.out += 1
            toNode.come += 1
            fromNode.edges.append( newEdge )
            graph.edges[fro,to] =  newEdge

    markets = {}
    markets_df = pd.DataFrame()
    for edge in graph.edges.keys():
        graph.edges[edge].get_price()

        # print(graph.edges[edge].fro.quote , graph.edges[edge].to.quote,
        #       graph.edges[edge].price,graph.edges[edge].value)

        markets[edge] = graph.edges[edge].value

        df = pd.DataFrame(graph.edges[edge].value,index= [edge[0]],columns=[edge[1]])
        print(df)
        markets_df.join(df,how='outer')

    print(markets)
    print(markets_df)

    usdt_eos = graph.edges['usdt','eos'].value

    print(usdt_eos)


    #todo: 用DataFrame表达 报价
    #todo: 图的遍利


    print('End')