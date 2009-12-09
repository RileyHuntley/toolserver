#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/home/emijrp/public_html/tool0000')
import tool0000
import os

tool_id="0001"
tool_title="Replicated databases in Toolserver"
tool_desc="Some info about all replicated databases in Toolserver. Grouped by family project and sorted by size."
path=tool0000.generateToolPath(tool_id)

#dbs=tool0000.loadAllDatabasesFromNoc()

families=tool0000.getAllWikimediaFamilies() #to simplify
queries=[
'mysql -h eswiki-p.db.toolserver.org -e "USE eswiki_p;SELECT lang, family, CONCAT(\'sql-s\', server) AS dbserver, dbname, size, CONCAT(\'http://\', domain, script_path, \'api.php\') AS url FROM toolserver.wiki WHERE 1 ORDER BY size DESC;"', #original query from https://wiki.toolserver.org/view/Database_access
]
filenames=[
"all-databases-sorted-by-size.txt",
]
descriptions=[
u"Todas las bases de datos replicadas ordenadas por tamaño",
]

for family in families:
	queries.append("mysql -h eswiki-p.db.toolserver.org -e \"USE eswiki_p;SELECT lang, family, CONCAT('sql-s', server) AS dbserver, dbname, size, CONCAT('http://', domain, script_path, 'api.php') AS url FROM toolserver.wiki WHERE family = '%s' ORDER BY size DESC;\"" % family)
	filenames.append("%s-databases-sorted-by-size.txt" % family)
	descriptions.append(u"Todas las bases de datos replicadas de proyectos <b>%s</b> por tamaño" % family)

output=tool0000.getPHPHeader()
output+=u"<h2>%s (Tool #%s)</h2>" % (tool_title, tool_id)
f=open("%sall-databases-sorted-by-size.txt" % path, "r")
total=len(f.readlines())
f.close()
output+=u"En Toolserver hay un total de %s bases de datos replicadas:" % (total-1)
output+=u"<ul>"

for family in families:
	f=open("%s%s-databases-sorted-by-size.txt" % (path, family), "r")
	subtotal=len(f.readlines())-1
	f.close()
	output+=u"<li>%s %s</li>" % (subtotal, family)

output+=u"</ul>"

output+=u"<h3>Análisis descargables</h3>"
output+=u"<ul>"
for i in range(0, len(queries)):
	os.system('%s > %s%s' % (queries[i], path, filenames[i]))
	output+=u"<li><tt><a href=\"%s\">%s</a></tt> - %s<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<small>Consulta SQL: <tt>%s</tt></small></li>" % (filenames[i], filenames[i], descriptions[i], queries[i])
output+=u"</ul>"

output+=getPHPFooter()
f=open("%sindex.php" % path, "w")
f.write(output.encode("utf-8"))
f.close()




