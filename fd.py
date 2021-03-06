"""
FD parser
"""

import os

from fv import FV
from raw import RAW


class FD(object):
    def __init__(self, data, start, prefix='', full_dump=True):
        self.start = start
        self.prefix = prefix
        self.data = data
        self.size = len(data)
        self.full_dump = full_dump
        self.blocks = []
        start_ncb = 0
        cur_pos = 0
        index = 0
        if prefix.startswith('bios_'):
            prefix = prefix[len('bios_'):]
        while cur_pos < len(data):
            cur_prefix = '%s%02d_' % (prefix, index)
            if FV.check_sig(data, cur_pos):
                if start_ncb < cur_pos:
                    ncb = RAW(data[start_ncb:cur_pos], start + start_ncb, cur_prefix)
                    self.blocks.append(ncb)
                    index += 1
                    start_ncb = cur_pos
                    continue
                fv = FV(data[cur_pos:], start + cur_pos, cur_prefix)
                self.blocks.append(fv)
                index += 1
                cur_pos += fv.size
                start_ncb = cur_pos
            else:
                cur_pos += 8
        if start_ncb < len(data):
            cur_prefix = '%s%02d_' % (prefix, index)
            ncb = RAW(data[start_ncb:], start + start_ncb, cur_prefix)
            self.blocks.append(ncb)
            index += 1

    def __str__(self):
        return '0x%08x+0x%08x: FD' % (self.start, self.size)

    def showinfo(self, ts='  '):
        for block in self.blocks:
            print ts + str(block)
            block.showinfo(ts + '  ')

    def dump(self):
        if self.full_dump:
            fnprefix = '%s%08x' % (self.prefix, self.start)
            fn = '%s.fd' % fnprefix
            fn = os.path.normpath(fn)
            print 'Dumping FD  to %s' % fn
            dn = os.path.dirname(fn)
            if dn and not os.path.isdir(dn):
                os.makedirs(dn)
            with open(fn, 'wb') as fout:
                fout.write(self.data)

        for block in self.blocks:
            block.dump()
