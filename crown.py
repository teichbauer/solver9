from TransKlauseEngine import TxEngine


class Crown:
    def __init__(self, parent, vk1dic, vk2dic, nov):
        self.parent = parent
        self.vk1dic = vk1dic
        self.vk2dic = vk2dic
        self.nov = nov

    def simplify(self):
        ''' 1. among vk1s, if 2 bit on the same bit, one has
                a. opposite value -> this crown dies (return False)
                b. the same value -> get rid of one
            2. for each vk1, loop vk2s, if it has a bit of vk1, and same value,
               then this vk2 is over-shadowed, and can be removed
            '''
        kn1s = list(self.vk1dic.keys())
        kn2s = list(self.vk2dic.keys())
        bestvk = self.vk2dic[kn2s[0]]
        if len(kn1s) > 0:
            ind = 0
            while ind < len(kn1s) - 1:
                vk = self.vk1dic[kn1s[ind]]
                i = ind + 1
                while i < len(kn1s):
                    vkx = self.vk1dic[kn1s[i]]
                    if vk.bits == vkx.bits:
                        if vk.dic[vk.bits[0]] == vkx.dic[vks.bits[0]]:
                            kn1s.remove(i)
                        else:
                            return False
                    else:
                        i += 1
                ind += 1
            # see if a vk1 over-shadow a vk2
            # also count how many vk2 touched by a vk1
            # pick the vk1 that has most touches
            max_touch_cnt = 0
            for kn1 in kn1s:
                vk = self.vk1dic[kn1]
                touch_cnt = 0
                ind = 0
                while ind < len(kn2s):
                    vk2 = self.vk2dic[kn2s[ind]]
                    for b in vk2.bits:
                        if b == vk.bits[0]:
                            if vk2.dic[b] == vk.dic[b]:
                                kn2s.pop(ind)
                                continue
                            else:
                                touch_cnt += 1
                    ind += 1
                if touch_cnt > max_touch_cnt:
                    max_touch_cnt = touch_cnt
                    bestvk = vk
        #
        # no vk1 exits
        # if any kn got removed, pop out vk from vk1dic or vk2dic
        if len(kn1s) != len(self.vk1dic):
            xkn1s = list(self.vk1dic.keys())
            for k in xkn1s:
                if k not in kn1s:
                    self.vk1dic.pop(k)

        if len(kn2s) != len(self.vk2dic):
            xkn2s = list(self.vk2dic.keys())
            for k in xkn2s:
                if k not in kn2s:
                    self.vk2dic.pop(k)

        return bestvk

    def bestchoice(self):
        if len(self.vk1dic) > 0:
            return list(self.vk1dic.values())[0]
        else:
            return list(self.vk2dic.values())[0]

    def transfer_clone(self, base_vk):
        tx = TxEngine(base_vk, self.nov)
        vk1dic = tx.trans_vkdic(self.vk1dic)
        vk2dic = tx.trans_vkdic(self.vk2dic)
        return Crown(self.parent, vk1dic, vk2dic, self.nov)

    def spawn(self):
        bvk = self.bestchoice()
        txed = self.transfer_clone(bvk)
