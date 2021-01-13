from vk12mgr import VK12Manager
from crown import Crown

class CrownManager:
    def __init__(self, sh, nov):
        self.sh = sh
        self.nov = nov
        self.crowns = []
        self.crown_index = -1

    def add_crown(self, val, psats, vk1dic, vk2dic):
        vk12m = VK12Manager(vk1dic, vk2dic, self.nov)
        if vk12m.terminated:
            return None
        crown = Crown(val, self.sh.clone(), psats, vk12m)

        # adde to ranked self.crown list
        if len(self.crowns) == 0:
            self.crowns.append(crown)
        else:
            cnt1 = len(crown.vk12m.vk1dic)
            cnt2 = len(crown.vk12m.vk2dic)
            inserted = False
            for i, crn in enumerate(self.crowns):
                ln = len(crn.vk12m.vk1dic)
                if ln < cnt1:
                    self.crowns.insert(i, crown)
                    inserted = True
                elif ln == cnt1:
                    if len(crn.vk12m.vk2dic) < cnt2:
                        self.crowns.insert(i, crown)
                        inserted = True
            if not inserted:
                self.crowns.append(crown)
        self.crown_index = 0
        return crown

    def topcrown_psats(self):
        if self.crown_index >= len(self.crowns):
            return None
        crn = self.crowns[self.crown_index]
        self. crown_index += 1
        result = crn.solve()
        return result
