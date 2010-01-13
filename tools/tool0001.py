#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import sys
from tool0000 import *
import os

tool_id="0001"
tool_title="Replicated databases in Toolserver"
tool_desc="Some info about all replicated databases in Toolserver. Grouped by family project and sorted by size."
tool_path=generateToolPath(tool_id)
tool_archive_path=generateToolArchivePath(tool_id)

if not os.path.exists(tool_path):
	os.makedirs(tool_path)

if not os.path.exists(tool_archive_path):
	os.makedirs(tool_archive_path)

#dbs=loadAllDatabasesFromNoc()

families=getAllWikimediaFamilies() #to simplify
queries=[
'mysql -h eswiki-p.db.toolserver.org -e "USE eswiki_p;SELECT lang, family, CONCAT(\'sql-s\', server) AS dbserver, dbname, size, CONCAT(\'http://\', domain, script_path, \'api.php\') AS url FROM toolserver.wiki WHERE 1 ORDER BY size DESC;"', #original query from https://wiki.toolserver.org/view/Database_access
]
filenames=[
"all-replicated-databases-sorted-by-size.txt",
]
descriptions=[
u"Todas las bases de datos replicadas ordenadas por tamaño",
]

for family in families:
	queries.append(""" mysql -h eswiki-p.db.toolserver.org -e "USE eswiki_p;SELECT lang, family, CONCAT('sql-s', server) AS dbserver, dbname, size, CONCAT('http://', domain, script_path, 'api.php') AS url FROM toolserver.wiki WHERE family = '%s' ORDER BY size DESC;" """ % family)
	filenames.append("%s-replicated-databases-sorted-by-size.txt" % family)
	descriptions.append(u"Todas las bases de datos replicadas de proyectos <b>%s</b> por tamaño" % family)

output=getPHPHeader(tool_id, tool_title)
try:
	f=open("%s/all-replicated-databases-sorted-by-size.txt" % tool_path, "r")
	total=len(f.readlines())
	f.close()
except:
	total=0
output+=u"En Toolserver hay un total de %s bases de datos replicadas. A continuación se ordenan por familias:" % (total-1)
output+=u"<ul>"

for family in families:
	try:
		f=open("%s/%s-replicated-databases-sorted-by-size.txt" % (tool_path, family), "r")
		subtotal=len(f.readlines())-1
		f.close()
	except:
		subtotal=0
	output+=u"<li>%s %s</li>" % (subtotal, family)

output+=u"</ul>"

output+=u"<h3>Análisis descargables</h3>"
output+=u"<ul>"
for i in range(0, len(queries)):
	os.system('%s > %s/%s' % (queries[i], tool_path, filenames[i]))
	os.system('cp %s/%s %s/%s-%s' % (tool_path, filenames[i], tool_archive_path, datetime.date.today().isoformat(), filenames[i]))
	#output+=u"<li><tt><a href=\"%s\">%s</a></tt> - %s<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<small>Consulta SQL: <tt>%s</tt></small></li>" % (filenames[i], filenames[i], descriptions[i], queries[i])
	output+=u"<li><tt><a href=\"%s\">%s</a></tt> - %s</li>" % (filenames[i], filenames[i], descriptions[i])
output+=u"</ul>"

output+=getPHPFooter()
filename="%s/index.php" % tool_path
writeToFile(filename, output)


