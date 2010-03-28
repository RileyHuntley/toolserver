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

import re
import sys
import wikipedia
import time, os
import tarea000
import MySQLdb

limit=1000
conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT dbname, domain, server, lang, family from wiki where is_closed=0 and (family='commons' or family='wikibooks' or family='wikinews' or family='wikipedia' or family='wikiquote' or family='wikisource' or family='wikispecies' or family='wikiversity' or family='wiktionary');")
result=cursor.fetchall()
users=[]
for row in result:
	#break
	if len(row)==5:
		dbname=row[0]
		domain=row[1]
		server=row[2]
		lang=row[3]
		family=row[4]
		
		t1=time.time()
		conn2 = MySQLdb.connect(host='sql-s%s' % server, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
		cursor2 = conn2.cursor()
		cursor2.execute("select user_name, user_editcount from user where user_editcount!=0 order by user_editcount desc limit %s;" % limit)
		result2=cursor2.fetchall()
		print domain, time.time()-t1, "seconds"
		
		for row2 in result2:
			user_name=row2[0]
			user_editcount=row2[1]
			users.append([user_editcount, user_name, domain, lang, family])
		cursor2.close()
		conn2.close()

users.sort()
users.reverse()
site=wikipedia.Site('meta', 'meta')
wiii=wikipedia.Page(site, u"User:Emijrp/List of Wikimedians by number of edits")
output=u"{| class='wikitable sortable' \n! # !! User !! Project !! Edits"
c=0
for user_editcount, user_name, domain, lang, family in users:
	c+=1
	output+=u"\n|-\n| %d || [[%s:%s:User:%s|%s]] || %s || [[%s:%s:Special:Contributions/%s|%d]] " % (c, family, lang, user_name, user_name, domain, family, lang, user_name, user_editcount)
	if c == limit:
		break
output+=u"\n|}"
wiii.put(output, u"BOT - Updating ranking")

cursor.close()
conn.close()	

