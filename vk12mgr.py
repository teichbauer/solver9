class VK12Manager:
    def __init__(self, vk1dic, vk2dic, nov, initial=False):
        self.nov = nov
        self.vk1dic = vk1dic
        self.vk2dic = vk2dic
        self.done = False
        if initial:
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
        vk12m = VK12Manager(vk1dic, vk2dic, self.nov, True)
        return vk12m

    def simplify(self):
        kn1s = list(self.vk1dic.keys())
        if len(kn1s) > 0:
            # pick first vk1 as bvk
            self.bvk = list(self.vk1dic.values())[0]
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
                            self.done = True
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
