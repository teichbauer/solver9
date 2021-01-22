from basics import print_json, merge_sats
from TransKlauseEngine import TxEngine
from vk12mgr import VK12Manager
from basics import topbits
from satholder import SatHolder


class Node12:
    def __init__(self, vname, parent, vk12m, sh):
        self.parent = parent
        self.vk12m = vk12m
        self.sh = sh
        self.nov = vk12m.nov
        # vname is 2 ditigs number. vname % 10 is the given val
        self.vname = vname    # vname // 10: is the parent-nob

        # child_satdic for next-level children:
        # {<node-name>: <sat-dic>, ..}
        self.child_satdic = {}

        self.sats = {}
        self.state = 0
        self.nexts = []
        if self.nov == 3:
            self.sats = self.nov3_sats()

    def name(self):
        return f'{self.nov}.{self.vname}'

    def collect_sats(self):
        node = self
        parent = node.parent
        sdic = node.sats.copy()
        while True:  # type(parent).__name__ == 'Node12':
            merge_sats(sdic, parent.child_satdic[node.vname])
            if type(parent).__name__ == 'Crown':
                break
            node = parent
            parent = parent.parent
        assert(type(parent).__name__ == 'Crown')
        merge_sats(sdic, parent.rootsats)
        print(f'{self.name()} finds sats: {sdic}')
        parent.csats.append((sdic, self.name()))
        self.state = 1

    def nov3_sats(self):   # when nov==3, collect integer-sats
        sats = []
        vkdic = self.vk12m.vkdic
        for i in range(8):  # 8 = 2**3
            hit = False
            for vk in vkdic.values():
                if vk.hit(i):
                    hit = True
                    break
            if not hit:
                sats.append(i)
        ln = len(sats)
        if ln == 0:
            self.state = -1
            self.suicide()
        else:
            for si in sats:
                merge_sats(self.sats, self.sh.get_sats(si))
            self.state = 2
            # self.suicide()
        return self.sats

    def spawn(self):
        # self.vk12m must have bvk
        assert(self.vk12m.bvk != None)
        nob = self.vk12m.bvk.nob    # nob can be 1 or 2
        name_base = nob * 10        # name_base: 10 or 20
        self.topbits = topbits(self.nov, nob)

        # what if > 1 bvks (nob==2), need cvs to be excluded in morph
        if self.vk12m.need_tx():
            self.tx = TxEngine(self.vk12m.bvk, self.nov)
            self.sh.transfer(self.tx)
            vk12m = self.vk12m.txed_clone(self.tx)
        else:
            vk12m = self.vk12m.clone()
        chdic = vk12m.morph(self.topbits)  # , self.vk12m.bvk_cvs)
        shtail = self.sh.spawn_tail(nob)
        new_sh = SatHolder(shtail)
        self.sh.cut_tail(nob)

        if len(chdic) == 0:
            self.sats = self.sh.full_sats()
            self.state = 1  #
            # return []
        else:
            for val, vkm in chdic.items():
                node = Node12(
                    name_base + val,  # %10 -> val, //10 -> nob
                    self,             # node's parent
                    vkm,              # vk12m for node
                    new_sh.clone())   # sh is a clone: for sh.varray is a ref
                if node.state != -1:
                    self.child_satdic[node.vname] = self.sh.get_sats(val)
                if node.state == 0:
                    self.nexts.append(node)
                elif node.state == 2:
                    node.collect_sats()  # this will set state = 1
        return self.nexts

    def suicide(self):
        print(f'{self.name} destroyed.')
        i = 0
        while i < len(self.parent.next()):
            if self.parent.next[i].name == self.name:
                self.parent.next.pop(i)
                break
            else:
                i += 1
        if len(self.parent.next) == 0:
            self.parent.suicide()
