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
import time
import os

lang='es'
if len(sys.argv)>1:
	lang=sys.argv[1]

file='%swiki-latest-stub-meta-history.xml.gz' % lang
path='/mnt/user-store/stub-meta-history/'

try:
	f=gzip.open('%s%s' % (path, file), 'r')
except:
	os.system('wget http://download.wikimedia.org/%swiki/latest/%s -O %s%s' % (lang, file, path, file)) #entorno a 700MB
	f=gzip.open('%s%s' % (path, file), 'r')

r_page = re.compile(ur'<page>')
r_title = re.compile(ur'<title>(.*?)</title>')
r_pageid = re.compile(ur'<id>(\d+)</id>')
r_rev = re.compile(ur'<revision>')
r_rev_ = re.compile(ur'</revision>')
r_revid = re.compile(ur'<id>(\d+)</id>')
r_timestamp = re.compile(ur'<timestamp>(.*?)</timestamp>')
r_author = re.compile(ur'<(ip|username)>(.*?)</\1>')
r_comment = re.compile(ur'<comment>(.*?)</comment>')

g=gzip.open('%sfetch/fetch-%s.txt.gz' % (path, file.split('.')[0]), 'w')
output='pagetitle;;;pageid;;;revisionid;;;timestamp;;;author;;;comment;;;\n'
output=output.encode('utf-8')
g.write(output)
data={'pagetitle':u'','pageid':u'','revisionid':u'','timestamp':u'','author':u'','comment':u''}
lock1=False #cerrojo para pageid
lock2=False #cerrojo para revid
cpages=0.0 #contadores
crevisions=0.0
limite=1000 #mostrar stats cada...
t1=time.time()
for l in f:
	l=unicode(l, 'utf-8')
	
	#t=temporal
	t=re.findall(r_title, l)
	if t:
		data['pagetitle']=t[0] #actualizamos
		lock1=True #justamente despues viene el pageid
		cpages+=1
		continue
	
	if lock1:
		t=re.findall(r_pageid, l)
		if t:
			data['pageid']=t[0] #actualizamos
			lock1=False
			continue
	
	t=re.findall(r_rev, l)
	if t:
		lock2=True
		continue
	
	if lock2:
		t=re.findall(r_revid, l)
		if t:
			data['revisionid']=t[0] #actualizamos
			lock2=False
			continue
	
	t=re.findall(r_timestamp, l)
	if t:
		data['timestamp']=t[0] #actualizamos
		continue
	
	t=re.findall(r_author, l)
	if t:
		data['author']=t[0][1] #actualizamos
		continue
	
	t=re.findall(r_comment, l)
	if t:
		data['comment']=t[0] #actualizamos
		continue
	
	#cada vez que encuentra un </revision>, debe guardar una linea con los datos actuales
	t=re.findall(r_rev_, l)
	if t:
		crevisions+=1
		output='%s;;;%s;;;%s;;;%s;;;%s;;;%s;;;\n' % (data['pagetitle'], data['pageid'], data['revisionid'], data['timestamp'], data['author'], data['comment'])
		#output='%s;%s;%s;%s;%s;%s;\n' % (data['pagetitle'], data['pageid'], data['revisionid'], data['timestamp'], data['author'], data['comment'])
		output=output.encode('utf-8')
		g.write(output)
		if crevisions % limite == 0:
			speed=limite/(time.time()-t1)
			print u'Pages: %d | Revs: %d | / = %.2f | %.2f revs/s | %d min every 1M ' % (cpages, crevisions, (crevisions/cpages), speed, (1000000/speed/60))
			t1=time.time()
		#blanqueamos datos de la revision
		data['revisionid']=u''
		data['timestamp']=u''
		data['author']=u''
		data['comment']=u''

g.close()
f.close()
