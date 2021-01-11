from basics import print_json
from TransKlauseEngine import TxEngine
from vk12mgr import VK12Manager
from basics import topvalue, topbits
from satholder import SatHolder


class Node12:
    def __init__(self, val, parent, vk12m, sh, ppsats):
        self.val = val
        self.parent = parent
        self.vk12m = vk12m
        self.sh = sh
        self.nov = vk12m.nov
        self.name = f'{self.nov}-{val}'
        self.ppsats = ppsats  # parent-partial-sat
        self.state = 0
        self.nexts = []

    def spawn(self):
        # self.vk12m must have bvk
        assert(self.vk12m.bvk != None)
        nob = self.vk12m.bvk.nob
        self.topbits = topbits(self.nov, nob)

        # what if > 1 bvks (nob==2), need cvs to be excluded in morph
        if self.vk12m.need_tx():
            self.tx = TxEngine(self.vk12m.bvk, self.nov)
            self.sh.transfer(self.tx)
            vk12m = self.vk12m.txed_clone(self.tx)
        else:
            vk12m = self.vk12m.clone()
        vk12m.bvk_cvs = self.vkm12m.bvk_cvs
        chdic = vk12m.morph(self.topbits)
        shtail = self.sh.spawn_tail(nob)
        new_sh = SatHolder(shtail)
        self.sh.cut_tail(nob)

        if chdic == None:
            self.state = 1
        elif len(chdic) == 0:
            self.state = 2
        else:
            for val, vkm in chdic.items():
                psats = self.sh.get_psats(val)
                node = Node12(val, self, vkm, new_sh.clone(), psats)
                self.nexts.append()
        noc = len(self.nexts)
        print(f'{self.name} has {noc} children.')
        return self.nexts
