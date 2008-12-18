# -*- coding: utf-8 -*-

import wikipedia, re

site=wikipedia.Site("es", "wikipedia")

data=site.getUrl("/w/index.php?title=Especial:WhatLinksHere/Plantilla:Ficha_de_wikiproyecto&limit=5000&from=0&namespace=102")
data=data.split('<!-- start content -->')[1]
data=data.split('<!-- end content -->')[0]
m=re.compile(ur'title="Wikiproyecto:(.*?)">Wikiproyecto').finditer(data)

salida=u"La siguiente es una '''lista de [[Wikipedia:Wikiproyectos|wikiproyectos]]''' ordenada por número de participantes.\n\n<center>\n{| class='wikitable sortable' style='text-align:center;'\n! #\n! Wikiproyecto\n! Participantes"
cont=1
for i in m:
	project=i.group(1)
	p=wikipedia.Page(site, u"Wikiproyecto:%s" % project)
	vh=p.getVersionHistory()
	
	participantes=wikipedia.Page(site, u"Wikiproyecto:%s/participantes" % project)
	if participantes.exists() and not participantes.isRedirectPage():
		contpart=0
		parttext=participantes.get()
		n=re.compile(ur'(?i)(\[\[(User|Usuario):|\{\{ *u *\|)').finditer(parttext)
		for i in n:
			contpart+=1
		wikipedia.output(ur'%d) Wikiproyecto:%s [%d participantes]' % (cont, project, contpart))
		salida+=u"\n|-\n| %d || [[Wikiproyecto:%s|%s]] || [[Wikiproyecto:%s/participantes|%d]] " % (cont, project, project, project, contpart)
	cont+=1

salida+=u"\n|}\n</center>\n\n== Véase también ==\n*[[Wikipedia:Ranking de ediciones]]\n*[[Wikipedia:Ranking de ediciones (incluye bots)]]\n\n[[Categoría:Wikipedia:Estadísticas|Ranking]]"

wiii=wikipedia.Page(site, u"Wikipedia:Ranking de wikiproyectos")
wiii.put(salida, u"BOT - Actualizando ranking de wikiproyectos")

