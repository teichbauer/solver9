from basics import topbits_coverages
from vklause import VKlause


class VK12Manager:
    def __init__(self, vk1dic, vk2dic, nov, callmbd=True, callsmp=True):
        ''' callop[0]: True/False call/not-call self.make_bdic()
            callop[1]: True/False call/not-call self.somplify()
            '''
        self.nov = nov
        self.vk1dic = vk1dic
        self.vk2dic = vk2dic
        self.terminated = False  # no sat possible/total hit-blocked
        if callmbd:
            self.make_bdic()
        if callsmp:
            self.simplify()

    def clone(self):
        vkm = VK12Manager(self.vk1dic.copy(), self.vk2dic.copy(), self.nov,
                          False, False)  # no calls: make_bdic/simplify
        vkm.bdic = self.bdic.copy()
        return vkm

    def make_bdic(self):
        d = self.vk1dic.copy()
        d.update(self.vk2dic)
        self.bdic = {b: set([]) for b in range(self.nov)}
        for kn, vk in d.items():
            for b in vk.dic:
                self.bdic[b].add(kn)

    def txed_clone(self, tx):
        vk1dic = tx.trans_vkdic(self.vk1dic)
        vk2dic = tx.trans_vkdic(self.vk2dic)
        # make a new vk12m call make_bdic, but not simplify
        vk12m = VK12Manager(vk1dic, vk2dic, self.nov, True, False)
        # take tx's vk as bvk, not the one picked by VK12Manager constructor
        vk12m.bvk = tx.vklause
        return vk12m

    def need_tx(self):
        vk = self.bvk
        tbs = list(range(self.nov-1, self.nov-1-vk.nob, -1))
        return tbs != vk.bits

    def highst_vk1(self):
        hvk = None
        for kn, vk in self.vk1dic.items():
            if vk.bits[0] == self.nov - 1:
                return vk
            elif hvk == None:
                hvk = vk
        return hvk

    def simplify(self):
        ''' A. len(vk1s) > 0
            1. test if 2 opposite vk1s (same bit/opposite value): 
                if True terminated = True
            2. if 2 vk1s have same bit, same value, remove that one vk1
            3. pick self.bvk: the one with most touch of vk2s;
               among the same touch-count, pick the one with bit == nov - 1
            B. len(vk1s) == 0, pick random 1 vk2 as bvk
            '''
        kn1s = list(self.vk1dic.keys())
        if len(kn1s) > 0:
            # pick first vk1 as bvk
            self.bvk = self.highst_vk1()
            maxtouch_cnt = 0
            while len(kn1s) > 0:
                k1 = kn1s.pop(0)
                v1 = self.vk1dic[k1]
                bit = v1.bits[0]
                # for loop may change its size, use a clone for looping
                knset = self.bdic[bit].copy()
                knset.remove(k1)
                touch_cnt = 0
                for k in knset:
                    if k in kn1s:
                        if self.vk1dic[k].dic[bit] == v1.dic[bit]:
                            kn1s.remove(k)
                            self.vk1dic.pop(k, None)
                            self.bdic[bit].remove(k)
                        else:  # a opposite vk1 -> total block
                            self.terminated = True
                            return
                    elif k in self.vk2dic:
                        if self.vk2dic[k].dic[bit] == v1.dic[bit]:
                            self.vk2dic.pop(k, None)
                            self.bdic[bit].remove(k)
                        else:
                            # vk2 with opposite bit-value: count as a touch
                            touch_cnt += 1
                if touch_cnt > maxtouch_cnt:
                    maxtouch_cnt = touch_cnt
                    # pick a better vk1 as bvk
                    if self.bvk.kname != k1:
                        self.bvk = v1
        else:
            # no vk1 exists - pick a vk2 as bvk
            self.bvk = list(self.vk2dic.values())[0]

    def morph(self, topbits, excl_cv):
        ln = len(topbits)
        chdic = {}
        nov = self.nov - ln

        vkdic = self.vk1dic.copy()
        vkdic.update(self.vk2dic)
        if len(vkdic) == 1:
            return None
        for c in range(2 ** ln):
            if c == excl_cv:
                continue
            vk1d = {}
            vk2d = {}
            for kn, vk in vkdic.items():
                v = vk.clone(topbits)
                if v:
                    if v.nob == 1:
                        vk1d[kn] = v
                    elif v.nob == 2:
                        vk2d[kn] = v
            if len(vk1d) == 0 and len(vk2d) == 0:
                return None
            # make a shortened vk12m, call both make_bdic/simplify
            chdic[c] = VK12Manager(vk1d, vk2d, nov)
        return chdic
