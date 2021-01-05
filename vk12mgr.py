from basics import topbits_coverages
from vklause import VKlause


class VK12Manager:
    def __init__(self, vk1dic, vk2dic, nov):
        self.nov = nov
        self.vk1dic = vk1dic
        self.vk2dic = vk2dic
        self.terminated = False  # no sat possible/total hit-blocked
        self.make_bdic()
        self.simplify()

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
        vk12m = VK12Manager(vk1dic, vk2dic, self.nov)
        # take tx's vk as bvk, not the one picked by VK12Manager constructor
        vk12m.bvk = tx.vklause
        return vk12m

    def highst_vk1(self):
        hvk = None
        for kn, vk in self.vk1dic.items():
            if vk.bits[0] == self.nov - 1:
                hvk = vk
            elif hvk == None:
                hvk = vk

    def simplify(self):
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
            chdic[c] = VK12Manager(vk1d, vk2d, nov)
        return chdic

    def chopped_clone(self, topbits):
        ''' make a new vk12mgr, with topbits chopped off:
            some of vk1s/vk2s vanish, some vk2s become vk1s
            '''
        nov = self.nov - len(topbits)
        kn1s = list(self.vk1dic.keys())
        kn2s = list(self.vk2dic.keys())
        vk1dic = {}
        vk2dic = {}
        for kn, vk in self.vk1dic.items():
            v = vk.clone(topbits)
            if v:
                vk1dic[kn] = v
        for kn, vk in self.vk2dic.items():
            v = vk.clone(topbits)
            if v:
                if v.nob == 1:
                    vk1dic[kn] = v
                elif v.nob == 2:
                    vk2dic[kn] = v
        vkm = VK12Manager(vk1dic, vk2dic, nov)
        return vkm
