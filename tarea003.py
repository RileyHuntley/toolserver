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

from __future__ import generators
import sys, re
import wikipedia, pagegenerators,catlib, config
import string
import thread, time, urllib
 
global salida
global cont1
global cont2
PageTitles=[]
 
#'A', 'A2', 'A3', 'A4', 'A5', 'B', 'B2', 'B3', 'C', 'C2', 'C3', 'C4', 'D', 'D2', 'E', 'E2', 'F', 'F2', 'F3', 'G', 'G2', 'G3', 'H', 'H2', 'H3', 'I', 'J', 'J2', 'J3', 'J4', 'J5', 'K', 'K2', 'L', 'L2', 'M', 'M2', 'M3', 'N', 'O', 'P', 'P2', 'P3', 'Q', 'R', 'R2', 'S', 'S2', 'S3', 'T', 'T2','U', 'V', 'W', 'W2','X-Z'

for i in ['A', 'A2', 'A3', 'A4', 'A5', 'B', 'B2', 'B3', 'C', 'C2', 'C3', 'C4', 'D', 'D2', 'E', 'E2', 'F', 'F2', 'F3', 'G', 'G2', 'G3', 'H', 'H2', 'H3', 'I', 'J', 'J2', 'J3', 'J4', 'J5', 'K', 'K2', 'L', 'L2', 'M', 'M2', 'M3', 'N', 'O', 'P', 'P2', 'P3', 'Q', 'R', 'R2', 'S', 'S2', 'S3', 'T', 'T2','U', 'V', 'W', 'W2','X-Z']:
	PageTitles.append(u"Wikipedia:WikiProject Missing encyclopedic articles/1911 verification/%s" % i)
 
pages = [wikipedia.Page(wikipedia.Site("en", "wikipedia"), PageTitle) for PageTitle in PageTitles]
gen = iter(pages)
preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber = 5)
 
contt1=0
contt2=0
progreso=u"{{subst:Progreso1911/subst"
for p in preloadingGen:
	wtitle=p.title()
	wtext=p.get()
	
	m=re.compile(ur"(?im)^\# *(\[\[ *(Image|File) *\:[^\]]*?\]\])?[^\[]*?\[\[(?P<page>[^|\]]*?)(\||\]\])").finditer(wtext)
	
	articleslist=[]
	for i in m:
		articleslist.append(i.group("page"))
	
	pp = [wikipedia.Page(wikipedia.Site("en", "wikipedia"), PageTitle) for PageTitle in articleslist]
	g = iter(pp)
	pg = pagegenerators.PreloadingGenerator(g, pageNumber = 250)
	
	salida=u"{{Wikiproyecto:Enciclopedia Británica 1911/Header}}\n\n"
	cont1=cont2=0
	articleslist=[]
	for j in pg:
		if j.exists():
			if j.isRedirectPage():
				articleslist.append(j.getRedirectTarget().title())
			else:
				articleslist.append(j.title())
	
	pp = [wikipedia.Page(wikipedia.Site("en", "wikipedia"), PageTitle) for PageTitle in articleslist]
	g = iter(pp)
	pg = pagegenerators.PreloadingGenerator(g, pageNumber = 250)
	for j in pg:
		if j.exists():
			jtitle=j.title()
			if j.exists() and not j.isRedirectPage() and not j.isDisambig():
				jtext=j.get()
				iws=j.interwiki()
				es=tt=u""
				for iw in iws:
					if not es and iw.site().lang=='es':
						es=iw.title()
				
				iwstext=u""
				for iw in iws:
					if iw.site().lang in ['de', 'fr', 'pt', 'it']:
						iwstext+=u" - [[:%s:%s|%s]]" % (iw.site().lang, iw.title(), iw.site().lang)
				
				if re.search(ur"(?i)\{\{ *(template\:)? *taxobox", jtext):
					tt+="T"
				
				if es:
					cont1+=1
					salida+=u"\n# [[%s]] - [[:en:%s|en]]%s" % (es, jtitle, iwstext)
					if tt:
						salida+=u" (%s)" % (tt)
				else:
					cont2+=1
					salida+=u"\n# [[%s]] - [[:en:%s|en]]%s" % (jtitle, jtitle, iwstext)
					if tt:
						salida+=u" (%s)" % (tt)
	
	contt1+=cont1
	contt2+=cont2
	
	porcentaje=cont1*1.0/(cont1+cont2)*100
	progreso+=u"|%.2f" % porcentaje
	
	#wikipedia.output(u"%s" % salida)
	
	trozos=wtitle.split("/")
	
	x=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Wikiproyecto:Enciclopedia Británica 1911/%s" % (trozos[2]))
	x.put(salida, u"BOT - Generando lista")
 
porcentaje=contt1*1.0/(contt1+contt2)*100
progreso+=u"|%.2f" % porcentaje
progreso+=u"}}<noinclude>{{documentación de plantilla}}</noinclude>"
x=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Plantilla:Progreso1911")
x.put(progreso, u"BOT - Actualizando plantilla")
