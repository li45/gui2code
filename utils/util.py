import json
import zipfile
import jsonpath as jp


class NodeTree():
    # JSON
    jsonTree = None
    # 节点树
    nodeTree = {}
    # 节点列表
    nodeList = []

    def __init__(self) -> None:
        pass

    def loadFromZip(self, file, parse=True):
        with zipfile.ZipFile(file) as zip:
            for f in zip.filelist:
                if f.filename.startswith("pages/"):
                    with zip.open(f.filename) as page_file:
                        self.jsonTree = json.load(page_file)
                    if parse:
                        board = self.findBoard(self.jsonTree)
                        self.parse(board)

    # 保存JSON
    def saveJsonTree(self, file):
        with open(file, 'w') as f:
            f.write(json.dumps(self.jsonTree))

    # 获取画板
    def findBoard(self, root):
        if not root:
            return
        if root['_class'] == 'artboard':
            return root

        childs = root.get('layers')
        for i in childs:
            node = self.findBoard(i)
            if node:
                return node
        return

        # 解析JSON

    def parse(self, node, parent=None):
        if not self.isVisibe(node):
            if parent:
                parent['layers'].remove(node)
            return

        if not self.isLeaf(node):
            allNodes = []
            for i in node['layers']:
                allNodes.append(i)
            allNodes[1]

        pass

    # 是否叶子节点
    def isLeaf(self, node):
        if str(node['name']).startswith("#"):
            return True
        if not node.get('layers'):
            return True
        if str(node['_class']) == "shapeGroup":
            return True
        return node and node.get('layers') and len(node.get('layers')) == 0

    # 是否已处理
    def isParsed(self, node):
        if node.get('parsed'):
            return True
        return True

    # 是否可见
    def isVisibe(self, node):
        if not node:
            return False
        if jp.jsonpath(node, '$.style.contextSettings.opacity')[0] == 0:
            return False
        if not node['isVisible']:
            return False
        return True

    pass

    def compareSize(self, node1, node2):
        n1 = node1['frame']
        n2 = node2['frame']

        n1Size = n1['width'] * n1['height']
        n2Size = n2['width'] * n2['height']

        if n1Size > n2Size:
            return 1
        elif n1Size < n2Size:
            return -1
        else:
            if n1['width'] > n2['width']:
                return 1
            return 0

    def sutable(self, node1, node2):
        n1 = node1['frame']
        n2 = node2['frame']

        n1x = (n1['x'], n1['x'] + n1['width'])
        n1y = (n1['y'], n1['y'] + n1['height'])
        n2x = (n2['x'], n2['x'] + n2['width'])
        n2y = (n2['y'], n2['y'] + n2['height'])

        return n2x[1] <= n1x[1] and n2x[2] >= n1x[2] and n2y[1] <= n1y[1] and n2y[2] >= n1y[2]

    def takeMinNode(self, nodeList):
        if len(nodeList) == 0:
            return None
        if len(nodeList) == 1:
            min = nodeList[0]
            nodeList.remove(min)

        min = nodeList[0]
        for node in nodeList[1:]:
            if self.compareSize(min, node) > 0:
                min = node
        nodeList.remove(min)
        return min

    def getAllParent(self, node):
        allParent = []
        for cp in self.nodeList:
            if self.sutable(node, cp):
                allParent.append(cp)

    def convertToNodeTree(self):
        min = self.takeMinNode(self.nodeList)
        if min:
            cas = self.getAllParent(min)
            ca = self.takeMinNode(cas)
            ca['layers'].append(min)
        pass


nodeTree = NodeTree()
nodeTree.loadFromZip('/Users/lichao/Desktop/g.sketch')
nodeTree.saveJsonTree('/Users/lichao/Desktop/g.json')
print(len(nodeTree.nodeList))


# 加载页面
def loadFileAsJson(name):
    with open(name, 'r') as page_file:
        return json.load(page_file)


# 是否可以成为容器
def isContainer(node):
    if str(node['class']) not in ["text"]:
        return True


# 是否底层容器
def printLeafGroup(node):
    if not node['isVisible']:
        return
    if isLeaf(node):
        return True
    else:
        childs = node['layers']
        isLeafGroup = True
        for i in range(len(childs)):
            leafGroup = printLeafGroup(childs[i])
            if not leafGroup:
                isLeafGroup = False
                continue
        if isLeafGroup:
            print("leaf", node["_class"], node["name"], node["do_objectID"])


def isGroup(node):
    if str(node['_class']) == "group":
        return True
    if str(node['_class']) == "artboard":
        return True
    return False


def printNode(base, node, ax, isLeaf, level):
    x = max(node['frame']['x'], 0)
    y = max(node['frame']['y'], 0)
    w = min(node['frame']['width'], base[2])
    h = min(node['frame']['height'], base[3])

    print(node['name'], node['_class'], x, ",", y, ",", w, ",", h, "base:", base[0], ",", base[1], "level:", level)

    edgecolor = 'r'
    if node['_class'] == 'text':
        edgecolor = 'b'

    rect = patches.Rectangle((base[0] + x, base[1] + y), w, h, linewidth=0.5, edgecolor=edgecolor, facecolor=None)
    ax.add_patch(rect)

