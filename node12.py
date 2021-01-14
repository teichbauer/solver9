from basics import print_json
from TransKlauseEngine import TxEngine
from vk12mgr import VK12Manager
from basics import topbits
from satholder import SatHolder


class Node12:
    def __init__(self, vname, parent, vk12m, sh, satdic):
        # self.val = val
        # self.psats = psats
        self.parent = parent
        self.vk12m = vk12m
        self.sh = sh
        self.nov = vk12m.nov
        # vname is 2 ditigs number. vname % 10 is the given val
        self.vname = vname  # vname // 10: is the parent-nob
        self.satdic = satdic
        self.sats = {}
        self.state = 0
        self.nexts = []
        if self.nov == 3:
            self.sats = self.nov3_sats()

    def name(self):
        return f'{self.nov}.{self.vname}'

    def collect_sats(self):
        parent = self.parent
        sdic = self.sats
        while type(parent).__name != 'SatNode':
            self.merge_sats(sdic, parent.sats)
            parent = self.parent
        self.satdic[self.name()] = sdic

    def merge_sats(self, dic0, dic1):
        # merge dic1 into dic0 - if a key has both 0 | 1, set its value = 2
        for k, v in dic1.items():
            if k in dic0:
                if dic0[k] != v:
                    dic0[k] = 2
            else:
                dic0[k] = v
        return dic0

    def nov3_sats(self):   # when nov==3, collect integer-sats
        sats = []
        vkdic = self.vk12m.union_vkdic()
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
                self.merge_sats(self.sats, self.sh.get_sats(si))
            self.collect_sats()
            self.state = 1
            # self.suicide()
        return sats

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
        chdic = vk12m.morph(self.topbits, self.vk12m.bvk_cvs)
        shtail = self.sh.spawn_tail(nob)
        new_sh = SatHolder(shtail)
        self.sh.cut_tail(nob)
        self.sats = self.sh.get_sats(self.vname % 10)  # get the given-val

        if len(chdic) == 0:
            self.sats = self.sh.full_sats()
            self.state = 1  #
            # return []
        else:
            for val, vkm in chdic.items():
                # psats = self.sh.get_sats(val)
                node = Node12(
                    name_base + val,  # %10 -> val, //10 -> nob
                    self,             # node's parent
                    vkm,              # vk12m for node
                    new_sh.clone(),   # sh is a clone: for sh.varray is a ref
                    self.satdic)      # crown.csats, for collected partial-sats
                # if node.state == 0:
                self.nexts.append(node)
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
