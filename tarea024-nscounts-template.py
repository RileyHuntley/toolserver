#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright 2008 bjweeks, valhallasw, MZMcBride

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

import wikipedia
import MySQLdb
import datetime

report_template = u'''{{#switch:{{{1|0}}}
%s
| T | Total | All =
{{#switch:{{{2|NR}}}
| NR = %s
| R = %s
| T = %s}}
| date = ~~~~~
}}<noinclude>{{documentación}}</noinclude>'''

site = wikipedia.getSite()

conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf')
cursor = conn.cursor()
cursor.execute('''
/* nscounts.py SLOW_OK */
SELECT
  page_namespace,
  ns_name,
  MAX(notredir),
  MAX(redir)
FROM (
  SELECT page.page_namespace,
         IF( page_is_redirect, COUNT(page.page_namespace), 0 ) AS redir,
         IF( page_is_redirect, 0, COUNT(page.page_namespace)) AS notredir
  FROM page
  GROUP BY page_is_redirect, page_namespace
  ORDER BY page_namespace, page_is_redirect
) AS pagetmp
JOIN toolserver.namespace ON page_namespace = ns_id AND dbname = 'eswiki_p'
GROUP BY page_namespace;
''')

i = 1
output = []
ns_count_tcol = 0
ns_count_r_tcol = 0
for row in cursor.fetchall():
    page_namespace = row[0]
    ns_name = row[1]
    if ns_name:
        ns_name = u'%s' % unicode(ns_name, 'utf-8')
    else:
        ns_name = '(Principal)'
    ns_count = row[2]
    if ns_count:
        ns_count = ns_count
    else:
        ns_count = '0'
    ns_count_r = row[3]
    if ns_count_r:
        ns_count_r = ns_count_r
    else:
        ns_count_r = '0'
    ns_count_trow = int(ns_count) + int(ns_count_r)
    ns_count_tcol += int(ns_count)
    ns_count_r_tcol += int(ns_count_r)
    ns_count_gtotal = ns_count_tcol + ns_count_r_tcol
    table_row = u'''| %s | %s = 
{{#switch:{{{2|NR}}}
| NR = %s
| R = %s
| T = %s}}''' % (page_namespace, ns_name, ns_count, ns_count_r, ns_count_trow)
    output.append(table_row)
    i += 1

cursor.execute('SELECT UNIX_TIMESTAMP() - UNIX_TIMESTAMP(rc_timestamp) FROM recentchanges ORDER BY rc_timestamp DESC LIMIT 1;')
rep_lag = cursor.fetchone()[0]

report = wikipedia.Page(site, u'Plantilla:Páginas')
report.put(report_template % ('\n'.join(output), ns_count_tcol, ns_count_r_tcol, ns_count_gtotal), u'BOT - Actualizando plantilla', None, False)
cursor.close()
conn.close()

wikipedia.stopme()
