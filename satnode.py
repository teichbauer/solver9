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
        self.children = {}
        self.sats = None
        self.next_sh = SatHolder(self.sh.spawn_tail(3))
        self.crwnmgr = CrownManager(self.next_sh, self.nov - 3)
        self.sh.cut_tail(3)
        self.topbits = topbits(self.nov, 3)
        if len(vkm.vkdic) == 0:
            self.sats = self.max_sats()

    def spawn(self):
        choice = self.vkm.bestchoice()
        self.bvk = self.vkm.vkdic[choice['bestkey'][0]]
        if self.topbits != self.bvk.bits:
            self.tx = TxEngine(self.bvk, self.nov)
            self.sh.transfer(self.tx)
            vkm = self.vkm.txed_clone(self.tx)
        else:
            vkm = self.vkm

        excl_cvs = [topvalue(vkm.vkdic[kn]) for kn in choice['bestkey']]

        crown_dic = vkm.morph(choice, self.topbits, excl_cvs) # vkm.nov -= 3

        for val, cdic in crown_dic.items():
            psats = self.sh.get_psats(val)
            self.crwnmgr.add_crown(val, psats, cdic[1], cdic[2])

        self.next = None
        while True:
            psats = self.crwnmgr.topcrown_psats()
            if psats == None:
                print(f'{self.name} has no sats')
                return
            if self.next == None:
                self.next = SatNode(self, self.next_sh, vkm)
            sats = self.combine_sats(psats, self.next)
            if sats:
                print(f'{self.name} has sats: {sats}')
                return

    def combine_sats(self, psats, node):
        return True
