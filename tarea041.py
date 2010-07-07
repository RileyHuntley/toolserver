#!/usr/bin/env python
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

""" Update a projects list """

import MySQLdb
import re

import wikipedia

def main():
    """ Update a projects list """
    site = wikipedia.Site("es", "wikipedia")

    conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute('SELECT distinct page_title from page where page_namespace=100 and page_is_redirect=0 and page_title not regexp "/";')
    result = cursor.fetchall()
    portales = []
    for row in result:
        if len(row) == 1:
            portal = re.sub("_", " ", unicode(row[0], "utf-8"))
            portales.append(portal)

    page = wikipedia.Page(site, u"Wikiproyecto:Portales/Lista")
    output = u"Portales que existen en [[Wikipedia en español]]:"
    for portal in portales:
        output += u"\n# [[Portal:%s|%s]]" % (portal, portal)
    if output != page.get():
        page.put(output, u"BOT - Actualizando lista de portales [%s]" % len(portales))
    page = wikipedia.Page(site, u"Wikiproyecto:Portales/Número")
    output = u"%s<noinclude>{{documentación}}</noinclude>" % len(portales)
    if output != page.get():
        page.put(output, u"BOT - Actualizando número de portales [%s]" % len(portales))

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()

