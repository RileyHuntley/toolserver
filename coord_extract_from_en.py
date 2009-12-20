# -*- coding: utf-8 -*-

import re
import wikipedia
import sys
import pagegenerators

#TODO: insertar {{coord}} en el parámetro coor de las infobox de localidad

eswiki=wikipedia.Site("es", "wikipedia")
enwiki=wikipedia.Site("en", "wikipedia")

"""f=open("zzzcoord-missing.txt", "r")

for l in f:
	l=unicode(l, "utf-8")
	wtitle=l.split("	")[0]
	page=wikipedia.Page(eswiki, wtitle)"""

st=u"Estadio Sheikh"
if (len(sys.argv)>=2):
	st=sys.argv[1]
gen=pagegenerators.AllpagesPageGenerator(start = st, namespace = 0, includeredirects = False, site = eswiki)
pre=pagegenerators.PreloadingGenerator(gen, pageNumber=250, lookahead=250)
for page in pre:
	if not page.exists():
		continue
	while page.isRedirectPage():
		page=page.getRedirectTarget()
	eswtext=page.get()
	if re.search(ur"(?i)(\{\{ *coord *\|coor|latitude? *\=|longitude? *\=|nacidos en|fallecidos en)", eswtext):
		continue
	#if not re.search(ur"(?i)\{\{ *ficha de localidad", eswtext):
	#	continue
	wikipedia.output(u"%s" % page.title())
	iws=page.interwiki()
	enwtitle=""
	for iw in iws:
		if iw.site().lang=="en":
			enwtitle=iw.title()

	if enwtitle and not re.search(ur"#", enwtitle):
		enpage=wikipedia.Page(enwiki, enwtitle)
		if not enpage.exists():
			continue
		while enpage.isRedirectPage():
			enpage=enpage.getRedirectTarget()
		if re.search(ur"#", enpage.title()):
			continue
		enwtext=enpage.get()
		m=n=re.compile(ur"(?i)(?P<coord>\{\{ *coord *\|[^\}]*\}\})").finditer(enwtext)
		ii=0
		for i in n:
			ii+=1
		if ii>1:
			continue
		for i in m:
			coord=i.group("coord")
			print enwtitle, coord
			coord=re.sub(ur"display *\=[^\|\}]+([\|\}])", ur"display=title\1", coord) #anulamos display
			
			eswtext=page.get()
			esnewtext=re.sub(ur"(?i)(\[\[ *Categor(y|ía) *\:)", ur"%s\n\n\1" % coord, eswtext, 1) #solo insertamos 1 vez
			if eswtext!=esnewtext:
				wikipedia.showDiff(eswtext, esnewtext)
				page.put(esnewtext, u"BOT - Insertando coordenadas %s desde [[:en:%s]]" % (coord, enwtitle))
			break
	
#f.close()

