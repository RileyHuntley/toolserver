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

import datetime
import os, re, wikipedia

site=wikipedia.Site("es", "wikipedia")

#discusiones mas activas
os.system('mysql -h sql-s3 -e "use eswiki_p;select count(*) as count, rc_title from recentchanges where rc_timestamp>=date_add(now(), interval -3 day) and rc_namespace=1 group by rc_title order by count desc limit 25;" > /home/emijrp/temporal/tarea006data')

f=open('/home/emijrp/temporal/tarea006data', 'r')
sql=unicode(f.read(), 'utf-8')
m=re.compile(ur"(\d+)\s+(.*)").finditer(sql)

page=wikipedia.Page(site, "Template:DiscusionesActivas")
s=u"<div class='plainlinks'>\n{| class='wikitable' style='width: {{{ancho|275px}}};clear: right;float: right;margin: 0 0 1em 1em;text-align: center;'\n! Discusiones más activas [[Image:FireIcon.svg|18px]]\n! Ediciones\n"
c=1
ss=""
for i in m:
    ed=str(i.group(1))
    art_=i.group(2)
    art=re.sub("_", " ", art_)
    if not re.search(u"Candidatura a destacado", art):
        if c<=5:
            ss+=u"|-\n| [[Discusión:%s|%s]] || [http://es.wikipedia.org/w/index.php?title=Discusión:%s&action=history %s] \n" % (art,art,art_,ed)
        c+=1
s+=ss
s+=u"|-\n| colspan='2' | <small>Actualizado: {{subst:CURRENTTIME}} (UTC) del {{subst:CURRENTDAY}} de {{subst:CURRENTMONTHNAME}} de {{subst:CURRENTYEAR}}</small>\n"
s+=u"|}\n</div>"
wikipedia.output(s)
if ss: #evita errores de db 
    page.put(s, u"BOT - Actualizando plantilla")
f.close()
