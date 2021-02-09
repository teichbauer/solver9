from basics import topbits, filter_sdic, unite_satdics, print_json, FINAL
from vklause import VKlause
from satholder import SatHolder
from TransKlauseEngine import TxEngine
from node12 import Node12
from vk12mgr import VK12Manager
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
            self.tx = TxEngine(self.bvk, self.nov)
            self.sh.transfer(self.tx)
            self.tx_vkm = self.vkm.txed_clone(self.tx)
        else:
            self.tx_vkm = self.vkm.clone()

        next_sh = SatHolder(self.sh.spawn_tail(3))
        self.crwnmgr = CrownManager(next_sh, self.nov - 3)
        self.sh.cut_tail(3)
        # after tx_vkm.morph, tx_vkm only has (.vkdic) vk3 left, if any
        self.raw_crown_dic = self.tx_vkm.morph(self.topbits)  # vkm.nov -= 3
        self.next_stuff = (next_sh, self.tx_vkm)

    def reset_crwnmgr(self):
        pass

    def spawn(self, satfilter=None):
        if self.done:
            return self.sats
        # after morph, vkm.vkdic only have vk3s left, if any
        if satfilter:
            crown_dic = self.filter_children(self.raw_crown_dic, satfilter)
        else:
            crown_dic = self._clone_chdic(self.raw_crown_dic)
        if len(crown_dic) == 0:
            return None
        self.crwnmgr.init()
        for val, vkdic in crown_dic.items():
            psats = self.sh.get_sats(val)
            self.crwnmgr.add_crown(val, psats, vkdic, satfilter)

        while self.crwnmgr.state == 0:
            psats = self.crwnmgr.next_psat(satfilter)
            if psats == None:
                print(f'{self.name} has no sats')
                return None
            if self.next == None:
                self.next = SatNode(
                    self, self.next_stuff[0], self.next_stuff[1])
            sats = self.next.spawn(psats)
            if not sats:  # psats resulted in nothing.
                continue
            if satfilter:
                if not filter_sdic(satfilter, sats):
                    self.sats = sats
                if self.sats and len(self.sats) > 0:
                    self.sats = unite_satdics(psats, self.sats, True)
                    # print(f'{self.name} has sats: {self.sats}')
                return self.sats
            else:  # if no satfilter, it is on top level - finalize
                self.sats = unite_satdics(sats, psats, True)
                FINAL['sats'].append(self.sats)
                if FINAL['limit'] <= len(FINAL['sats']):
                    return FINAL['sats']
            # if self.sats and len(self.sats) > 0:
            #     self.sats = unite_satdics(psats, self.sats, True)
            #     # print(f'{self.name} has sats: {self.sats}')
            # return self.sats

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
            if filter_sdic(satfilter, d):
                cdic.pop(val)
        return cdic

    def combine_sats(self, sdic1, sdic2):
        sdic = sdic1.copy()
        sdic.update(sdic2)
        return sdic
