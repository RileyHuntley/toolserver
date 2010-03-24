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

st=u"!"
if (len(sys.argv)>=2):
	st=sys.argv[1]
gen=pagegenerators.AllpagesPageGenerator(start = st, namespace = 0, includeredirects = False, site = eswiki)
pre=pagegenerators.PreloadingGenerator(gen, pageNumber=250, lookahead=250)
for page in pre:
	if not page.exists():
		continue
	while page.isRedirectPage():
		page=page.getRedirectTarget()
	if page.isDisambig():
		continue
	eswtext=page.get()
	if re.search(ur"(?i)(\{\{ *coord *\||coor|latitude? *\=|longitude? *\=|nacidos en|fallecidos en|\{\{ *BD *\|)", eswtext):
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
		if not enpage.exists() or enpage.isRedirectPage() or enpage.isDisambig():
			continue
		if re.search(ur"#", enpage.title()):
			continue
		enwtext=enpage.get()
		m=re.compile(ur"(?i)(?P<coord>\{\{ *coord *\|[^\}]*\}\})").finditer(enwtext)
		
		if len(re.findall(ur"(?i)(?P<coord>\{\{ *coord *\|[^\}]*\}\})", enwtext))>1:
			continue
		
		for i in m:
			coord=i.group("coord")
			if not re.search(ur"(?i)title", coord): #evitamos coordenadas que estén por el medio del texto y no salgan arriba a la derecha
				break
			wikipedia.output(u"%s - %s" % (enwtitle, coord))
			coord=re.sub(ur"display *\=[^\|\}]+([\|\}])", ur"display=title\1", coord) #dejamos display title solo
			
			eswtext=page.get()
			esnewtext=re.sub(ur"(?i)(\[\[ *Categor(y|ía) *\:)", ur"%s\n\n\1" % coord, eswtext, 1) #solo insertamos 1 vez
			if eswtext!=esnewtext:
				wikipedia.showDiff(eswtext, esnewtext)
				try:
					page.put(esnewtext, u"BOT - Insertando coordenadas %s desde [[:en:%s]]" % (coord, enwtitle))
				except:	
					pass
			break
	
#f.close()

