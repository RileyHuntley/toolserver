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
 
import wikipedia
import MySQLdb
 
site = wikipedia.Site('es', 'wikipedia')
 
conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf')
cursor = conn.cursor()
cursor.execute('''
/* SLOW_OK */SELECT CONCAT("| [[:Category:",page_title,"]]\n|-")
FROM page
JOIN categorylinks ON cl_to = page_title
WHERE page_id = cl_from
AND page_namespace = 14;
''')
 
query = [unicode(row[0], 'utf-8') for row in cursor.fetchall()]
page_list = []
for i, page in enumerate(query): page_list.append(u'| %d\n%s' % (i + 1, page))
 
report = wikipedia.Page(site, u'Wikipedia:Informes automáticos/Categorías autocontenidas')
report.put(u'{{/begin}}\n\nCategorías autocontenidas. Informe generado a las ~~~~~.\n\n{| class=\"wikitable ' +
u'sortable\" style=\"width:100%; margin:auto;\"\n! #\n! Categoría\n|-\n' + 
'\n'.join(page_list) + '\n|}\n\n{{/end}}', u'BOT - Actualizando informe', None, False)
cursor.close()
conn.close()
 
wikipedia.stopme()
