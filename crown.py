from node12 import Node12

class Crown:
    def __init__(self, val, sh, psats, vk12m):
        self.sh = sh
        self.val = val
        self.sats = psats
        self.csats = {}
        self.vk12m = vk12m
        self.node = Node12(30 + val, self, vk12m, sh, self.csats)
        self.done = False


    def dig_thru(self):
        nodes = [self.node]
        nexts = []
        while True:
            for node in nodes:
                if node.state == 0:
                    nexts += node.spawn()
            if len(next) == 0:
                break
            else:
                nodes = nexts
        self.done = True
        return self.sats