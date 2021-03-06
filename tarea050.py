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

""" Update a template with my user accounts edits """

import re
import time
import urllib

import wikipedia

def main():
    """ Update a template with my user accounts edits """
    
    eswiki = wikipedia.Site('es', 'wikipedia')
    users = ['AVBOT', 'BOTijo', 'Emijrp', 'Emijrpbot', 'Poc-oban', 'Toolserver']
    path = "http://toolserver.org/~vvv/sulutil.php?user="
    salida = u"{{#switch:{{{1|}}}"
    total = 0
    oldtotal = 0 #total anterior
    for user in users:
        url = path + user
        f = urllib.urlopen(url, 'r')
        raw = f.read()
        m = re.compile(ur"Total editcount: <b>(?P<useredits>\d+)</b>").finditer(raw)
        for j in m:
            salida += u"\n|%s=%s" % (user, j.group("useredits"))
            edits = j.group("useredits")
            total += int(edits)
        f.close()
        print user, edits
        time.sleep(5)
    salida += u"\n|Total=%d\n|%d}}" % (total, total)

    editcount = wikipedia.Page(eswiki, u"User:Emijrp/Editcount")
    #evitamos regresiones en el contador
    oldtotal = int(editcount.get().split("Total=")[1].split("\n")[0])
    
    print "Total:", total, "Oldtotal:", oldtotal
    if total > oldtotal:
        oldpage = wikipedia.Page(eswiki, u"User:Emijrp/Editcount/Old")
        oldpage.put(editcount.get(), u"BOT - Datos de la versión anterior de [[User:Emijrp/Editcount]]")    
        editcount.put(salida, u"BOT - Actualizando ediciones globales de %s: %d" % (", ".join(users), total))

if __name__ == "__main__":
    main()
