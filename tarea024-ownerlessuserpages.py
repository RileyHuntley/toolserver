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

import re
import wikipedia
import MySQLdb
import datetime

report_template = u'''
{{/begin}}

Páginas de usuario sin dueño; actualizado a las <onlyinclude>~~~~~</onlyinclude>.

{| class="wikitable sortable plainlinks" style="width:100%%; margin:auto;"
|- style="white-space:nowrap;"
! #
! Página
! Longitud
|-
%s
|}

{{/end}}
'''

site = wikipedia.Site('es', 'wikipedia')

conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf')
cursor = conn.cursor()
cursor.execute('''
/* ownerlessuserpages.py SLOW_OK */
SELECT
  page_namespace,
  ns_name,
  page_title,
  page_len
FROM page
JOIN toolserver.namespace
ON page_namespace = ns_id
AND dbname = 'eswiki_p'
LEFT JOIN user
ON user_name = REPLACE(page_title, '_', ' ')
WHERE page_namespace IN (2,3)
AND page_is_redirect = 0
AND page_title NOT LIKE "%/%"
AND page_title NOT RLIKE "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
AND user_name IS NULL;
''')

i = 1
output = []
for row in cursor.fetchall():
    page_namespace = row[0]
    ns_name = u'%s' % unicode(row[1], 'utf-8')
    page_title = u'[[%s:%s]]' % (ns_name, unicode(row[2], 'utf-8'))
    page_len = row[3]
    table_row = u'''| %d
| %s
| %s
|-''' % (i, page_title, page_len)
    output.append(table_row)
    i += 1

cursor.execute('SELECT UNIX_TIMESTAMP() - UNIX_TIMESTAMP(rc_timestamp) FROM recentchanges ORDER BY rc_timestamp DESC LIMIT 1;')
rep_lag = cursor.fetchone()[0]

report = wikipedia.Page(site, u'Wikipedia:Informes automáticos/Páginas de usuario sin dueño')
report.put(report_template % ('\n'.join(output)), u'BOT - Actualizando informe', True, False)
cursor.close()
conn.close()

wikipedia.stopme()