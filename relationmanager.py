class RelationManager:
    def __init__(self, bitdic):
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
        self.make_shdic()

    def make_shdic(self):
        for kn in self.kns:
            # pop a value of sh_sets: a set of kns
            bs = set(self.init_vkdic[kn].bits)
            b0 = bs.pop()
            tsvk = self.reldic[kn][b0]
            tcvk = tsvk.copy()
            for b in bs:
                s = self.reldic[kn][b]
                tsvk = tsvk.intersection(s)
                tcvk = tcvk.union(s)

            # ( {<share-all>}, {<share-any>} )
            # {<share-all>}: set of kname: vk shares all kn's bits
            #      all vk in here must have <nob> bits
            # {<share-any>}: knames of vk sharing at least 1 bit with kn
            #       it is super-set of tsvk
            pair = (tsvk, tcvk - tsvk)
            key = tuple(sorted(list(tsvk)))
            self.shdic[3][key] = pair

    def best_pair(self, nob):
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
            touched = self.shdic[nob][bestkey]
            return bestkey, touched

    def test(self):
        k3s, pair = self.best_pair(3)
        self.remove_choice(3, k3s, pair)
        x = 1

    def remove_choice(self, nob, bestkey, touched):
        ''' 1. remove the entry(key and value-pair) from shdic[nob]
            2. update shdic: all touched vks become vk2/vk1
            '''
        for k3 in bestkey:  # step 1
            self.shdic[nob].pop(k3, None)

        for kn in bestkey:  # key-kns with nob-bits,
            pass

        for kn in touched:
            pass
        x = 1
