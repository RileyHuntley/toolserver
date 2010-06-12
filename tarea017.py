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

import wikipedia, re
import pagegenerators

site=wikipedia.Site("es", "wikipedia")

data=site.getUrl("/w/index.php?title=Especial:WhatLinksHere/Plantilla:Ficha_de_wikiproyecto&limit=5000&from=0&namespace=102")
data=data.split('<!-- bodytext -->')[1].split('<!-- /bodytext -->')[0]
m=re.compile(ur'title="Wikiproyecto:(.*?)">Wikiproyecto').finditer(data)

salida=u"{{/begin}}"

projectslists=[]
for i in m:
    projectslists.append(u"Wikiproyecto:%s/participantes" % i.group(1))

projects=[]
gen=pagegenerators.PagesFromTitlesGenerator(projectslists, site)
pre=pagegenerators.PreloadingGenerator(gen, pageNumber=100, lookahead=10)
for p in pre:
    if p.exists() and not p.isRedirectPage():
        contpart=0
        parttext=p.get()
        n=re.compile(ur'(?i)(\[\[(User|Usuario):|\{\{ *u *\|)').finditer(parttext)
        for i in n:
            contpart+=1
        project=p.title().split(':')[1].split('/')[0]
        wikipedia.output(ur'Wikiproyecto:%s [%d participantes]' % (project, contpart))
        projects.append([contpart, project])

projects.sort()
projects.reverse()

cont=1
for contpart, project in projects:
    salida+=u"\n|-\n| %d || [[Wikiproyecto:%s|%s]] || [[Wikiproyecto:%s/participantes|%d]] " % (cont, project, project, project, contpart)
    cont+=1

salida+=u"\n{{/end}}"

wiii=wikipedia.Page(site, u"Wikipedia:Ranking de wikiproyectos")
wiii.put(salida, u"BOT - Actualizando ranking de wikiproyectos")

