#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright 2008 bjweeks, MZMcBride

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import MySQLdb, wikipedia

report_title = 'Wikipedia:Informes automáticos/Páginas con más ediciones'

report_template = u'''
Páginas con más ediciones; actualizado a las ~~~~~.

{| class="wikitable sortable" style="width:100%%; margin:auto;"
|- style="white-space:nowrap;"
! #
! [[Wikipedia:Espacio de nombres|ID]]
! Página
! Ediciones
|-
%s
|}
'''

conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf')
cursor = conn.cursor()
cursor.execute('''
/* mostrevisions.py SLOW_OK */
SELECT
  page_namespace,
  ns_name,
  page_title,
  COUNT(*)
FROM revision
JOIN page ON page_id = rev_page
JOIN toolserver.namespace ON page_namespace = ns_id
AND dbname = 'eswiki_p'
GROUP BY page_namespace, page_title
ORDER BY COUNT(*) DESC
LIMIT 500;
''')

i = 1
output = []
ns_count_tcol = 0
ns_count_r_tcol = 0
for row in cursor.fetchall():
    page_namespace = row[0]
    ns_name = u'%s' % unicode(row[1], 'utf-8')
    page_title = u'%s' % unicode(row[2], 'utf-8')
    if page_namespace == 6 or page_namespace == 14:
        page_title = '[[:%s:%s]]' % (ns_name, page_title)
    elif ns_name:
        page_title = '[[%s:%s]]' % (ns_name, page_title)
    else:
        page_title = '[[%s]]' % (page_title)
    revisions = row[3]
    table_row = u'''| %d
| %s
| %s
| %s
|-''' % (i, page_namespace, page_title, revisions)
    output.append(table_row)
    i += 1

cursor.execute('SELECT UNIX_TIMESTAMP() - UNIX_TIMESTAMP(rc_timestamp) FROM recentchanges ORDER BY rc_timestamp DESC LIMIT 1;')
rep_lag = cursor.fetchone()[0]

report = wikipedia.Page(wikipedia.Site('es', 'wikipedia'), report_title)
report_text = report_template % ('\n'.join(output))
report.put(report_text, u'BOT - Actualizando informe')

cursor.close()
conn.close()