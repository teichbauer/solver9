
def get_bit(val, bit):
    return (val >> bit) & 1


def set_bit(val, bit_index, new_bit_value):
    """ Set the bit_index (0-based) bit of val to x (1 or 0)
        and return the new val. the input param val remains unmodified.
        """
    mask = 1 << bit_index  # mask - integer with just the chosen bit set.
    val &= ~mask           # Clear the bit indicated by the mask (if x == 0)
    if new_bit_value:
        val |= mask        # If x was True, set the bit indicated by the mask.
    return val             # Return the result, we're done.


def set_bits(val, d):
    for b, v in d.items():
        val = set_bit(val, b, v)
    return val


def get_sdic(filename):
    path = './configs/' + filename
    sdic = eval(open(path).read())
    return sdic


def ordered_dic_string(d):
    m = '{ '
    ks = list(sorted(list(d.keys()), reverse=True))
    for k in ks:
        m += str(k) + ': ' + str(d[k]) + ', '
    m = m.strip(', ')
    m += ' }'
    return m


def merge_sats(dic0, dic1):
    # merge dic1 into dic0 - if a key has both 0 | 1, set its value = 2
    for k, v in dic1.items():
        if k in dic0:
            if dic0[k] != v:
                dic0[k] = 2
        else:
            dic0[k] = v
    return dic0


def merge_satdics(target_dic, src_dic):
    # satdic is a dic with keys being bit-number(varaible names), and
    # values are the boolena values 0 | 1
    # if a value set to be 2, this is a "wild-card": can be either 0 or 1
    # -------------------------------------------------------------------
    # merge src_dic into target_dic - if a key has 0 and 1, set its value = 2
    for k, v in src_dic.items():
        if k in target_dic:
            if target_dic[k] != v:
                target_dic[k] = 2
        else:
            target_dic[k] = v
    return target_dic


def print_json(nov, vkdic, fname):
    sdic = {
        'nov': nov,
        'kdic': {}
    }
    for kn, vk in vkdic.items():
        sdic['kdic'][kn] = vk.dic
    ks = sorted(list(sdic['kdic'].keys()))

    with open(fname, 'w') as f:
        f.write('{\n')
        f.write('    "nov": ' + str(sdic['nov']) + ',\n')
        f.write('    "kdic": {\n')
        # for k, d in sdic['kdic'].items():
        for k in ks:
            msg = ordered_dic_string(sdic['kdic'][k])
            line = f'        "{k}": {msg},'
            f.write(f'{line}\n')
        f.write('    }\n}')


def topvalue(vk):
    # shift all bit to top positions and return that n-bits value
    # E.G. {7:1, 5:0, 0:1} -> 101/5
    bits = vk.bits[:]
    v = 0
    while bits:
        v = (v << 1) | vk.dic[bits.pop(0)]
    return v


def topbits(nov, nob):
    # for nov = 5 (bits: 4,3,2,1,0), nob == 2 -> get [4,3]
    t = nov - 1
    lst = []
    while nob > 0:
        lst.append(t)
        t -= 1
        nob -= 1
    return lst


def topbits_coverages(vk, topbits):
    ''' example: vk.dic: {7:1, 4:1, 1:0}, topbits:[7,6]. for the 2 bits
        allvalues: [00,01,10,11]/[0,1,2,3] vk only hit 10/2,11/3, 
        {4:1, 1:0} lying outside of topbits - outdic: {4:1, 1:0}
        return [2,3], {4:1, 1:0}   '''
    outdic = {}
    L = len(topbits)
    allvalues = list(range(2**L))
    cvs = []
    new_nov = vk.nov - L

    dic = {}
    for b in vk.dic:
        if b in topbits:
            dic[b - new_nov] = vk.dic[b]
        else:
            outdic[b] = vk.dic[b]
    for x in allvalues:
        conflict = False
        for bit, v in dic.items():
            if get_bit(x, bit) != v:
                conflict = True
                break
        if not conflict:
            cvs.append(x)
    return cvs, outdic


def filter_sdic(filter, sdic):
    ''' see if sdic has <key>:<value> pair violating filter. if sdic has
        v:2, and filter[v] = 0 or 1, sdic[v] will be modified to 0 or 1
        '''
    d1 = sdic.copy()    # sdic may get updated. a copy for for loop
    for b, v in d1.items():     # check every k/v in sdic
        if b in filter:         # if filter doesn't have it: don't care
            if filter[b] == 2:  # filter[b] tolerates both values
                continue        # let it thru
            if filter[b] != v:  # violates filter[b] value, stop here
                if v == 2:      # when sdic[b] is 2, allowing 0|1,
                    sdic[b] = filter[b]  # set it to be filter[b]
                else:
                    return True  # return True: sdic fails
    return False


def unite_satdics(s0, s1, extend=False):  # s1 as filter satdic
    ''' restrictively filter unify/extend s0 with filter_dic(s1): 
        1. bit in both: 
            a: s0[bit] == s1[bit] -> {*, bit:v0, *}. (v0 is s0[bit])
            b: v0 != v1, but v0 is 2   -> {*, bit:v1, *} / restrict v0 to v1
            c: v0 != v1, but v1 is 2   -> {*, bit:v0, *} / passed filter s1
            d: v0 != v1, none of v0, v1 is 2 -> return None / conflict
        2. bit only in s0 or s1
            a. bit in s0 only -> {bit:v0} -> filter not touched
            b. bit only in s1 
               if extend==True: extend with s1[bit]
               if extend==False: doesn't take s1's bit/value. same leng as s0.
        '''
    res = {}
    unified_keys = set(s0.keys()).union(set(s1.keys()))
    for b in unified_keys:
        if (b in s0) and (b in s1):
            if s0[b] != s1[b]:
                if s0[b] == 2:
                    res[b] = s1[b]
                elif s1[b] == 2:
                    res[b] = s0[b]
                else:
                    # conflicting values (0,1) on the same bit
                    return None
            else:  # s0[b] == s1[b]
                res[b] = s0[b]
        else:      # b is in s0, OR in s1, but not in both
            if b in s0:
                res[b] = s0[b]
            elif extend and (b in s1):
                res[b] = s1[b]
    return res
