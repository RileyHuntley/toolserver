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

import os
import wikipedia
import re
import datetime
import MySQLdb

for lang in ["en", "es"]:
	username="%swikieditednow" % lang
	password=""
	f=open("/home/emijrp/.my.cnf2", "r")
	raw=f.read()
	f.close()
	m=re.findall(ur'%s = *"(.*)"' % username, raw)
	password=m[0]

	#what host?
	conn = MySQLdb.connect(host='sql-s1', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
	cursor = conn.cursor()
	cursor.execute("SELECT CONCAT('sql-s', server) FROM toolserver.wiki WHERE dbname='%swiki_p';" % lang)
	host=cursor.fetchall()[0][0]

	#conexión a la db
	try:
		conn = MySQLdb.connect(host=host, db='%swiki_p' % lang, read_default_file='~/.my.cnf', use_unicode=True)
		cursor = conn.cursor()
		cursor.execute("select rc_title, count(*) as edits from recentchanges where rc_namespace=0 and rc_deleted=0 and rc_timestamp>=date_add(now(), interval -1 hour) group by rc_title order by edits desc limit 1")
		[page_title_, edits]=cursor.fetchall()[0]

		page_title=re.sub("_", " ", page_title_)
		if page_title_[-1]==')':
			page_title_+="_"
		msg=u"%s (%s edits) → http://%s.wikipedia.org/wiki/%s #wikipedia" % (page_title, edits, lang, page_title_)
		orden='curl -u %s:%s -d status="%s" http://twitter.com/statuses/update.json' % (username, password, msg.encode("utf-8"))
		os.system(orden)
	except:
		pass
	

