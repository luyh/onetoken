import requests
import itertools

# 图的节点结构
class Node:
    def __init__(self, contract):
        self.contract = contract      # 节点值

        self.come = 0           # 节点入度
        self.out = 0            # 节点出度
        self.nexts = []         # 节点的邻居节点
        self.edges = []         # 在节点为from的情况下，边的集合

        self.buy1_price = None
        self.sell1_price = None

    def get_price(self):
        res = requests.get( 'https://1token.trade/api/v1/quote/single-tick/okex/{}'.format(self.contract) )
        self.sell1_price = res.json()['asks'][0]['price']
        self.buy1_price = res.json()['bids'][0]['price']

# 图的边结构
class Edge:
   def __init__(self,fro, to):
       #self.weight = weight        # 边的权重
       self.fro = fro              # 边的from节点
       self.to = to                # 边的to节点

# 图结构
class Graph:
    def __init__(self):
        self.nodes = {}     # 图的所有节点集合  字典形式：{节点编号：节点}
        self.edges = []     # 图的边集合


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

    quotes = ['eos','usdt','usdk']
    nodes = ['eos.usdt', 'eos.usdk', 'usdt.usdk']

    graph = Graph()

    for node in nodes:
        graph.nodes[node] = Node(node)
        graph.nodes[node].get_price()

        if DEBUG:
            pass
            #print(graph.nodes[node].buy1_price,graph.nodes[node].sell1_price)


    '''
    product 笛卡尔积　　（有放回抽样排列）

    permutations 排列　　（不放回抽样排列）
    
    combinations 组合,没有重复　　（不放回抽样组合）
    
    combinations_with_replacement 组合,有重复　　（有放回抽样组合）
    '''
    for edge in itertools.combinations( quotes, 2 ):
        print(edge)

    for edge in itertools.permutations( quotes, 2 ):
        print(edge)