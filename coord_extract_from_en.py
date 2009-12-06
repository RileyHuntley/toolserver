# -*- coding: utf-8 -*-

import re
import wikipedia

eswiki=wikipedia.Site("es", "wikipedia")
enwiki=wikipedia.Site("en", "wikipedia")

f=open("zzzcoord-missing.txt", "r")

for l in f:
	l=unicode(l, "utf-8")
	wtitle=l.split("	")[0]
	page=wikipedia.Page(eswiki, wtitle)
	if not page.exists():
		continue
	while page.isRedirectPage():
		page=page.getRedirectTarget()
	eswtext=page.get()
	if re.search(ur"(?i)\{\{ *coord *\|", eswtext):
		continue
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
		m=re.compile(ur"(?i)(?P<coord>\{\{ *coord *\|[^\}]*\}\})").finditer(enwtext)
		for i in m:
			coord=i.group("coord")
			print enwtitle, coord
			coord=re.sub(ur"display *\=[^\|\}]+([\|\}])", ur"display=title\1", coord) #anulamos display
			
			eswtext=page.get()
			esnewtext=re.sub(ur"(?i)(\[\[ *Categor(y|ía) *\:)", ur"%s\n\n\1" % coord, eswtext, 1) #solo insertamos 1 vez
			if eswtext!=esnewtext:
				wikipedia.showDiff(eswtext, esnewtext)
				page.put(esnewtext, u"BOT - Insertando coordenadas %s desde [[:en:%s]]" % (coord, enwtitle))
	
f.close()

