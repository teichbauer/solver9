from basics import topbits_coverages, topvalue, topbits, sdic_fail, print_json
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
            tx_vkm = self.vkm.txed_clone(self.tx)
        else:
            tx_vkm = self.vkm.clone()

        next_sh = SatHolder(self.sh.spawn_tail(3))
        self.crwnmgr = CrownManager(next_sh, self.nov - 3)
        self.sh.cut_tail(3)
        # after tx_vkm.morph, tx_vkm only has (.vkdic) vk3 left, if any
        self.raw_crown_dic = tx_vkm.morph(self.topbits)  # vkm.nov -= 3
        # self.next = SatNode(self, next_sh, tx_vkm)
        self.next_stuff = (next_sh, tx_vkm)

    def spawn(self, satfilter=None):
        if self.done:
            return self.sats
        # after morph, vkm.vkdic only have vk3s left, if any
        if satfilter:
            crown_dic = self.filter_children(self.raw_crown_dic, satfilter)
        else:
            crown_dic = self.raw_crown_dic

        for val, vkdic in crown_dic.items():
            psats = self.sh.get_sats(val)
            self.crwnmgr.add_crown(val, psats, vkdic, satfilter)

        while True:
            # psats = self.crwnmgr.topcrown_psats()
            psats = self.crwnmgr.next_psats()
            if psats == None:
                print(f'{self.name} has no sats')
                return None
            if self.next == None:
                self.next = SatNode(
                    self, self.next_stuff[0], self.next_stuff[1])
            sats = self.next.spawn(psats[0])
            if satfilter:
                if not sdic_fail(satfilter, sats):
                    self.sats = sats
            else:
                self.sats = sats
            if self.sats and len(self.sats) > 0:
                self.sats = self.combine_sats(psats, self.sats)
                print(f'{self.name} has sats: {self.sats}')
            return self.sats

    def filter_children(self, chdic, satfilter):
        vals = list(chdic.keys())
        for val in vals:
            d = self.sh.get_sats(val)
            if sdic_fail(satfilter, d):
                chdic.pop(val)
        return chdic

    def combine_sats(self, sdic1, sdic2):
        sdic = sdic1.copy()
        sdic.update(sdic2)
        return sdic
