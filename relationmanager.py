class RelationManager:
    def __init__(self, bitdic):
        self.orig_bitdic = bitdic
        self.init_vkdic = {kn: vk.clone() for kn, vk in bitdic.vkdic.items()}
        self.kns = list(self.init_vkdic.keys())
        self.bdic = {b: lst[:] for b, lst in bitdic.dic.items()}
        self.reldic = {}
        for kn in self.kns:
            self.reldic[kn] = {}
            for b in self.init_vkdic[kn].bits:
                self.reldic[kn][b] = set(bitdic.dic[b])
        # 3 lists for 3-/2-/1-share
        # each list-element:((total-shre-kns),(touched-kns)
        # for 1-share list, only 1 kns-tuple as list-element: [(),(),..]
        self.shdic = {  # each dic-value:
            3: {},  # ([kns sharing 3 bits],[kns touched at least 1 bit of 3])
                    # keyed by tuple([kns sharing 3 bits])
            2: {},  # ([kns sharing 2 bits],[kns touched at least 1 bit of 2])
                    # keyed by tuple([kns sharing 2 bits])
            1: {}   # [kns sharing the 1 bit], keyed by nk of vk1
        }
        # at beginning, every vk is 3-bit vk (called vk3)
        self.make_shdic(self.kns, True)
        x = 1

    def make_shdic(self, kns, initial=False):
        ''' making entries in self.shdic for every kn in kns.
            if initial==True, it is self.kns, and len(bs) == 3 for all
            '''
        for kn in kns:
            # pop a value of sh_sets: a set of kns
            if initial:
                bs = set(self.init_vkdic[kn].bits)
            else:
                bs = set(self.reldic[kn].keys())
            bs0 = bs.copy()

            if len(bs) == 1:
                b = bs.pop()
                tsvk = self.reldic[kn][b]
                tcvk = tsvk.copy()
            else:
                b0 = bs.pop()
                tsvk = self.reldic[kn][b0]
                tcvk = tsvk.copy()
                for b in bs:
                    s = self.reldic[kn][b]
                    tsvk = tsvk.intersection(s)
                    tcvk = tcvk.union(s)
            removal = set([])
            for k in tsvk:
                if k != kn and len(bs0) != len(self.reldic[k].keys()):
                    removal.add(k)
            if len(removal) > 0:
                tsvk = tsvk - removal

            # ( {<share-all>}, {<share-any>} )
            # {<share-all>}: set of kname: vk shares all kn's bits
            #      all vk in here must have <nob> bits
            # {<share-any>}: knames of vk sharing at least 1 bit with kn
            #       it is super-set of tsvk
            tpl = (tsvk, tcvk - tsvk, bs0)
            key = tuple(sorted(list(tsvk)))
            if key not in self.shdic[len(bs0)]:
                self.shdic[len(bs0)][key] = tpl

    def best_choice(self, nob):
        ''' Among shdic[nob], pick the best lelement - pair, keyed by tuple, of 
            (total-share-kns):([total-share-kns],[touched kns]).
            return the key and the pair
            '''
        # find keys with max-length - there may be multiple of them
        # put them into max_keys list
        keys = self.shdic[nob].keys()
        max_leng = 0
        max_keys = []
        for k in keys:
            if len(max_keys) == 0:
                max_keys.append(k)
            else:
                leng = len(k)
                if leng < max_leng:
                    continue
                if leng > max_leng:
                    max_leng = leng
                    max_keys = [k]
                max_keys.append(k)
        if len(max_keys) == 1:
            # only one best key, return the pair keyed by this key
            return self.shdic[nob][max_keys[0]]
        else:
            # among the keys with the same length, find the one
            # with longst pair[1] (kn-list of vks touched by key-kn(s))
            lst_leng = len(max_keys)
            max_leng = len(self.shdic[nob][max_keys[0]])
            index = 0
            for i in range(1, lst_leng - 1):
                leng = len(self.shdic[nob][max_keys[i]][1])
                if leng > max_leng:
                    index = i
                    max_leng = leng
            bestkey = max_keys[index]
            touched = self.shdic[nob][bestkey][1]
            bits = self.shdic[nob][bestkey][2]

            # debug
            for kn, d in self.reldic.items():
                if kn in touched:
                    bs = set(self.reldic[kn].keys())
                    inbits = bs.intersection(bits)
                    outbits = bs - bits
                    print(f'{kn}-bits: in-bits: {inbits},  out-bits: {outbits}')

            return bestkey, touched, bits

    def remove_choice(self, bestkey,
                      touched,
                      k3bits):
        ''' bestkey: tuple of kns sharing all their bits on k3bits
            touched: other kns with bit(s) in, *-bit out of k3bits. Here
                     * may be 0,1,2
            k3bits:  the bits all kn in bestkey sit on and share: being cut
            ----------------------------------------------------------------
            1. remove the entry keyed by bestkay from shdic[length(bk3bits)]
            2. 
            2. update shdic: all touched vks become vk2/vk1
            '''
        # step 1
        self.shdic[len(k3bits)].pop(bestkey, None)
        for k3 in bestkey:
            self.kns.remove(k3)

        touched1 = touched.copy()

        for kn in touched:  # for a kn with at least 1 bit in k3bits
            bs = set(self.reldic[kn].keys())  # bits kn has
            nbs = len(bs)                     # how many bits
            cutbs = k3bits.intersection(bs)   # part inside of k3bits
            leftbs = list(bs - cutbs)         # part outside of k3bits

            # cut bit-entries in reldic[kn]: all bits inside k3bits
            for b in cutbs:
                self.reldic[kn].pop(b, None)

            knlen = len(leftbs)
            if knlen == 0:
                # kn has nothing left. delete it from reldic
                del self.reldic[kn]
                # delete it from self.kns
                self.kns.remove(kn)
                touched1.remove(kn)

            # nbs is original number of bits for kn. Among self.shdic[nbs]
            # any one-key with kn in it, will be removed

            # collect keys with kn in it
            touched_keys = []
            for key, tpl in self.shdic[nbs].items():
                if kn in key:
                    touched_keys.append(key)
            # remove them all
            for k in touched_keys:
                self.shdic[nbs].pop(k)

        self.make_shdic(touched1)
        x = 1

    def test(self):
        k3s, touched, bits = self.best_choice(3)
        self.remove_choice(k3s, touched, bits)

        while len(self.kns) > 0:
            # policy: prefer small
            if len(self.shdic[1]) > 0:
                ksx, touchedx, bitsx = self.best_choice(1)
                self.remove_choice(ksx, touchedx, bitsx)
            elif len(self.shdic[2]) > 0:
                ksx, touchedx, bitsx = self.best_choice(1)
                self.remove_choice(ksx, touchedx, bitsx)
            elif len(self.shdic[3]) > 0:
                ksx, touchedx, bitsx = self.best_choice(1)
                self.remove_choice(ksx, touchedx, bitsx)
            else:
                raise Exception("!!!")

            # policy: prefer big
            # if len(self.shdic[3]) > 0:
            #     ksx, touchedx, bitsx = self.best_choice(1)
            #     self.remove_choice(ksx, touchedx, bitsx)
            # elif len(self.shdic[2]) > 0:
            #     ksx, touchedx, bitsx = self.best_choice(1)
            #     self.remove_choice(ksx, touchedx, bitsx)
            # elif len(self.shdic[1]) > 0:
            #     ksx, touchedx, bitsx = self.best_choice(1)
            #     self.remove_choice(ksx, touchedx, bitsx)
            # else:
            #     raise Exception("!!!")

        # k3sa, toucheda, bitsa = self.best_choice(3)
        # self.remove_choice(k3sa, toucheda, bitsa)

        x = 1
