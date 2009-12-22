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

import time
from xml.etree.cElementTree import iterparse
import bz2, sys

#llamado con 7za e -so eowiki-20091128-pages-meta-history.xml.7z | python stubmetahistory-fetch-celementtree.py 

#source=open("zuwiki-latest-pages-meta-history.xml", 'r')
source=sys.stdin
g=open("zzzfetched.txt", "w")

context = iterparse(source, events=("start", "end"))
context = iter(context)

page_title=''
page_id=''
rev_id=''
rev_timestamp=''
rev_author=''
rev_comment=''
rev_text=''
lock_page_id=False
lock_revision_id=False
t1=time.time()
limit=1000
cpages=crevisions=0.0
for event, elem in context:
	tag=elem.tag.split("}")[1]	
	
	if event=="start" and tag=="page":
		lock_page_id=True
	if event=="start" and tag=="revision":
		lock_revision_id=True
	
	if tag=="id":
		if lock_page_id:
			page_id=elem.text
			lock_page_id=False
		if lock_revision_id:
			rev_id=elem.text
			lock_revision_id=False
	if tag=="title":
		page_title=elem.text
	
	if tag=="timestamp":
		rev_timestamp=elem.text
	
	if tag=="username" or tag=="ip":
		rev_author=elem.text
	
	if tag=="comment":
		rev_comment=elem.text

	if tag=="text":
		if elem.text:
			rev_text=elem.text
		else:
			rev_text=''
	if event=="end" and tag=="page":
		cpages+=1
		elem.clear()
		
	if event=="end" and tag=="revision":
		crevisions+=1
		elem.clear()
		if crevisions % limit == 0:
			print u'Pages: %d | Revisions: %d | Rev/pag = %.2f | %.2f pags/s | %.2f revs/s' % (cpages, crevisions, (crevisions/cpages), cpages/(time.time()-t1), (crevisions/(time.time()-t1)))		
		#output rev
		output='%s	%s	%s	%s	%s	%s	%s\n' % (page_title, page_id, rev_id, rev_timestamp, rev_author, rev_comment, len(rev_text))
		g.write(output.encode('utf-8'))
		#print page_title, page_id, rev_id, rev_timestamp, len(rev_text)
		#limpiamos
		rev_id=''
		rev_timestamp=''
		rev_author=''
		rev_comment=''
		rev_text=''

source.close()
g.close()




