from satholder import SatHolder
from TransKlauseEngine import TxEngine


class SatNode:
    def __init__(self, parent, sh, vkm):
        self.parent = parent
        self.sh = sh
        self.vkm = vkm
        self.nov = vkm.nov
        if self.nov == 3:
            self.sats = self.nov3()
        else:
            self.sats = None
        self.topbits = list(range(self.nov - 1, self.nov - 1 - 3, -1))
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

        self.chdic, self.vk12dic = vkm.morph(choice, self.topbits)
        shtail = self.sh.spawn_tail(3)
        new_sh = SatHolder(shtail)
        self.sh.cut_tail(3)

        self.next = SatNode(self, new_sh, vkm)
        return self.next

    def resolve(self, path):
        pass

    def nov3(self):
        return 7

    def max_sats(self):
        return 5
