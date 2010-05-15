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

# clear;python svn-gource.py --filter-dirs gourceforwiki.log > gourceforwikib.log;gource --log-format custom gourceforwikib.log -s 4

import wikipedia,re,sys,os,gzip,time
import MySQLdb
import math
import datetime

start='<?xml version="1.0"?>\n<log>\n'
end='</log>'

f=open("gourceforwiki.log", "w")
f.write(start)
conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT rc_id, rc_user_text, rc_timestamp, rc_title, rc_comment from recentchanges where rc_namespace=0 and rc_deleted=0 order by rc_timestamp desc limit 30000;")
result=cursor.fetchall()
for row in result:
    if len(row)==5:
	rc_id=row[0]
	rc_author=row[1]
	rc_timestamp=t=row[2]
	rc_timestamp="%s-%s-%sT%s:%s:%s.000000Z" % (t[0:4], t[4:6], t[6:8], t[8:10], t[10:12], t[12:14])
	#print rc_timestamp
	rc_title=row[3]
	rc_comment=""#row[4]

	action="M"
	
	logentry="""<logentry
	   revision="%d">
	<author>%s</author>
	<date>%s</date>
	<paths>
	<path
	   kind=""
	   action="%s">%s</path>
	</paths>
	<msg>%s</msg>
	</logentry>\n""" % (rc_id, rc_author, rc_timestamp, action, rc_title, rc_comment)
	
	logentry=re.sub("&", "&amp;", logentry)
	logentry=re.sub("_", " ", logentry)
	#print logentry
	try:
		f.write(logentry)
	except:
		try:
			f.write(logentry)
		except:
			print 'Error'
			pass

conn.close()
cursor.close()
f.write(end)
f.close()

