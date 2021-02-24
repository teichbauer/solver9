from basics import get_bit, get_sdic, set_bits
from datetime import datetime


class SatHolder:
    ''' Manages original variable names. Originally: [0,1,2,..<nov-1>]
        Instance owned by every branch as .sh. At the very beginning,
        br0.sh's array is nov long. br0 has 3 bit-cut, and has
        a tx :[(4,7,(2,6),(1,5),...]. br0.sh will call transfer(br0.tx),
        then cut its tail([0,1,...<nov-4>]) for giving it to br0's every child.
        Afterwards, br0.sh only keeps 3 [4,2,1]
        when br0 has children[1], children[5] (1,5 are sat-values for them),
        the part of sats for this 3-bit will be
        <sat0-1>: {4:0, 2:0, 1:0}  reflecting sat-value 001(1), and
        <sat0-5>: {4:1, 2:0, 1:1}  reflecting sat-value 101(5)
        if eventually r1 gets its sats (of length nov - 3), the total sats-set
        will then include this <sat0-1>, to have complete sats-set.
        This process is true for every child down the tree. So each br-m is done
        it will have a sh of length 1,2 or max:3, containing the variable-names
        for its 1,3 or 7 (2-1, 4-1,8-1) sat-values, and be one part of the
        whole sat-set (chain)
        '''

    def __init__(self, varray):
        self.varray = varray
        self.ln = len(varray)

    def clone(self):
        return SatHolder(self.varray[:])

    def spawn_tail(self, cutcnt):
        return self.varray[:-cutcnt]

    def transfer(self, txe):
        self.varray = txe.trans_varray(self.varray)

    def cut_tail(self, cutcnt):
        self.varray = self.varray[-cutcnt:]
        self.ln = cutcnt

    def get_sats(self, val):
        assert(val < (2 ** self.ln))
        satdic = {}
        for ind, vn in enumerate(self.varray):
            v = get_bit(val, ind)
            satdic[vn] = v
        return satdic

    def full_sats(self):
        sats = {v: 2 for v in self.varray}
        return sats

    def get_segment_sats(self, chil_keyvalue):
        ''' assert check:
               varray length can be 1, 2 or 3, where sat-value can be:
               (0,1), (0,1,2,3) or (0,1,2,3,4,5,6,7)
            operational example:
                varray: [231, 8]: names of two variables,
                varray[0] == 231, varray[1] == 8
                And sat chil_keyvalue: 2 == bin( 10 )
                output:
            return value is a list of tuples, as like:
                [(231,0), (8,1)]:
                variable-231 has boolean chil_keyvalue 0
                variable-8   has boolean chil_keyvalue 1
            '''
        assert(chil_keyvalue < (2 ** self.ln))
        lst = []
        for ind, v in enumerate(self.varray):
            # every bit in varray represent a variable(original name)
            lst.append((v, get_bit(chil_keyvalue, ind)))
        return lst
