from basics import topbits_coverages, print_json
from TransKlauseEngine import TxEngine
from vk12mgr import VK12Manager


class Node12:
    def __init__(self, val, parent, vk12m):
        self.val = val
        self.parent = parent
        self.vk12m = vk12m
        self.nov = vk12m.nov
        self.name = f'{self.nov}-{val}'
        self.psats = []  # list of partial sats
        self.state = 0
        self.nexts = []

    def spawn(self):
        if self.vk12m.need_tx():
            self.tx = TxEngine(self.vk12m.bvk, self.nov)
            vk12m = self.vk12m.txed_clone(self.tx)
        else:
            vk12m = self.vk12m.clone()
        cutn = vk12m.bvk.nob
        self.topbits = list(range(self.nov - 1, self.nov - 1 - cutn, -1))
        cvr, dummy = topbits_coverages(vk12m.bvk, self.topbits)
        chdic = vk12m.morph(self.topbits, cvr[0])
        if chdic == None:
            self.state = 1
        elif len(chdic) == 0:
            self.state = 2
        else:
            for val, vkm in chdic.items():
                self.nexts.append(Node12(val, self, vkm))
        noc = len(self.nexts)
        print(f'{self.name} has {noc} children.')
        return self.nexts
