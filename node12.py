from basics import topbits_coverages, print_json
from TransKlauseEngine import TxEngine
from vk12mgr import VK12Manager


class Node12:
    def __init__(self, val, parent, vk12m):
        self.val = val
        self.parent = parent
        self.vk12m = vk12m
        self.nov = vk12m.nov
        self.psats = []  # list of partial sats
        self.children = {}

    def transfer_clone(self):
        tx = TxEngine(self.bvk, self.nov)
        vk12m = self.vk12m.txed_clone(tx)
        return Node12(self.val, self, vk12m)

    def spawn(self):
        txed = self.transfer_clone()
        self.bvk = txed.vk12m.bvk
        cutn = self.bvk.nob
        self.topbits = list(range(self.nov - 1, self.nov - 1 - cutn, -1))
        cvr, dummy = topbits_coverages(self.bvk, self.topbits)
        chdic = txed.vk12m.morph(self.topbits, cvr[0])
        for val, vkm in chdic.items():
            self.children = Node12(val, self, vkm)
