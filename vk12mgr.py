from vklause import VKlause
from basics import topvalue, topbits


class VK12Manager:
    def __init__(self, vk1dic, vk2dic, nov, callmbd=True, callsmp=True):
        ''' callop[0]: True/False call/not-call self.make_bdic()
            callop[1]: True/False call/not-call self.somplify()   '''
        self.nov = nov
        self.bdic = None
        self.vk1dic = vk1dic
        self.vk2dic = vk2dic
        self.terminated = False  # no sat possible/total hit-blocked
        if callmbd:
            self.make_bdic()
        if callsmp:
            self.normalize()

    def clone(self):
        vkm = VK12Manager(self.vk1dic.copy(), self.vk2dic.copy(), self.nov,
                          False, False)  # no calls: make_bdic/normalize
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
        # make a new vk12m call make_bdic, but not normalize
        vk12m = VK12Manager(vk1dic, vk2dic, self.nov, True, False)
        return vk12m

    def need_tx(self):
        vk = self.bvk
        return topbits(self.nov, vk.nob) != vk.bits

    def highst_vk1(self):
        hvk = None
        for kn, vk in self.vk1dic.items():
            if vk.bits[0] == self.nov - 1:
                return vk
            elif hvk == None:
                hvk = vk
        return hvk

    def best_vk2(self):
        ''' 1. pick the one vk2 with most touches.
            2. if there are more than 1 on the same bits, return list of them 
            '''
        def ts_tc_vks(me, vk):
            # return a tuple (ts, tc), where ts is the kn of a vkx that sits
            # on the same 2 bits as vk does. tc is the kns vk touches
            # both ts, tc exclude vk.kname (vk itself)
            sh_sets = {}
            for b in vk.bits:
                s = self.bdic[b].copy()
                s.remove(vk.kname)
                sh_sets[b] = s
            ts = set(sh_sets.popitem()[1])  # [0] is bit, [1] is the set
            tc = ts.copy()
            for s in sh_sets.values():
                ts = ts.intersection(s)
                tc = tc.union(s)
            return ts, tc - ts

        kn2s = list(self.vk2dic.keys())
        n = len(kn2s)
        choices = {}
        for kn, vk in self.vk2dic.items():
            ts, tc = ts_tc_vks(self, vk)
            ts.add(kn)
            tp = tuple(sorted(list(ts)))
            choices[tp] = tc
        # choices = {kn: ts_tc_vks(self, vk) for kn, vk in self.vk2dic.items()}
        bvk = None
        for ts, tc in choices.items():
            if bvk == None:
                bvk = ts
                max_tsleng = len(ts)
                max_tcleng = len(tc)
            else:
                lns = len(ts)
                lnc = len(tc)
                if lns > max_tsleng:
                    bvk = ts
                    max_tsleng = lns
                    max_tcleng = lnc
                elif lns == max_tsleng:
                    if lnc > max_tcleng:
                        bvk = ts
                        max_tcleng = lnc
        return bvk
    # end of --- def best_vk2(self):

    def _remove_vk(self, vk):
        if self.bdic:
            for b in vk.bits:
                if vk.kname in self.bdic[b]:
                    self.bdic[b].remove(vk.kname)
        self.vk1dic.pop(vk.kname, None)
        self.vk2dic.pop(vk.kname, None)

    def normalize(self):
        ''' A. len(vk1s) > 0
            1. test if 2 opposite vk1s (same bit/opposite value): 
                if True terminated = True
            2. if 2 vk1s have same bit, same value, remove that one vk1
            3. pick self.bvk: the one with most touch of vk2s;
               among the same touch-count, pick the one with bit == nov - 1
            B. len(vk1s) == 0, pick the best vk2 as bvk   '''
        self.bvk_cvs = set([])
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
                            self._remove_vk(self.vk1dic[k])
                        else:  # a opposite vk1 -> total block
                            self.terminated = True
                            return
                    elif k in self.vk2dic:
                        if self.vk2dic[k].dic[bit] == v1.dic[bit]:
                            # vk2 is over-shadowed by v1. remove it
                            self._remove_vk(self.vk2dic[k])
                        else:
                            # vk2 with opposite bit-value: count as a touch
                            touch_cnt += 1
                if touch_cnt > maxtouch_cnt:
                    maxtouch_cnt = touch_cnt
                    # pick a better vk1 as bvk
                    if self.bvk.kname != k1:
                        self.bvk = v1
            self.bvk_cvs.add(topvalue(self.bvk))
        else:
            # no vk1 exists - pick the best vk2 as bvk. can be multiple.
            self.bvk = self.best_vk2()
            for kn in self.bvk:
                vk = self.vk2dic[kn]
                self.bvk_cvs.add(topvalue(vk))
            if len(self.bvk_cvs) == 4:
                self.terminated = True

    def morph(self, topbits):
        ln = len(topbits)
        chdic = {}
        nov = self.nov - ln

        vkdic = self.vk1dic.copy()
        vkdic.update(self.vk2dic)
        if len(vkdic) == 1:
            return None
        for c in range(2 ** ln):
            if c in self.bvk_cvs:
                continue
            vk1d = {}
            vk2d = {}
            for kn, vk in vkdic.items():
                v = vk.clone(topbits)
                if v:  # if all bits are gone/dropped: v==None -> drop v
                    if v.nob == 1:
                        vk1d[kn] = v
                    elif v.nob == 2:
                        vk2d[kn] = v
            if len(vk1d) == 0 and len(vk2d) == 0:
                return None
            # make a shortened vk12m, call both make_bdic/normalize
            chdic[c] = VK12Manager(vk1d, vk2d, nov)
        return chdic
