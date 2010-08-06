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

""" Update a list of newbies """

import MySQLdb
import re

import wikipedia

def main():
    """ Update a list of newbies """
    
    eswiki = wikipedia.Site('es', 'wikipedia')
    dias = 7
    conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute("SELECT user_name from user where user_editcount>=%d and user_registration>=date_add(now(), interval -%d day) and user_name not in (select ipb_address from ipblocks) order by user_editcount desc;" % (dias*2, dias))
    result=cursor.fetchall()
    users = []
    for row in result:
        user_name = unicode(row[0], "utf-8")
        users.append(user_name)
    
    output = u"La siguiente es una lista con los usuarios que han llegado en los últimos %d días y han editado algunas cosas, pero todavía nadie les ha saludado. Es posible que interese darles la bienvenida después de revisar sus contribuciones. Ejemplo de bienvenida: <code>{<nowiki></nowiki>{su<nowiki></nowiki>bst:Usuario:Emijrp/Bienvenida.css}<nowiki></nowiki>} --~~<nowiki></nowiki>~~</code>\n" % (dias)
    for user_name in users:
        talk = wikipedia.Page(eswiki, u"User talk:%s" % user_name)
        if not talk.exists():
            output += u"# [[Usuario:%s|%s]] ([[Usuario Discusión:%s|discusión]] · [[Special:Contributions/%s|contribuciones]])\n" % (user_name, user_name, user_name, user_name)
    novatos = wikipedia.Page(eswiki, u"User:Emijrp/Recién llegados")
    novatos.put(output, u"BOT - Actualizando lista de recién llegados")

if __name__ == "__main__":
    main()
