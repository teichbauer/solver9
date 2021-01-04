from basics import topbits_coverages, print_json
from TransKlauseEngine import TxEngine
from vk12mgr import VK12Manager


class Node12:
    def __init__(self, val, parent, vk12m):
        self.val = val
        self.parent = parent
        self.vk12m = vk12m
        self.nov = vk12m.nov
        self.children = {}

    def transfer_clone(self):
        tx = TxEngine(self.bvk, self.nov)
        vk12m = self.vk12m.txed_clone(tx)
        return Node12(self.val, self, vk12m)

    def spawn(self):
        txed_node = self.transfer_clone()
        cutn = self.bvk.nob
