from node12 import Node12

class Crown:
    def __init__(self, val, sh, psats, vk12m):
        self.sh = sh
        self.val = val
        self.psats = psats
        self.vk12m = vk12m
        self.node = Node12(val, self, vk12m, sh)


    