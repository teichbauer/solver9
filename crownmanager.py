from vk12mgr import VK12Manager
from crown import Crown


class CrownManager:
    def __init__(self, sh, nov):
        self.sh = sh
        self.nov = nov
        self.crowns = []
        self.crown_index = -1

    def add_crown(self, val, psats, vk1dic, vk2dic):
        ln1 = len(vk1dic)
        ln2 = len(vk2dic)
        if ln1 + ln2 == 1:
            if ln1:
                csats = self.onevk_sats(vk1dic.popitem()[1])
            else:
                csats = self.onevk_sats(vk2dic.popitem()[1])
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
        sdic = {}
        for b in range(len(self.sh.varray)):
            val = (vk.dic[b] + 1) % 2  # oppo val of vk.dic[b]
            if b == vk.bits[0]:
                sdic[b] = val
            else:
                sdic[b] = 2
        return [(sdic, f'{self.nov}.1{val}')]

    def _vk2_sdic(self, vk):
        b0 = vk.bits[0]
        b1 = vk.bits[1]
        d0 = {b0: (vk.dic[b0] + 1) % 2, b1: vk.dic[b1]}
        d1 = {b0: vk.dic[b0], b1: (vk.dic[b1] + 1) % 2}
        for b in range(len(self.sh.varray)):
            if b not in vk.bits:
                d0[b] = 2
                d1[b] = 2
        return [(d0, 'name1'), (d1, 'name2')]

    def onevk_sats(self, vk):
        sdic = {}
        if vk.nob == 1:
            for b in range(len(self.sh.varray)):
                if b == vk.bits[0]:
                    sdic[b] = (vk.dic[b] + 1) % 2  # oppo val of vk.dic[b]
                else:
                    sdic[b] = 2
        else:
            pass
        return sdic

    def topcrown_psats(self):
        if self.crown_index >= len(self.crowns):
            return None
        crn = self.crowns[self.crown_index]
        self. crown_index += 1
        result = crn.dig_thru()
        if len(result) == 0:
            return self.topcrown_psats()
        return result
