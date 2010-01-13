#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import sys
from tool0000 import *
import os
#import Gnuplot
import MySQLdb

tool_id="0027"
tool_title=u"Proyectos en peligro de extinción"
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
lastedits=[]
limit=10000
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
		cursor2.execute("select rc_user_text, rc_timestamp, rc_this_oldid as edits from recentchanges where rc_namespace>=0 order by rc_timestamp desc limit 1")
		result2=cursor2.fetchall()
		for row2 in result2:
			username=unicode(row2[0], "utf-8")
			timestamp=row2[1]
			oldid=row2[2]
			
			lastedits.append([timestamp, lang, family, username, oldid])
		cursor2.close()
		conn2.close()
	except:
		print "Error in", dbserver, dbname

lastedits.sort()

output=getPHPHeader(tool_id, tool_title)
output+=u""
c=0
output+=u"<center>\n<table>\n<tr><th>#</th><th>Project</th><th>User</th><th>Timestamp</th></tr>\n"
for timestamp, lang, family, username, oldid in lastedits:
	if family=="commons":
		wikiurl="commons.wikimedia.org"
	elif family in ["wikipedia", "wiktionary", "wikiquote", "wikibooks", "wikisource", "wikinews", "wikiversity"]:
		wikiurl="%s.%s.org" % (lang, family)
	else:
		wikiurl="%s:%s" % (lang, family)
	c+=1
	if c<=limit:
		date=datetime.datetime(year=int(timestamp[:4]), month=int(timestamp[4:6]), day=int(timestamp[6:8]), hour=int(timestamp[8:10]), minute=int(timestamp[10:12]), second=int(timestamp[12:14]))
		delta=datetime.datetime.now()-date
		output+=u"<tr><td>%s</td><td>%s</td><td><a href='http://%s/wiki/User:%s'>%s</a></td><td><a href='http://%s/w/index.php?oldid=%s&diff=prev'>%s</a></td><td>%s days</td></tr>\n" % (c, wikiurl, wikiurl, username, username, wikiurl, oldid, date.isoformat(), delta.days)
	else:
		break

output+=u"</table>\n</center>\n"

#output+=u"<ul>\n<li><tt><a href=\"%s\">%s</a></tt> - %s</li>\n</ul>" % (filename, filename, filedesc)
output+=getPHPFooter()
filename="%s/index.php" % tool_path
writeToFile(filename, output)

cursor.close()
conn.close()

