#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO: al parecer tarda un rato en ejecutarse, por lo que el date_add de mysql va desplazándose, corregir y poner la hora fija

import datetime
import sys
from tool0000 import *
import os
#import Gnuplot
import MySQLdb

tool_id="0025"
tool_title="Last hour activity"
tool_desc=""
tool_path=generateToolPath(tool_id)
tool_archive_path=generateToolArchivePath(tool_id)

if not os.path.exists(tool_path):
	os.makedirs(tool_path)

#if not os.path.exists(tool_archive_path):
#	os.makedirs(tool_archive_path)

conn = MySQLdb.connect(host='sql-s1', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT lang, family, CONCAT('sql-s', server) AS dbserver, dbname FROM toolserver.wiki WHERE 1;")
result=cursor.fetchall()
users=[]
limit=100
total=0.0
for row in result:
	lang=row[0]
	family=row[1]
	dbserver=row[2]
	dbname=row[3]
	
	try:
		conn2 = MySQLdb.connect(host=dbserver, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
		cursor2 = conn2.cursor()
		print "OK:", dbserver, dbname
		cursor2.execute("select rc_user_text, count(*) as edits from recentchanges where rc_timestamp>=date_add(now(), interval -1 hour) and (rc_type=0 or rc_type=1) group by rc_user_text order by edits desc")
		result2=cursor2.fetchall()
		for row2 in result2:
			username=unicode(row2[0], "utf-8")
			edits=int(row2[1])
			total+=edits
			
			users.append([edits, lang, family, username])
		cursor2.close()
		conn2.close()
	except:
		print "Error in", dbserver, dbname
	
users.sort()
users.reverse()

output=getPHPHeader(tool_id, tool_title)
output+=u""
c=0
output+=u"<center>\n<table>\n<tr><th>#</th><th>Project</th><th>User</th><th>Edits</th><th>%</th></tr>\n"
for edits, lang, family, username in users:
	if family=="commons":
		wikiurl="commons.wikimedia.org"
	else:
		wikiurl="%s.%s.org" % (lang, family)
	c+=1
	if c<=limit:
		output+=u"<tr><td>%s</td><td>%s</td><td><a href='http://%s/wiki/User:%s'>%s</a></td><td><a href='http://%s/wiki/Special:Contributions/%s'>%s</a></td><td>%.3f%%</td></tr>\n" % (c, wikiurl, wikiurl, username, username, wikiurl, username, edits, edits/(total/100))


output+=u"<tr><td></td><td></td><td>%s users</td><td>%.0f</td><td>100%%</td></tr>\n" % (len(users), total)
output+=u"</table>\n</center>\n"

#output+=u"<ul>\n<li><tt><a href=\"%s\">%s</a></tt> - %s</li>\n</ul>" % (filename, filename, filedesc)
output+=getPHPFooter()
filename="%s/index.php" % tool_path
writeToFile(filename, output)

cursor.close()
conn.close()


