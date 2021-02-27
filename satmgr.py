class SatManager:
    def __init__(self):
        self.sats = []

    def resolve(self, hnode, csats):
        sats = []
        crmgr = hnode.crwnmge
        for sfilter in csats:
            crmgr.init()
            for val, vkdic in crmgr.raw_crown_dic.items():
                crmgr.add_crown(val, vkdic, sfilter)

            sats += hnode.crwnmgr.resolve(sfilter)
        hnode.next = None
        hnode.sats = sats
        if hnode.parent:
            self.resolve(hnode.parent, hnode.sats)
        else:
            self.sats = hnode.sats
