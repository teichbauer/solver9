from node12 import Node12
from basics import topbits, unite_satdics
from TransKlauseEngine import TxEngine
from satholder import SatHolder


class Crown:
    def __init__(self, val, sh, psats, vk12m):
        self.sh = sh
        self.val = val
        self.rootsats = psats
        # child_satdic for top-level children:
        # {<node-name>: <sat-dic>, ..}
        if type(vk12m) == type([]):  # vk12m is actually csats list
            self.csats = vk12m       # assign csats list
            self.done = True
        else:
            self.child_satdic = {}
            self.vk12m = vk12m
            self.csats = []  # sats of successful children
            self.done = False

    def initial_nodes(self):
        self.nodes = []
        nob = self.vk12m.bvk.nob    # nob can be 1 or 2
        name_base = nob * 10        # name_base: 10 or 20
        tbs = topbits(self.vk12m.nov, nob)

        if self.vk12m.need_tx():
            tx = TxEngine(self.vk12m.bvk, self.vk12m.nov)
            self.sh.transfer(tx)
            vk12m = self.vk12m.txed_clone(tx)
        else:
            vk12m = self.vk12m.clone()
        chdic = vk12m.morph(tbs)
        if len(chdic) == 0:
            return
        shtail = self.sh.spawn_tail(nob)
        new_sh = SatHolder(shtail)
        self.sh.cut_tail(nob)

        for val, vkm in chdic.items():
            if vkm:
                node = Node12(
                    name_base + val,  # node12.vname: %10 -> val, //10 -> nob
                    self,             # node's parent
                    vkm,              # vk12m for node
                    new_sh.clone())   # sh is a clone: for sh.varray is a ref
            else:
                tail_sat = new_sh.full_sats()
                node = Node12(
                    name_base + val,
                    self,
                    tail_sat,
                    None)
            # node.state can be 0 or 2
            self.nodes.append(node)
            self.child_satdic[val] = self.sh.get_sats(val)

    def crown_psat(self, index):
        ' combine rootsats with csats[index][0] '
        return unite_satdics(self.rootsats, self.csats[index][0], True)

    def resolve(self, satfilter):
        if not self.done:
            self.initial_nodes()
            self.done = len(self.nodes) == 0
            if not self.done:
                nodes = self.nodes
                nexts = []
                while True:
                    for node in nodes:
                        if node.state == 0:
                            nexts += node.spawn(satfilter)
                        elif node.state == 2:
                            node.collect_sats(satfilter)
                    if len(nexts) == 0:
                        break
                    else:
                        nodes = nexts
                        nexts = []
                self.done = True
        return self.csats
