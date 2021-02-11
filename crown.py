from node12 import Node12
from basics import topbits, unite_satdics
from TransKlauseEngine import TxEngine
from satholder import SatHolder


class Crown:
    def __init__(self, val, sh, psats, vk12m):
        self.sh = sh
        self.val = val
        self.satpath = [psats]
        # {<node-name>: <sat-dic>, ..}
        if type(vk12m) == type([]):        # vk12m is actually csats list
            # the single csat: [psats, vk12m]
            self.csats = [[psats, vk12m]]  # assign csat in csats list as [0]
            self.done = True
        else:
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
            node.satpath.append(self.sh.get_sats(val))

    def crown_psat(self, index):
        ' combine rootsats with csats[index][0] '
        csat = self.csats[index]
        n = len(csat[1])
        csat[0].update(csat[1][self.sub_cursor])
        self.sub_cursor += 1
        if self.sub_cursor < n:
            new_index = index
        else:
            new_index = index + 1
            self.sub_cursor = 0
        return csat[0], new_index
        # return unite_satdics(self.rootsats, self.csats[index][0], True)

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
        if len(self.csats) > 0:
            self.sub_cursor = 0  # for fetching each sub-sat within a csat
        return self.csats
