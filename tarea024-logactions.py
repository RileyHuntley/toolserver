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
import operator
import MySQLdb
import wikipedia

report_title = u'Wikipedia:Informes automáticos/Usuarios por acciones de log'

conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()

def get_stats(type, action):
    cursor.execute(u'''
        /* logactions.py SLOW_OK */
        SELECT
          user_name,
          COUNT(log_timestamp)
        FROM logging
        JOIN user_ids
        ON user_id = log_user
        WHERE log_type = "%s"
        AND log_action = "%s"
        GROUP BY log_user;
    ''' % (type, action))
    return cursor.fetchall()

query_list = [
    {'name': u'Borrados', 'short_name': 'DL', 'type': 'delete', 'action': 'delete'},
    {'name': u'Restauraciones', 'short_name': 'UD', 'type': 'delete', 'action': 'restore'},
    {'name': u'Revision deletions', 'short_name': 'RD', 'type': 'delete', 'action': 'revision'},
    {'name': u'Event suppressions', 'short_name': 'ES', 'type': 'suppress', 'action': 'event'},
    {'name': u'Protecciones', 'short_name': 'PT', 'type': 'protect', 'action': 'protect'},
    {'name': u'Desprotecciones', 'short_name': 'UP', 'type': 'protect', 'action': 'unprotect'},
    {'name': u'Modificaciones de protección', 'short_name': 'PM', 'type': 'protect', 'action': 'modify'},
    {'name': u'Bloqueos', 'short_name': 'BL', 'type': 'block', 'action': 'block'},
    {'name': u'Desbloqueos', 'short_name': 'UB', 'type': 'block', 'action': 'unblock'},
    {'name': u'Modificaciones de bloqueos', 'short_name': 'BM', 'type': 'block', 'action': 'reblock'},
    {'name': u'Renombramiento de usuarios', 'short_name': 'UR', 'type': 'renameuser', 'action': 'renameuser'},
    {'name': u'User rights modifications', 'short_name': 'RM', 'type': 'rights', 'action': 'rights'},
    {'name': u'Bot flaggings', 'short_name': 'BF', 'type': 'makebot', 'action': 'grant'},
    {'name': u'Bot de-flaggings', 'short_name': 'BD', 'type': 'makebot', 'action': 'revoke'},
    {'name': u'Whitelistings', 'short_name': 'WL', 'type': 'gblblock', 'action': 'whitelist'},
    {'name': u'De-whitelistings', 'short_name': 'DW', 'type': 'gblblock', 'action': 'dwhitelist'}
]
user_stats = {}

for query in query_list:
    stats_query = get_stats(query['type'], query['action'])
    query['len'] = len(stats_query)
    for row in stats_query:
        user = unicode(row[0], 'utf-8')
        count = row[1]
        if user not in user_stats:
            user_stats[user] = {query['name']: count}
        else:
            user_stats[user][query['name']] = count
            
output = u''

report_template = u'Usuarios por acciones de log; actualizado a las ~~~~~.\n%s'

table_template = u'''
== %s ==
{| class="wikitable sortable" style="width:23em;"
|- style="white-space:nowrap;"
! #
! Usuario
! Número
|-
%s
|}
'''
            
for query in query_list:
    stat_dict = {}
    for user,stats in user_stats.iteritems():
        if query['name'] in stats:
            stat_dict[user] = stats[query['name']]
    stats = sorted(stat_dict.iteritems(), key=operator.itemgetter(1), reverse=True)[0:25]
    rows = []
    i = 1
    for user, count in stats:
        rows.append(u'''| %d\n| %s\n| %s\n|-''' % (i, user, count))
        i += 1
    output += table_template % (query['name'], '\n'.join(rows))

master_table_template = u'''
== Total ==
{| class="wikitable sortable" style="width:100%%; margin:auto;"
|- style="white-space:nowrap;"
! #
! Usuario
%s
! Total
|-
%s class="sortbottom"
! colspan="2" | Total
%s
|}
'''

new_query_list = []

for query in query_list:
    if query['len'] > 25:
        new_query_list.append(query)
        
query_list = new_query_list

rows = []
totals = dict([(query['name'], 0) for query in query_list])
totals['total'] = 0
i = 1
user_stats_sorted = sorted(user_stats.iteritems(), key=operator.itemgetter(0))
for user,stats in user_stats_sorted:
    row = []
    total = 0
    row.append(str(i))
    row.append(user)
    for query in query_list:
        if query['name'] in stats:
            row.append(str(stats[query['name']]))
            total += stats[query['name']]
            totals[query['name']] += stats[query['name']]
            totals['total'] += stats[query['name']]
        else:
            row.append('0')
    row.append(str(total))
    rows.append('| %s \n|-' % ('\n| '.join(row)))
    i += 1

output += master_table_template % (
    '\n'.join([u'! <span title="%s">%s</span>' % (query['name'], query['short_name']) for query in query_list]), 
    '\n'.join(rows),
    '\n'.join([u'! style="text-align:left;" | %d' % totals[query['name']] for query in query_list]) + u'\n! style="text-align:left;" | %d' % totals['total']
)
    
cursor.execute('SELECT UNIX_TIMESTAMP() - UNIX_TIMESTAMP(rc_timestamp) FROM recentchanges ORDER BY rc_timestamp DESC LIMIT 1;')
rep_lag = cursor.fetchone()[0]

final_output = report_template % (output)
report = wikipedia.Page(wikipedia.Site('es', 'wikipedia'), report_title)
report.put(final_output, u'BOT - Actualizando informe')

cursor.close()
conn.close()