import sys
import time
from basics import get_sdic
from satholder import SatHolder, Sat
from satnode import SatNode
from vkmgr import VKManager
from vklause import VKlause


def make_vkdic(kdic, nov):
    vkdic = {}
    for kn, klause in kdic.items():
        vkdic[kn] = VKlause(kn, klause, nov)
    return vkdic


def make_vkm(cnf_fname):
    sdic = get_sdic(cnf_fname)
    vkdic = make_vkdic(sdic['kdic'], sdic['nov'])
    return VKManager(vkdic, sdic['nov'], True)


def verify_sats(sat, bitdic):
    return sat.verify(bitdic)


def verify_satfile(sat_filename):
    cnf_fname = sat_filename.split('.')[0] + '.json'
    bitdic = make_bitdic('r', cnf_fname)
    sat_dic = eval(open('verify/' + sat_filename).read())
    sat = Sat(sat_dic['end-node-name'], sat_dic['sats'])
    verif, intv = sat.verify(bitdic)
    return verif, intv


def process(cnfname):
    vkm = make_vkm(cnfname)
    path = []
    satslots = list(range(vkm.nov))
    sh = SatHolder(satslots)

    sn = SatNode(None, sh, vkm)
    while sn.sats == None:
        path.append(sn)
        sn = sn.spawn()
    sn.resolve(path)

    return None


if __name__ == '__main__':
    # configfilename = 'cfg100-450.json'
    # configfilename = 'cfg60-266.json'
    # configfilename = 'cfg60-262.json'
    # configfilename = 'config1.json'
    # configfilename = 'config1.sat'
    configfilename = 'cfg12-45.json'
    # configfilename = 'cfg60-262.json'

    if len(sys.argv) > 1:
        configfilename = sys.argv[1].strip()

    if configfilename.endswith('.sat'):
        result, value = verify_satfile(configfilename)
        if result:
            print(f'Verified: {value}')
        else:
            print('Not verified')

    elif configfilename.endswith('.json'):
        start_time = time.time()
        sat = process(configfilename)
        now_time = time.time()
        if sat:
            sat.cnf_file = configfilename
            # result = sat.verify(Root_bitdic)
            # if result:
            print('saved under ' + sat.save_dir)
            sat.save()  # save to verify/<cnf>.sat
        else:
            print('No sat found')
        time_used = now_time - start_time
        print(f'Time used: {time_used}')

    x = 1
