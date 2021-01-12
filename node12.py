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
        if self.nov == 3:
            sats = self.nov3_sats()
            ln = len(sats)
            if ln > 0:
                self.collect_psat(sats)
                self.state = 1      # hit at least 1 psat
            else:
                self.state = -1     # no sat possible

    def collect_psat(self, sats):
        self.ppsats.update(self.sh.get_psats(sats[0]))
        if len(sats) > 1:
            for i in range(1, len(sats)):
                dic = self.sh.get_psats(sats[i])
                self.merge_sats(self.ppsats, dic)
        parent = self.parent
        while True:
            self.merge_sats(self.ppsats, parent.ppsats)
            parent = parent.parent
            if type(parent).__name__ == 'SatNode':
                break
            else:
                val = parent.val
        print(f"{val}/{self.name} finds psat: {self.ppsats}")
        # parent is a SatNode instance. Fill in sats2s[val]
        dic = parent.sats2s.setdefault(val, {})
        dic[self.name] = self.ppsats

    def merge_sats(self, dic0, dic1):
        # merge dic1 into dic0 - if a key has both 0 | 1, set its value = 2
        for k, v in dic1.items():
            if k in dic0:
                if dic0[k] != dic1[k]:
                    dic0[k] = 2
            else:
                dic0[k] = dic1[k]
        return dic0

    def nov3_sats(self):
        sats = []
        vkdic = self.vk12m.union_vkdic()
        for i in range(8):
            hit = False
            for vk in vkdic.values():
                if vk.hit(i):
                    hit = True
                    break
            if not hit:
                sats.append(i)
        return sats

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
        chdic = vk12m.morph(self.topbits, self.vk12m.bvk_cvs)
        shtail = self.sh.spawn_tail(nob)
        new_sh = SatHolder(shtail)
        self.sh.cut_tail(nob)

        if chdic == None:
            self.state = -1
        elif len(chdic) == 0:
            self.state = -2
        else:
            for val, vkm in chdic.items():
                psats = self.sh.get_psats(val)
                node = Node12(val, self, vkm, new_sh.clone(), psats)
                # if node.state == 0:
                self.nexts.append(node)
        return self.nexts

    def suicide(self):
        print(f'{self.name} destroyed.')
        if type(self.parent).__name__ == 'SatNode':
            self.parent.children.pop(self.val)
            return
        i = 0
        while i < len(self.parent.next()):
            if self.parent.next[i].name == self.name:
                self.parent.next.pop(i)
                break
            else:
                i += 1
        if len(self.parent.next) == 0:
            self.parent.suicide()
