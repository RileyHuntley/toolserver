# -*- coding: utf-8 -*-

from __future__ import generators
import sys, re
import wikipedia, pagegenerators,catlib, config
import string
import thread, time, urllib
 
global salida
global cont1
global cont2
PageTitles=[]
 
def f1(j):
	global salida
	global cont1
	global cont2

	jj=j.title()
	if j.exists() and not j.isRedirectPage() and not j.isDisambig():
		jt=j.get()
		n=re.compile(u"\[\[es:([^\]]*?)\]\]").finditer(jt)
		es=u""
		tt=u""
		for k in n:
			if not es:
				es+=u"%s" % k.group(1)

		n=re.compile(u"\[\[(de|fr|pt|it):([^\]]*?)\]\]").finditer(jt)
		iws=u""
		for k in n:
			iws+=u" - [[:%s:%s|%s]]" % (k.group(1), k.group(2), k.group(1))

		if re.search(ur"(?i)\{\{ *(template\:)? *taxobox", jt):
			tt+="T"

		if es:
			cont1+=1
			salida+=u"\n# [[%s]] - [[:en:%s|en]]%s" % (es, jj, iws)
			if tt:
				salida+=u" (%s)" % (tt)
		else:
			cont2+=1
			salida+=u"\n# [[%s]] - [[:en:%s|en]]%s" % (jj, jj, iws)
			if tt:
				salida+=u" (%s)" % (tt)
 
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
	tt=p.title()
	t=p.get()

	m=re.compile(u"(?im)^\#.*?\[\[([^|\]]*?)\]\]").finditer(t)

	pt=[]
	for i in m:
		pt.append(u"%s" % i.group(1))

	pp = [wikipedia.Page(wikipedia.Site("en", "wikipedia"), PageTitle) for PageTitle in pt]
	g = iter(pp)
	pg = pagegenerators.PreloadingGenerator(g, pageNumber = 250)

	salida=u"{{Wikiproyecto:Enciclopedia Británica 1911/Header}}\n\n"
	cont1=0
	cont2=0
	pt=[]
	for j in pg:
		if j.exists():
			if j.isRedirectPage():
				pt.append(u"%s" % j.getRedirectTarget().title())# esta línea es la que dice que da problemas
			else:
				f1(j)

	pp = [wikipedia.Page(wikipedia.Site("en", "wikipedia"), PageTitle) for PageTitle in pt]
	g = iter(pp)
	pg = pagegenerators.PreloadingGenerator(g, pageNumber = 250)
	for j in pg:
		if j.exists():
			f1(j)

	contt1+=cont1
	contt2+=cont2

	porcentaje=cont1*1.0/(cont1+cont2)*100
	progreso+=u"|%.2f" % porcentaje

	wikipedia.output(u"%s" % salida)

	trozos=tt.split("/")

	#x=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Wikiproyecto:Enciclopedia Británica 1911/%s" % (trozos[2]))
	#x.put(salida, u"generando lista")
 
porcentaje=contt1*1.0/(contt1+contt2)*100
progreso+=u"|%.2f" % porcentaje
progreso+=u"}}"
x=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Plantilla:Progreso1911")
x.put(progreso, u"BOT - Actualizando plantilla")
