from basics import print_json, unite_satdics, filter_sdic
from TransKlauseEngine import TxEngine
from vk12mgr import VK12Manager
from basics import topbits
from satholder import SatHolder


class Node12:
    def __init__(self, vname, parent, vk12m, sh, psat):
        self.parent = parent
        self.psat = psat
        # vname is 2 ditigs number. vname % 10 is the given val
        self.vname = vname    # vname // 10: is the parent-nob
        self.nexts = []
        self.sh = sh
        if type(vk12m) == type({}):  # when vk12m is a dict(full-sats)
            self.sats = vk12m        # save the full-sats
            self.nov = len(vk12m)
            self.state = 2           # this will trigger collect_sats() call
        else:  # vk12m is of type VK12Manager
            self.vk12m = vk12m
            self.nov = vk12m.nov

            self.state = 0
            if self.nov <= 3:  # for nov=3 or less: get all sats by looping
                self.sats = self.nov321_sats()

    def collect_sats(self, satfilter):

        def filter(sfilter, sat):
            if type(sat) == type({}):
                if filter_sdic(sfilter, sat):
                    return [sat]
                else:
                    return []
            else:
                lst = []
                for sx in sat:
                    s = filter(sfilter, sx)
                    if len(s) > 0:
                        lst += s
                return lst

        ss = filter(satfilter, self.sats)
        if len(ss) == 0:
            return
        # find crown
        node = self
        while type(node).__name__ != 'Crown':
            node = node.parent
        # unify satpath
        if not self.satpath_collected:
            sd = {}
            for s in self.satpath:
                sd.update(s)
            self.satpath_collected = sd
        # add to crown
        # self.satpath.append(ss)
        # node.csats.append(self.satpath)
        node.csats.append([self.satpath_collected, ss])
        self.state = 1
    # end of def collect_sats(self, satfilter):

    def nov321_sats(self):   # when nov==3,2,1, collect integer-sats
        nsats = []
        vkdic = self.vk12m.vkdic
        N = 2 ** self.nov
        for i in range(N):  # 2** nov
            hit = False
            for vk in vkdic.values():
                if vk.hit(i):
                    hit = True
                    break
            if not hit:
                nsats.append(i)
        ln = len(nsats)
        if ln == 0:
            self.suicide()
        else:
            self.sats = [self.sh.get_sats(si) for si in nsats]
            self.state = 2
        return self.sats
    # end of def nov3_sats(self):

    def spawn(self, satfilter):
        nob = self.vk12m.bvk.nob    # nob can be 1 or 2
        name_base = nob * 10        # name_base: 10 or 20
        self.topbits = topbits(self.nov, nob)

        # what if > 1 bvks (nob==2), need cvs to be excluded in morph
        if self.vk12m.need_tx():
            self.tx = TxEngine(self.vk12m.bvk)
            self.sh.transfer(self.tx)
            vk12m = self.vk12m.txed_clone(self.tx)
        else:
            vk12m = self.vk12m.clone()
        chdic = vk12m.morph(self.topbits)

        if len(chdic) == 0:
            self.sats = self.sh.full_sats()
            # return []
        else:
            shtail = self.sh.spawn_tail(nob)
            new_sh = SatHolder(shtail)
            self.sh.cut_tail(nob)
            for val, vkm in chdic.items():
                psat = self.psat.copy()
                psat.update(self.sh.get_sats(val))
                if vkm:
                    node = Node12(
                        name_base + val,  # %10 -> val, //10 -> nob
                        self,             # node's parent
                        vkm,              # vk12m for node
                        new_sh.clone(),   # sh - clone: for sh.varray is a ref
                        psat)
                else:
                    tail_sat = new_sh.full_sats()
                    node = Node12(
                        name_base + val,  # %10 -> val, //10 -> nob
                        self,
                        tail_sat,
                        None,
                        psat)
                self.nexts.append(node)
        return self.nexts
    # end of def spawn(self, satfilter):

    def suicide(self):
        print(f'{self.name} destroyed.')
        i = 0
        while i < len(self.parent.next()):
            if self.parent.next[i].name == self.name:
                self.parent.next.pop(i)
                break
            else:
                i += 1
        if len(self.parent.next) == 0:
            self.parent.suicide()
