from basics import topbits_coverages, topvalue, topbits, print_json
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
            self.crwnmgr.add_crown(val, psats, vkdic)

        while True:
            # psats = self.crwnmgr.topcrown_psats()
            psats = self.crwnmgr.next_psats()
            if psats == None:
                print(f'{self.name} has no sats')
                return None
            self.sats = self.next.spawn(psats)
            if self.sats and len(self.sats) > 0:
                print(f'{self.name} has sats: {self.sats}')
                return self.sats

    def prepare(self):
        choice = self.vkm.bestchoice()
        self.bvk = self.vkm.vkdic[choice['bestkey'][0]]
        if self.topbits != choice['bits']:  # the same as self.bvk.bits:
            self.tx = TxEngine(self.bvk, self.nov)
            self.sh.transfer(self.tx)
            self.tx_vkm = self.vkm.txed_clone(self.tx)
        else:
            self.tx_vkm = self.vkm

        self.next_sh = SatHolder(self.sh.spawn_tail(3))
        self.crwnmgr = CrownManager(self.next_sh, self.nov - 3)
        self.sh.cut_tail(3)
        # after tx_vkm.morph, tx_vkm only has (.vkdic) vk3 left, if any
        self.raw_crown_dic = self.tx_vkm.morph(self.topbits)  # vkm.nov -= 3
        self.next = SatNode(self, self.next_sh, self.tx_vkm)

    def spawn0(self, satfilter=None):
        if self.done:
            return self.sats
        choice = self.vkm.bestchoice()
        self.bvk = self.vkm.vkdic[choice['bestkey'][0]]
        if self.topbits != choice['bits']:  # the same as self.bvk.bits:
            self.tx = TxEngine(self.bvk, self.nov)
            self.sh.transfer(self.tx)
            vkm = self.vkm.txed_clone(self.tx)
        else:
            vkm = self.vkm

        self.next_sh = SatHolder(self.sh.spawn_tail(3))
        self.crwnmgr = CrownManager(self.next_sh, self.nov - 3)
        self.sh.cut_tail(3)

        crown_dic = vkm.morph(self.topbits)  # vkm.nov -= 3
        # after morph, vkm.vkdic only have vk3s left, if any
        if satfilter:
            crown_dic = self.filter_children(crown_dic, satfilter)

        for val, vkdic in crown_dic.items():
            psats = self.sh.get_sats(val)
            self.crwnmgr.add_crown(val, psats, vkdic)

        while True:
            psats = self.crwnmgr.topcrown_psats()
            if psats == None:
                print(f'{self.name} has no sats')
                return
            if self.next == None:
                self.next = SatNode(self, self.next_sh, vkm)
                sat3s = self.next.spawn(psats)
            self.sats = self.combine_sats(psats, sat3s)
            if self.sats:
                print(f'{self.name} has sats: {sats}')
                return self.sats

    def filter_children(self, chdic, satfilter):
        vals = list(chdic.keys())
        for val in vals:
            conflict = False
            d = self.sh.get_sats(val)
            for b, v in d.items():
                if b in satfilter:
                    if satfilter[b] == 2:
                        continue
                    conflict = satfilter[b] != v
                    if conflict:
                        break
            if conflict:
                chdic.pop(val)
        return chdic
