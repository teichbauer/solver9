from basics import topbits, filter_sdic, unite_satdics, print_json
from basics import split_satfilter, vkdic_sat_test, vkdic_remove, FINAL, deb_01
from vklause import VKlause
from satholder import SatHolder
from TransKlauseEngine import TxEngine
from node12 import Node12
from vkmgr import VKManager
from crownmanager import CrownManager


class SatNode:
    def __init__(self, parent, sh, vkm):
        self.parent = parent
        self.sh = sh
        self.vkm = vkm
        self.nov = vkm.nov
        self.name = f'sn-{self.nov}'
        self.sats = None
        self.topbits = topbits(self.nov, 3)
        self.next = None
        self.done = False
        if len(vkm.vkdic) == 0:
            self.sats = self.sh.full_sats()
            self.done = True
        else:
            self.prepare()

    def prepare(self):
        choice = self.vkm.bestchoice()
        self.bvk = self.vkm.vkdic[choice['bestkey'][0]]
        if self.topbits != choice['bits']:  # the same as self.bvk.bits:
            self.tx = TxEngine(self.bvk)
            self.sh.transfer(self.tx)
            self.tx_vkm = self.vkm.txed_clone(self.tx)
        else:
            self.tx_vkm = self.vkm.clone()
        self.tail_varray = self.sh.spawn_tail(3)
        next_sh = SatHolder(self.tail_varray[:])
        self.crwnmgr = CrownManager(self, next_sh, self.nov - 3)
        self.sh.cut_tail(3)
        # after tx_vkm.morph, tx_vkm only has (.vkdic) vk3 left, if any
        self.raw_crown_dic = self.tx_vkm.morph(self.topbits)  # vkm.nov -= 3
        self.next_stuff = (next_sh.clone(), self.tx_vkm)
    # end of def prepare(self):

    def spawn(self):
        if self.done:
            return self.sats
        # after morph, vkm.vkdic only have vk3s left, if any
        if len(self.raw_crown_dic) == 0:
            self.sats = self.sh.full_sats()
            self.done = True
            return None

        self.next = SatNode(self, self.next_stuff[0], self.next_stuff[1])
        return self.next

    def resolve(self, satfilters=None):
        psats = []
        if satfilters:
            for satfilter in satfilters:  # ? clone each satfilter ?
                self.crwnmgr.init()
                for val, vkdic in crown_dic.items():
                    self.crwnmgr.add_crown(val, vkdic, satfilter)
                while self.crwnmgr.state == 0:
                    psat = self.crwnmgr.resolve(self.sats)
                    if psat:
                        psats.append(psat)
        else:
            while self.crwnmgr.state == 0:
                psat = self.crwnmgr.resolve(self.sats)
                if psat:
                    psats.append(psat)
        if self.parent:
            return self.parent.resolve(psats)
        else:
            return psats

    def tmp(self):
        while self.crwnmgr.state == 0:
            psat = self.crwnmgr.next_psat(satfilter)
            if psat == None:
                print(f'{self.name} has no sats')
                return FINAL
            if FINAL['debug']:
                deb_01(psat)

            # if self.next == None:
            #     self.next = SatNode(
            #         self, self.next_stuff[0], self.next_stuff[1])
            psats = split_satfilter(psat)

            if type(psats) == type({}):  # {1: {*:0|1,..}, 2:[kns of ':2'-vks]}
                if vkdic_sat_test(self.next.vkm.vkdic, psats[1]):
                    kd = vkdic_remove(self.next.vkm.vkdic, psats[2])
                    snode = SatNode(self, self.next_stuff[0],
                                    VKManager(kd, self.nov - 3, True))
                    ss = snode.spawn()
                    if ss:
                        ss.update(psats[1])
                        FINAL['sats'].append(ss)
                        if FINAL['limit'] <= len(FINAL['sats']):
                            print(f'limit of {FINAL["limit"]} reached.')
                            return FINAL
                    else:
                        continue
                else:
                    continue
            elif type(psats) == type([]):
                for psat in psats:
                    # sats = self.next.spawn(psat)
                    sats = self.verify_tail_sat(self.next.vkm.vkdic, psat)
                    if not sats:  # psats resulted in nothing.
                        continue

                    if satfilter:
                        if filter_sdic(satfilter, sats):
                            self.sats = sats
                        if self.sats and len(self.sats) > 0:
                            self.sats = unite_satdics(psat, self.sats, True)
                            # print(f'{self.name} has sats: {self.sats}')
                        return self.sats
                    else:  # if no satfilter, it is on top level - finalize
                        self.sats = unite_satdics(sats, psat, True)
                        FINAL['sats'].append(self.sats)
                        if FINAL['limit'] <= len(FINAL['sats']):
                            print(f'limit of {FINAL["limit"]} reached.')
                            return FINAL
        return FINAL
    # end of def spawn(self, satfilter=None):

    def verify_tail_sat(self, vkdic, sat):
        for vk in vkdic.values():
            Skip = False
            for b, v in vk.dic.items():
                key = self.tail_varray[b]
                if sat[key] != v:
                    Skip = True
                    break
            if not Skip:
                return False
        return sat

    def _clone_chdic(self, chdic):
        dic = {}
        for v, vkd in chdic.items():
            d = dic.setdefault(v, {})
            for kn, vk in vkd.items():
                d[kn] = vk.clone()
        return dic

    def filter_children(self, chdic, satfilter):
        cdic = self._clone_chdic(chdic)
        vals = list(cdic.keys())
        for val in vals:
            d = self.sh.get_sats(val)
            if not filter_sdic(satfilter, d):
                cdic.pop(val)
        return cdic
