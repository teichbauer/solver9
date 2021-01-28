from vk12mgr import VK12Manager
from crown import Crown
from basics import sdic_fail


class CrownManager:
    def __init__(self, sh, nov):
        self.sh = sh
        self.nov = nov
        self.crowns = []
        self.crown_index = -1
        self.solution_cursor = 0

    def add_crown(self, val, psats, vkdic, satfilter=None):
        ln = len(vkdic)
        if ln < 2:
            if ln == 0:
                sdic = {v: 2 for v in self.sh.varray}
                csats = [(sdic, f"{self.nov}.{val}-full")]
            elif ln == 1:
                vk = list(vkdic.values())[0]
                if vk.nob == 1:
                    csats = self._vk1_sdic(vk)
                else:
                    csats = self._vk2_sdic(vk)
            if satfilter:
                i = 0
                while i < len(csats):
                    if sdic_fail(satfilter, csats[i][0]):
                        csats.pop(i)
                    else:
                        i += 1
            if len(csats) > 0:
                crown = Crown(val, self.sh, psats, csats)
                self.crowns.insert(0, crown)
                self.crown_index = 0
            return

        vk12m = VK12Manager(vkdic, self.nov)
        if vk12m.terminated:
            return None
        crown = Crown(val, self.sh.clone(), psats, vk12m)

        # adde to ranked self.crown list
        if len(self.crowns) == 0:
            self.crowns.append(crown)
            self.crown_index = 0
        else:
            cnt1 = len(crown.vk12m.kn1s)
            cnt2 = len(crown.vk12m.kn2s)
            insert_index = -1
            for i, crn in enumerate(self.crowns):
                if crn.done:  # done crown(s) remain front
                    continue
                # ? for loop dont allow insert into src, but
                # in this case, when I use enumerate, it does allow
                ln = len(crn.vk12m.kn1s)
                if ln < cnt1:
                    # self.crowns.insert(i, crown)
                    insert_index = i
                    break
                elif ln == cnt1:
                    if len(crn.vk12m.kn2s) < cnt2:  # TBD: should be >
                        insert_index = i
                        break
            if insert_index == -1:         # no one in list has lower ranking
                self.crowns.append(crown)  # append as lowest
            else:
                # behind insert_index, lements are of lower ranking. insert.
                self.crowns.insert(insert_index, crown)
        return crown

    def _oppo(self, binary_value):
        return (binary_value + 1) % 2

    def _vk1_sdic(self, vk):
        sdic = {}
        for b in range(len(self.sh.varray)):
            if b == vk.bits[0]:  # set oppo val of vk.dic[bit]
                sdic[self.sh.varray[b]] = self._oppo(vk.dic[vk.bits[0]])
            else:
                sdic[self.sh.varray[b]] = 2
        return [(sdic, f'{self.nov}.{vk.kname}')]

    def _vk2_sdic(self, vk):
        b0 = vk.bits[0]
        b1 = vk.bits[1]
        sidc0 = {}
        sidc1 = {}

        for b in range(len(self.sh.varray)):
            if b != b0:
                sdic0[self.sh.varray[b]] = 2
            else:
                sdic0[self.sh.varray[b]] = self._oppo(vk.dic[b0])

        for b in range(len(self.sh.varray)):
            if b != b1:
                sdic1[self.sh.varray[b]] = 2
            else:
                sdic1[self.sh.varray[b]] = self._oppo(vk.dic[b1])
        return [(sdic0, 'name1'), (sdic1, 'name2')]

    def next_psats(self):
        ''' self.crowns has a list of crowns, each (after it resolved) has
            a list of solutions. self.solution_cursor points to the cuurent
            solution of current crown. Calling this, next solution is returned,
            and next call will return the next - moving thru all solutions
            of each crown, till there's no more: return None.
            '''
        if self.crown_index >= len(self.crowns):
            return None
        # if current crown not resolved, resolve it
        if not self.crowns[self.crown_index].done:
            self.crowns[self.crown_index].resolve()

        # if cursor is with-in current crown: return next solution. If not,
        # next crown set to be current, and call this again
        if self.solution_cursor < len(self.crowns[self.crown_index].csats):
            # res = self.crowns[self.crown_index].csats[self.solution_cursor]
            res = self.crowns[self.crown_index].get_psat(self.solution_cursor)
            self.solution_cursor += 1
            return res
        else:
            self.crown_index += 1       # set to next crown
            self.solution_cursor = 0    # reset cursor
            return self.next_psats()    # recursive call

    def next_psat(self):
        self.solution_cursor = 0
        while self.crown_index < len(self.crowns):
            res = self.get_psat()
            if res:
                return res
        return None

    def get_psat(self):
        " get current crown's csat. "
        # if current crown not resolved, resolve it
        if not self.crowns[self.crown_index].done:
            self.crowns[self.crown_index].resolve()

        if len(self.crowns[self.crown_index].csats) == 0:
            self.crown_index += 1
            return None

        # get csat of cursor-position in current crown. increment cursor.
        # if cursor overflow, increment crown_index and reset cursor tp 0
        res = self.crowns[self.crown_index].get_psat(self.solution_cursor)
        self.solution_cursor += 1
        if self.solution_cursor >= len(self.crowns[self.crown_index].csats):
            self.crown_index += 1
            self.solution_cursor = 0
        return res
