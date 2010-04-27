# -*- coding: utf-8 -*-

# Copyright (C) 2009 emijrp
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gzip
import re
import sys
import md5
import random 
import os

lang = sys.argv[1] #requiere un enwiki-latest-image.sql.gz
file='%swiki-latest-image.sql.gz' % lang
path='/mnt/user-store/'

try:
    f=gzip.open('%s%s' % (path, file), 'r')
except:
    os.system('wget http://download.wikimedia.org/%swiki/latest/%s -O %s%s' % (lang, file, path, file)) #entorno a 700MB
    f=gzip.open('%s%s' % (path, file), 'r')

image_pattern = re.compile(ur'\'([^\']*?)\',(\d+)\,(\d+)\,(\d+)\,')

images_dic = {}
c=0
for line in f:
    m = re.findall(image_pattern, line)
    for i in m:
        c+=1
        if c % 5000 == 0:
            print c
        
        filename = i[0]
        
        try:
            filename = unicode(filename, 'utf-8')
        except:
            continue
        
        size = i[1]
        width = i[2]
        height = i[3]
        
        if not re.search(ur'(?i)\.jpe?g', filename) or width==height or int(width)+int(height)<2000 or int(width)%10==0 or int(height)%10==0:
            continue
        
        key='%s-%s-%s' % (size, width, height)
        if images_dic.has_key(key):
            images_dic[key].append(filename)
        else:
            images_dic[key]=[filename,]
f.close()

f=open('duplicates.txt', 'w')
c=0
for k, v in images_dic.items():
    if len(v)>1:
        c+=1
        if c % 5 == 0:
            f.write('== %d ==\n' % random.randint(1000,9999))
        f.write('<gallery>\n')
        for i in v:
            line='Image:%s\n' % i
            f.write(line.encode('utf-8'))
        f.write('</gallery>\n\n')
print c
f.close()
