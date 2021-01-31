from vklause import VKlause
from basics import topvalue, topbits, topbits_coverages


class VK12Manager:
    def __init__(self, vkdic, nov, callmbd=True, callsmp=True):
        ''' callop[0]: True/False call/not-call self.make_bdic()
            callop[1]: True/False call/not-call self.somplify()   '''
        self.nov = nov
        self.bdic = None
        self.vkdic = vkdic
        self.kn1s = [kn for kn, vk in vkdic.items() if vk.nob == 1]
        self.kn2s = [kn for kn, vk in vkdic.items() if vk.nob == 2]

        self.terminated = False  # no sat possible/total hit-blocked
        if callmbd:
            self.make_bdic()
        if callsmp:
            self.normalize()

    def clone(self):
        vkm = VK12Manager(self.vkdic.copy(),
                          self.nov,
                          False, False)  # no calls: make_bdic/normalize
        vkm.bdic = self.bdic.copy()
        return vkm

    def make_bdic(self):
        self.bdic = {b: set([]) for b in range(self.nov)}
        for kn, vk in self.vkdic.items():
            for b in vk.dic:
                self.bdic[b].add(kn)

    def txed_clone(self, tx):
        vkdic = tx.trans_vkdic(self.vkdic)
        # make a new vk12m call make_bdic, but not normalize
        vk12m = VK12Manager(vkdic, self.nov, True, False)
        return vk12m

    def need_tx(self):
        vk = self.bvk
        return topbits(self.nov, vk.nob) != vk.bits

    def highst_vk1(self):
        # pick a vk1 with bit on nov-1, if not exists, pick first vk1 as bvk
        hvk = None
        for kn in self.kn1s:
            vk = self.vkdic[kn]
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

        n = len(self.kn2s)
        choices = {}
        for kn in self.kn2s:
            vk = self.vkdic[kn]
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
        # bvk is a tuple. But only first kv in it is returned
        return bvk
    # end of --- def best_vk2(self):

    def _remove_vk(self, vk):
        if self.bdic:
            for b in vk.bits:
                if vk.kname in self.bdic[b]:
                    self.bdic[b].remove(vk.kname)
        if vk.nob == 1:
            self.kn1s.remove(vk.kname)
        elif vk.nob == 2:
            self.kn2s.remove(vk.kname)
        self.vkdic.pop(vk.kname, None)

    def clean_vk1s(self):
        ''' 1. test if 2 opposite vk1s (same bit/opposite value): 
                if True terminated = True
            2. if 2 vk1s have same bit, same value, remove that one vk1 '''
        i = 0
        while i < (len(self.kn1s) - 1):
            vk = self.vkdic[self.kn1s[i]]
            j = i + 1
            while j < len(self.kn1s):
                vkx = self.vkdic[self.kn1s[j]]
                if vkx.bits[0] == vk.bits[0]:
                    if vkx.dic[vkx.bits[0]] == vk.dic[vk.bits[0]]:
                        self._remove_vk(vkx)
                    else:
                        self.terminated = True
                        return None
                else:
                    j += 1
            i += 1
        # pick a vk1 with bit@(nov-1) as bvk, if exists.
        # may be replaced by better choice in normalize
        self.bvk = self.highst_vk1()
        return self.kn1s

    def normalize(self):
        ''' if len(vk1s) > 0
               pick a vk1 as self.bvk: the one with most touch of vk2s;
            if no vk1 exists, pick the best vk2 as bvk by self.best_vk2() '''
        if len(self.kn1s) > 0:
            if self.clean_vk1s() == None:  # terminated
                return
            maxtouch_cnt = 0
            for k1 in self.kn1s:
                v1 = self.vkdic[k1]
                bit = v1.bits[0]
                touch_cnt = 0
                kns = self.bdic[bit].copy()
                for k in kns:
                    if k in self.kn2s:
                        if self.vkdic[k].dic[bit] == v1.dic[bit]:
                            # vk2 is over-shadowed by v1. remove it
                            self._remove_vk(self.vkdic[k])
                        else:
                            # vk2 with opposite bit-value: count as a touch
                            touch_cnt += 1
                if touch_cnt > maxtouch_cnt:
                    maxtouch_cnt = touch_cnt
                    # pick a better vk1 as bvk
                    if self.bvk.kname != k1:
                        self.bvk = v1
        elif len(self.kn2s) > 0:
            # no vk1 exists - pick the best vk2 as bvk. can be multiple.
            bvk_cvs = set([])   # collect all covered-values
            kns = self.best_vk2()
            self.bvk = self.vkdic[kns[0]]
            for kn in kns:
                vk = self.vkdic[kn]
                bvk_cvs.add(topvalue(vk))
            if len(bvk_cvs) == 4:  # if all 4 values are covered: done
                self.terminated = True
        else:  # no vk at all
            self.terminated = True

    def morph(self, topbits):
        chdic = {}
        L = len(topbits)
        self.nov -= L
        excl_cvs = set([])

        tdic = {}
        kns = list(self.vkdic.keys())
        for kn in kns:
            vk = self.vkdic[kn]
            cvr, odic = topbits_coverages(vk, topbits)
            if len(odic) == 0:
                for v in cvr:
                    excl_cvs.add(v)
            else:
                tdic.setdefault(tuple(cvr), []).append(
                    VKlause(kn, odic, self.nov)
                )
        for val in range(2 ** L):
            if val in excl_cvs:
                continue
            vkd = {}
            for cvr in tdic:
                if val in cvr:
                    vks = tdic[cvr]
                    for vk in vks:
                        vkd[vk.kname] = vk
            if len(vkd) == 0:
                chdic[val] = None
            else:
                vkm = VK12Manager(vkd, self.nov)
                if not vkm.terminated:
                    chdic[val] = vkm

        return chdic
