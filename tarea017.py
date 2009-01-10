# -*- coding: utf-8 -*-

import wikipedia, re
import pagegenerators

site=wikipedia.Site("es", "wikipedia")

data=site.getUrl("/w/index.php?title=Especial:WhatLinksHere/Plantilla:Ficha_de_wikiproyecto&limit=5000&from=0&namespace=102")
data=data.split('<!-- start content -->')[1]
data=data.split('<!-- end content -->')[0]
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

