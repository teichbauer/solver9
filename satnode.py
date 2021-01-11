from basics import topbits_coverages, topvalue, topbits, print_json
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
        self.topbits = topbits(self.nov, 3)
        if len(vkm.vkdic) == 0:
            self.sats = self.max_sats()

    def spawn(self):
        choice = self.vkm.bestchoice()
        self.bvk = self.vkm.vkdic[choice['bestkey'][0]]
        if self.topbits != self.bvk.bits:
            self.tx = TxEngine(self.bvk, self.nov)
            self.sh.transfer(self.tx)
            vkm = self.vkm.txed_clone(self.tx)
        else:
            vkm = self.vkm

        excl_cvs = [topvalue(vkm.vkdic[kn]) for kn in choice['bestkey']]

        crown_dic = vkm.morph(choice, self.topbits, excl_cvs)
        shtail = self.sh.spawn_tail(3)
        new_sh = SatHolder(shtail)
        self.sh.cut_tail(3)

        vals = sorted(list(crown_dic.keys()))
        for val in vals:
            cdic = crown_dic[val]
        # for val, cdic in crown_dic.items():
            # call both make_bdic/normalize (def: both True)
            psats = self.sh.get_psats(val)
            vk12m = VK12Manager(cdic[1], cdic[2], vkm.nov)
            if not vk12m.terminated:
                node = Node12(val, self, vk12m, new_sh.clone(), psats)
                self.children[val] = node

        vals = sorted(list(self.children.keys()))
        for val in vals:
            self.digchild(self.children[val])

        self.next = SatNode(self, new_sh, vkm)

        return self.next

    def digchild(self, ch):
        node = ch
        while node.state == 0:
            chs = node.spawn()
            if len(chs) == 0:
                if node.state == 1:
                    print(f'{node.name} has sats:')
                    print(node.ppsats)
                elif node.state < 0:
                    print(f'{node.name} is dead')
                else:
                    print(f'{node.name} is weird')
            else:
                node = chs[0]
        return node

    def resolve(self, path):
        pass

    def nov3(self):
        return 7

    def max_sats(self):
        return 5
