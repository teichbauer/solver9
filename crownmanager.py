from vk12mgr import VK12Manager
from crown import Crown


class CrownManager:
    def __init__(self, sh, nov):
        self.sh = sh
        self.nov = nov
        self.crowns = []
        self.crown_index = -1

    def add_done_crown(self, val, psats):
        sdic = {v: 2 for v in self.sh.varray}
        csats = [sdic, f"({self.nov}){val}-full"]
        crown = Crown(val, psats, csats)
        crown.done = True
        self.crowns.insert(0, crown)

    def add_crown(self, val, psats, vk1dic, vk2dic):
        ln1 = len(vk1dic)
        ln2 = len(vk2dic)
        if ln1 + ln2 == 1:
            if ln1:
                csats = self._vk1_sdic(vk1dic.popitem()[1])
            else:
                csats = self._vk2_sdic(vk1dic.popitem()[1])
            crown = Crown(val, self.sh, psats, csats)
            self.crowns.insert(0, crown)
            return

        vk12m = VK12Manager(vk1dic, vk2dic, self.nov)
        if vk12m.terminated:
            return None
        crown = Crown(val, self.sh.clone(), psats, vk12m)

        # adde to ranked self.crown list
        if len(self.crowns) == 0:
            self.crowns.append(crown)
            self.crown_index = 0
        else:
            cnt1 = len(crown.vk12m.vk1dic)
            cnt2 = len(crown.vk12m.vk2dic)
            insert_index = -1
            for i, crn in enumerate(self.crowns):
                if crn.done:  # done crown(s) remain front
                    continue
                # ? for loop dont allow insert into src, but
                # in this case, when I use enumerate, it does allow
                ln = len(crn.vk12m.vk1dic)
                if ln < cnt1:
                    # self.crowns.insert(i, crown)
                    insert_index = i
                    break
                elif ln == cnt1:
                    if len(crn.vk12m.vk2dic) < cnt2:  # TBD: should be >
                        insert_index = i
                        break
            if insert_index == -1:         # no one in list has lower ranking
                self.crowns.append(crown)  # append as lowest
            else:
                # behind insert_index, lements are of lower ranking. insert.
                self.crowns.insert(insert_index, crown)
        return crown

    def _vk1_sdic(self, vk):
        val = (list(vk.dic.values())[0] + 1) % 2  # oppo val of vk.dic.value
        v0 = self.sh.varray[0]
        sdic = {v0: val}
        for b in range(1, len(self.sh.varray)):
            sdic[self.sh.varray[b]] = 2
        return [(sdic, f'{self.nov}.1{val}')]

    def _vk2_sdic(self, vk):
        v0 = self.sh.varray[0]  # var-name in sh[0] (original bit-number)
        v1 = self.sh.varray[1]  # var-name in sh[1] (original bit-number)
        val_0 = vk.bits[1]      # vk.bits is reverse-sorted(descending), so
        val_1 = vk.bits[0]      # bits[1] maps to sh[0], bits[0] to sh[1]
        d0 = {v0: (val_0 + 1) % 2, v1: val_1}    # flip val_0
        d1 = {v0: val_0, v1: (val_1 + 1) % 2}    # flip val_1
        for b in range(2, len(self.sh.varray)):  # rest of sh.varray - [2:]
            d0[self.sh.varray[b]] = 2
            d1[self.sh.varray[b]] = 2
        return [(d0, 'name1'), (d1, 'name2')]

    def topcrown_psats(self):
        if self.crown_index >= len(self.crowns):
            return None
        crn = self.crowns[self.crown_index]
        self. crown_index += 1
        result = crn.dig_thru()
        if len(result) == 0:
            return self.topcrown_psats()
        return result
