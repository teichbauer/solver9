from basics import topbits_coverages, print_json
from vklause import VKlause


class VKManager:
    def __init__(self, vkdic, nov, initial=False):
        self.vkdic = vkdic
        self.nov = nov
        if initial:
            self.make_bdic()

    def printjson(self, filename):
        print_json(self.nov, self.vkdic, filename)

    def make_bdic(self):
        self.bdic = {b: set([]) for b in range(self.nov)}
        for kn, vk in self.vkdic.items():
            for b in vk.dic:
                self.bdic[b].add(kn)

    def txed_clone(self, tx):
        vkdic = tx.trans_vkdic(self.vkdic)
        return VKManager(vkdic, self.nov)

    def morph(self, choice, topbits, excl_cvs):
        ''' only called on a txed clone '''
        crowns = {}  # {<cvr-val>: {kn, ..},..}
        self.nov -= 3
        for k3 in choice['bestkey']:
            self.vkdic.pop(k3, None)

        for kn in choice['touched']:  # for a kn with at least 1 bit in k3bits
            vk = self.vkdic.pop(kn, None)  # pop out this touched kn
            assert(vk.bits != topbits), f"{kn} shouldn't be total-share."

            cvr, odic = topbits_coverages(vk, topbits)
            if len(odic) > 0:  # if odic has no bit left, skip this vk
                vk12 = VKlause(kn, odic, self.nov)
                for cv in cvr:
                    if cv in excl_cvs:
                        continue
                    d = crowns.setdefault(cv, {})
                    if len(odic) == 1:
                        d.setdefault(1, {})[kn] = vk12
                    else:
                        d.setdefault(2, {})[kn] = vk12
        # now all vks in self.vkdic are vk3s
        # and have nov -= 3 that is the same as self.nov
        for vk in self.vkdic.values():
            vk.nov = self.nov
        # make bdic based on updated vkdic (popped out all touched)
        self.make_bdic()    # make the bdic for self.vkdic - all 3-bit vks
        return crowns

    def bestchoice(self):
        ''' return: {(kn1,kn2): set([tkn1, tkn2,..]),'bits': bits}
            (kn1,kn2) are the vks (with kn1, kn2 names) sit on same *.bits,
            bits: the 3 bits kn1 and kn2 commonly sit on
            set([tkn1,..]): set of kns/vks that have 1 or 2 bit(s) in bits
            '''
        best_choice = None
        max_tsleng = -1
        max_tcleng = -1
        best_bits = None
        for kn, vk in self.vkdic.items():
            if best_choice and kn in best_choice[0]:
                continue
            # 3 sets. each has kns sharing 1 bit of vk
            # {<bit>:<set of kns sharing this bit>,..}
            sh_sets = {}  # dict keyed by bit, value is a set of kns on the bit
            bits = vk.bits
            for b in bits:
                sh_sets[b] = self.bdic[b].copy()
            # dict.popitem() pops a tuple: (<key>,<value>) from dict
            tsvk = sh_sets.popitem()[1]  # [0] is bit, [1] is the set
            tcvk = tsvk.copy()
            for s in sh_sets.values():
                tsvk = tsvk.intersection(s)
                tcvk = tcvk.union(s)

            # chc is a tuple of 2 sets: ( {<share-all>}, {<share-any>} )
            # {<share-all>}: set of kname: of vks shares all kn's bits
            #      all vk in here must share every bit
            # {<share-any>}: set of kname: of vks sharing min 1 bit with kn
            #      it is a super-set of tsvk
            chc = (tsvk, tcvk - tsvk)
            ltsvk = len(tsvk)
            if ltsvk < max_tsleng:
                continue
            ltcvk = len(tcvk)
            # insert into choices list: bigger front
            # if equal: dont insert
            # 1: find index of insertion
            if not best_choice:
                best_choice = chc
                max_tsleng = ltsvk
                max_tcleng = ltcvk
                best_bits = bits
            else:
                if best_choice[0] == tsvk:
                    continue
                # see if to replace the best_choice?
                replace = False
                if max_tsleng < ltsvk:
                    replace = True
                elif max_tsleng == ltsvk:
                    if max_tcleng < ltcvk:
                        replace = True
                if replace:
                    best_choice = chc
                    max_tsleng = ltsvk
                    max_tcleng = ltcvk
                    best_bits = bits
        result = {
            'bestkey': tuple(sorted(list(best_choice[0]))),
            'touched':  best_choice[1],
            'bits': best_bits
        }
        return result
