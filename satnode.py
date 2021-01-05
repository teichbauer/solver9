from basics import topbits_coverages, print_json
from satholder import SatHolder
from TransKlauseEngine import TxEngine
from node12 import Node12
from vk12mgr import VK12Manager


class SatNode:
    def __init__(self, parent, sh, vkm):
        self.parent = parent
        self.sh = sh
        self.vkm = vkm
        self.nov = vkm.nov
        self.children = {}
        if self.nov == 3:
            self.sats = self.nov3()
        else:
            self.sats = None
        self.topbits = list(range(self.nov - 1, self.nov - 1 - 3, -1))
        if len(vkm.vkdic) == 0:
            self.sats = self.max_sats()

    def spawn(self):
        choice = self.vkm.bestchoice()
        self.bvk = self.vkm.vkdic[choice['bestkey'][0]]
        if self.topbits != self.bvk.bits:
            self.tx = TxEngine(self.bvk, self.nov)
            self.sh.transfer(self.tx)
            bvk_cv, dum = topbits_coverages(self.tx.vklause, self.topbits)
            vkm = self.vkm.txed_clone(self.tx)
        else:
            bvk_cv, dum = topbits_coverages(self.bvk, self.topbits)
            vkm = self.vkm

        crown_dic, self.vk12dic = vkm.morph(choice, self.topbits, bvk_cv[0])
        shtail = self.sh.spawn_tail(3)
        new_sh = SatHolder(shtail)
        self.sh.cut_tail(3)

        for val, cdic in crown_dic.items():
            vk12m = VK12Manager(cdic[1], cdic[2], vkm.nov)
            node = Node12(val, self, vk12m)
            self.children[val] = node

        vals = sorted(list(self.children.keys()))
        # for val in vals:
        #     self.children[val].spawn()
        best_child = self.digchild(self.children[vals.pop()])

        self.next = SatNode(self, new_sh, vkm)

        return self.next

    def digchild(self, ch):
        node = ch
        while node.state == 0:
            chs = node.spawn()
            if len(chs) == 0:
                break
            node = chs[0]
        return node

    def resolve(self, path):
        pass

    def nov3(self):
        return 7

    def max_sats(self):
        return 5
