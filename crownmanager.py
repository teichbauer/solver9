from vk12mgr import VK12Manager
from crown import Crown
from basics import filter_sdic, unite_satdics


class CrownManager:
    def __init__(self, sh, nov):
        self.sh = sh
        self.nov = nov
        self.state = 0

    def init(self):    # be called every time satnode.spawn is called.
        self.crowns = []
        self.crown_index = -1
        self.csat_cursor = 0

    def add_crown(self, val, psats, vkdic, satfilter=None):
        ln = len(vkdic)
        if ln < 2:
            if ln == 0:
                sdic = {v: 2 for v in self.sh.varray}
                csats = [sdic]
            elif ln == 1:
                vk = list(vkdic.values())[0]
                if vk.nob == 1:
                    csats = self._vk1_sdic(vk, satfilter)
                else:
                    csats = self._vk2_sdic(vk, satfilter)
            if len(csats) > 0:
                crown = Crown(val, self.sh, psats, csats)
                self.crowns.append(crown)
                self.crown_index = 0
            return

        vk12m = VK12Manager(vkdic, self.nov)
        if vk12m.terminated:
            return None
        crown = Crown(val, self.sh.clone(), psats, vk12m)
        self.crowns.append(crown)
        self.crown_index = 0
        return crown
    # end of def add_crown(..)

    def _oppo(self, binary_value):
        return (binary_value + 1) % 2

    def _filter_1kvpair(self, bit, value, satfilter):
        sd = {}
        oppo = self._oppo(value)
        for b in range(self.sh.ln):
            vn = self.sh.varray[b]
            if b == bit:
                sd[vn] = oppo
            else:
                sd[vn] = 2
        if satfilter:
            return unite_satdics(sd, satfilter)
        return sd

    def _vk1_sdic(self, vk, satfilter=None):
        sdic = self._filter_1kvpair(vk.bits[0], vk.dic[vk.bits[0]], satfilter)
        if sdic:
            return [sdic]
        return []

    def _vk2_sdic(self, vk, satfilter=None):  # vk has 2 bits
        lst = []
        s0 = self._filter_1kvpair(vk.bits[0], vk.dic[vk.bits[0]], satfilter)
        s1 = self._filter_1kvpair(vk.bits[1], vk.dic[vk.bits[1]], satfilter)
        if s0:
            lst.append(s0)
        if s1 and S1 != s0:
            lst.append(s1)
        return lst

    def next_psat(self, satfilter):
        # if self.crown_index == 4:
        #     x = 1
        while self.crown_index < len(self.crowns):
            res = self.get_psat(satfilter)
            if res:
                return res
        return None

    def get_psat(self, satfilter):
        " get current crown's csat. "
        # if current crown not resolved, resolve it
        if not self.crowns[self.crown_index].done:
            self.crowns[self.crown_index].resolve(satfilter)
        if len(self.crowns[self.crown_index].csats) == 0:
            self.crown_index += 1
            return None

        # get csat of cursor-position in current crown. increment cursor.
        # if cursor overflow, increment crown_index and reset cursor tp 0
        res, self.csat_cursor = \
            self.crowns[self.crown_index].crown_psat(self.csat_cursor)
        if self.csat_cursor >= len(self.crowns[self.crown_index].csats):
            self.crown_index += 1
            if self.crown_index < len(self.crowns):
                self.csat_cursor = 0
            else:
                self.state = 1
        return res
