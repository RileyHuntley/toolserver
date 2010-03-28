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

wtitle=u"User:Emijrp/List of Wikimedians by number of edits"
site=wikipedia.Site('meta', 'meta')
limit=1000
conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT dbname, domain, server, lang, family from wiki where is_closed=0 and (family='commons' or family='wikibooks' or family='wikinews' or family='wikipedia' or family='wikiquote' or family='wikisource' or family='wikispecies' or family='wikiversity' or family='wiktionary');")
result=cursor.fetchall()
users=[]
bots=[]
botssubpage=wikipedia.Page(site, u"%s/Unflagged bots" % wtitle)
if botssubpage.exists():
	for l in botssubpage.get().splitlines():
		t=l.split(";")
		if len(t)==3:
			bots.append([t[0], t[1], t[2]])
	output=botssubpage.get().splitlines()
	output.sort()
	botssubpage.put("\n".join(output), u"BOT - Sorting list")

for row in result:
	#break
	if len(row)==5:
		dbname=row[0]
		domain=row[1]
		server=row[2]
		lang=row[3]
		family=row[4]
		
		
		try:
			t1=time.time()
			conn2 = MySQLdb.connect(host='sql-s%s' % server, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
			cursor2 = conn2.cursor()
			cursor2.execute("select user_name, user_editcount from user where user_editcount!=0 order by user_editcount desc limit %s;" % limit)
			result2=cursor2.fetchall()
			print domain, time.time()-t1, "seconds"
		
			for row2 in result2:
				user_name=unicode(row2[0], "utf-8")
				user_editcount=row2[1]
				users.append([user_editcount, user_name, domain, lang, family])
			cursor2.close()
			conn2.close()
			
			try:
				bots2=tarea000.botList(wikipedia.Site(lang, family))
				for bot in bots2:
					bots.append([lang, family, bot])
			except:
				print "Error while recovering bot list"
		except:
			print "Error", dbname, domain

users.sort()
users.reverse()

#hide users
hidepage=wikipedia.Page(site, u"%s/Anonymous" % wtitle)
m=re.compile(ur"(?i)\[\[\s*User\s*:\s*(?P<user>[^\]\|]+?)\s*[\|\]]").finditer(hidepage.get())
hidden=[]
for i in m:
	hidden.append(i.group("user"))

print len(hidden), "usuarios ocultos"

output=u"{{/begin|%s}}\n<center>\n{| class='wikitable sortable' style='text-align: center;' \n! # !! User !! Project !! Edits" % limit
outputbot=u"{{/begin|%s}}\n<center>\n{| class='wikitable sortable' style='text-align: center;' \n! # !! User !! Project !! Edits" % limit
c=1
cbots=1
for user_editcount, user_name, domain, lang, family in users:
	prefix=u""
	if family in ["commons", "wikispecies"]:
		prefix=family
	else:
		prefix=u"%s:%s" % (family, lang)
	if hidden.count(user_name):
		if bots.count([lang, family, user_name])==0:
			if c<=limit:
				output=u"{{/begin|%s}}\n<center>\n{| class='wikitable sortable' style='text-align: center;' \n! # !! User !! Project !! Edits" % limit
				c+=1
		if cbots<=limit:
			outputbot+=u"\n|-\n| %d || [Placeholder] || %s || %d " % (c, domain, user_editcount)
			cbots+=1
	else:
		if bots.count([lang, family, user_name])==0:
			if c<=limit:
				output+=u"\n|-\n| %d || [[%s:User:%s|%s]] || %s || [[%s:Special:Contributions/%s|%d]] " % (c, prefix, user_name, user_name, domain, prefix, user_name, user_editcount)
				c+=1
		outputbot+=u"\n|-\n| %d || [[%s:User:%s|%s]] || %s || [[%s:Special:Contributions/%s|%d]] " % (c, prefix, user_name, user_name, domain, prefix, user_name, user_editcount)
		if cbots<=limit:
			cbots+=1
	if c>limit and cbots>limit:
		break
output+=u"\n|}\n</center>\n{{/end}}"
outputbot+=u"\n|}\n</center>\n{{/end}}"
wiii=wikipedia.Page(site, wtitle)
wiii.put(output, u"BOT - Updating ranking")
wiii=wikipedia.Page(site, u"%s (bots included)" % wtitle)
wiii.put(output, u"BOT - Updating ranking")

cursor.close()
conn.close()	

