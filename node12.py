from TransKlauseEngine import TxEngine


class Node12:
    def __init__(self, val, parent, vk12m):
        self.val = val
        self.parent = parent
        self.vk12m = vk12m
        self.nov = vk12m.nov
        self.children = {}

    def transfer_clone(self, base_vk):
        tx = TxEngine(base_vk, self.nov)
        vk1dic = tx.trans_vkdic(self.vk1dic)
        vk2dic = tx.trans_vkdic(self.vk2dic)
        return Node12(self.parent, vk1dic, vk2dic, self.nov)

    def spawn(self):
        txed_crn = self.transfer_clone(self.bvk)
        cutn = self.bvk.nob
