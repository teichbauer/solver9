class RelationManager:
    def __init__(self, bitdic):
        self.bitdic = bitdic
        self.kns = list(bitdic.vkdic.keys())
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
        self.make_shlist(3, self.kns)

    def make_shlist(self, nob, candikns):
        for kn in candikns:
            vk = self.bitdic.vkdic[kn]
            # <nob>-many sets. each has kns sharing 1 bit of vk
            # {<bit>:<set of kns sharing this bit>,..}
            sh_sets = {}
            for b in vk.bits:
                sh_sets[b] = set(self.bitdic.dic[b])
            # pop a value of sh_sets: a set of kns
            tsvk = set(sh_sets.popitem()[1])
            tcvk = tsvk.copy()
            for s in sh_sets.values():
                tsvk = tsvk.intersection(s)
                tcvk = tcvk.union(s)

            # if a vk in tsvk with diff nob: remove it from tsvk
            # this is only possible when nob is 2 or 1
            if nob < 3:
                tmp = tsvk.copy()
                for k in tmp:
                    if self.vkdic[k].nob != nob:
                        tsvk.remove(k)

            # ( {<share-all>}, {<share-any>} )
            # {<share-all>}: set of kname: vk shares all kn's bits
            #      all vk in here must have <nob> bits
            # {<share-any>}: knames of vk sharing at least 1 bit with kn
            #       it is super-set of tsvk
            pair = (tsvk, tcvk)
            key = tuple(sorted(list(tsvk)))
            self.shdic[nob][key] = pair

    def best_pair(self, nob):
        # find keys with max-length - it may be multiple of them
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
            # if only one, return the pair keyed by this key
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
            return self.shdic[nob][max_keys[index]]

    def pop_best(self, nob, bestpair):
        pass
