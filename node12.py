from basics import print_json
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

    def get_topbits(self, n):
        t = self.nov - 1
        lst = []
        while n > 0:
            lst.append(t)
            t -= 1
            n -= 1
        return lst

    def spawn(self):
        # self.vk12m must have bvk
        assert(self.vk12m.bvk != None)

        cv = self.vk12m.bvk_topvalue()
        if self.vk12m.need_tx():
            self.tx = TxEngine(self.vk12m.bvk, self.nov)
            vk12m = self.vk12m.txed_clone(self.tx)
        else:
            vk12m = self.vk12m.clone()
        self.topbits = self.get_topbits(self.bvk.nob)
        chdic = vk12m.morph(self.topbits, cv)
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
