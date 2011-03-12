# -*- coding: utf-8 -*-

import gzip
import re
import time

rev_r = re.compile(r'<revision>')
path = '/mnt/user-store/emijrp/enwiki-20101011-stub-meta-history.xml.gz'
f = gzip.GzipFile(path, 'rb')
l = f.readline()
t1 = time.time()
limit = 1000
c = 1
ok = False
while l:
    if re.findall(rev_r, l):
        c += 1
        ok = True
    if c % limit == 0 and ok:
        print 'Analysed %d edits. Speed = %d edits/sec' % (c, (1.0/(time.time()-t1))*limit)
        ok = False
        t1 = time.time()
    l = f.readline()
f.close()
