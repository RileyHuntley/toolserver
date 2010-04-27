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

import wikipedia, gzip, os, re, datetime, sys
import urllib
import time
import pagegenerators

import tareas
import tarea000

#TODO
#que no cuente las talks
#y las totales a wikimedia?

limite=100
langs=[]
hourly=False
hourlylangs=[]
daily=False
dailylangs=[]
minimum=5 #visitas minimas para ser contabilizada la pagina
if len(sys.argv)>1:
	if sys.argv[1]=='daily':
		dailylangs=['it', 'ja', 'pl', 'nl', 'ru', 'sv', 'zh', 'no', 'ca', 'fi', 'uk', 'cs', 'ko', 'gl'] #ir metiendo de mas articulos a menos http://meta.wikimedia.org/wiki/List_of_Wikipedias
		langs+=dailylangs
		daily=True
	elif sys.argv[1]=='hourly':
		hourlylangs=['es', 'en', 'de', 'fr', 'pt', 'da', 'eo', 'hu', 'hr', 'ro', 'sl', 'th', 'tr'] #donde tenga flag
		langs+=hourlylangs
		hourly=True
	else:
		langs+=[sys.argv[1]]
alllangs=dailylangs+hourlylangs
if len(sys.argv)>2:
	limite=int(sys.argv[2])

commonexitpage=u'User:Emijrp/Popular articles'
exitpages={
'es': u'Plantilla:Artículos populares',
}


index='/home/emijrp/temporal/tmpweb.html'
os.system('wget http://dammit.lt/wikistats/ -O %s' % index)
f=open(index, 'r')
wget=f.read()
f.close()
m=re.compile(ur'(?i)\"(pagecounts\-\d{8}\-\d{6}\.gz)\"').finditer(wget)
#m=re.compile(ur'(?i)\"(pagecounts\-20081201\-\d{6}\.gz)\"').finditer(wget)
gzs=[]
for i in m:
	gzs.append(i.group(1))
gzs.sort()
if hourly:
	gzs=gzs[-1] #nos quedamos con el ultimo que es el mas reciente
elif daily:
	gzs=gzs[-24:] #las ultimas 24 horas para las que haya datos
print gzs	
wikipedia.output("Elegidos %d fichero(s)..." % len(gzs))

pagesdic={}
namespaceslists={}
exceptions={}

for lang in langs:
	namespaceslists[lang]=tareas.getNamespacesList(wikipedia.Site(lang, 'wikipedia'))
	exceptions[lang]={}
	exceptions[lang]['raw']='|'.join(namespaceslists[lang])
	exceptions[lang]['compiled']=re.compile(ur'(?i)(%s)\:' % exceptions[lang]['raw'])

wikipedia.output("Se van a analizar los idiomas: %s" % ', '.join(langs))
for lang in langs:
	wikipedia.output("Excepciones de %s: %s" % (lang, exceptions[lang]['raw']))

totalvisits={}
for gz in gzs:
	print gz
	try:
		f=gzip.open('/mnt/user-store/stats/%s' % gz, 'r')
	except:
		#os.system('wget http://dammit.lt/wikistats/%s -O /mnt/user-store/stats/%s' % (gz, gz))
		#f=gzip.open('/mnt/user-store/stats/%s' % gz, 'r')
		sys.exit()
	
	#regex=re.compile(ur'(?im)^([a-z]{2}) (.*?) (\d{1,}) (\d{1,})$') #evitamos aa.b
	regex=re.compile(r'(?im)^(?P<pagelang>%s) (?P<page>.+) (?P<times>\d{1,}) (?P<other>\d{1,})$' % '|'.join(langs)) #evitamos aa.b
	
	c=analized=errores=0
	for line in f:
		line=line[:len(line)-1]
		try:
			line=line.encode('utf-8')
			line=urllib.unquote(line)
		except:
			try:
				line=urllib.unquote(line)
			except:
				wikipedia.output(line)
				errores+=1
				continue
		c+=1
		if c % 250000 == 0:
			print "Leidas %d lineas (%d analizadas, %d fallos)" % (c, analized, errores)
			print "%d idiomas" % len(pagesdic.items())
			cc=0
			for proj, projpages in pagesdic.items():
				cc+=1
				if cc<=10:
					print "  %d) %s.wikipedia.org" % (cc, proj)
				else:
					print "    Y algunos mas..."
					break
		
		m=regex.finditer(line)
		for i in m:
			pagelang=i.group('pagelang')
			page=re.sub('_', ' ', i.group('page'))
			times=int(i.group('times'))
			other=int(i.group('other'))
			
			if not totalvisits.has_key(pagelang): #debe ir antes la exclusión, para contarlas todas
				totalvisits[pagelang]=times
			else:
				totalvisits[pagelang]+=times
			
			if re.search(exceptions[pagelang]['compiled'], page):
				continue
			
			if hourly and times<minimum:#si hago el diario, no descartar nada...
				continue
			
			#lang
			if not pagesdic.has_key(pagelang):
				pagesdic[pagelang]={}
			
			#page
			if pagesdic[pagelang].has_key(page):
				pagesdic[pagelang][page]+=times
			else:
				pagesdic[pagelang][page]=times
				analized+=1
	f.close()

#ordenamos de mas visitas a menos, cada idioma
pageslist={}
cc=0
for lang, pages in pagesdic.items():
	cc+=1
	print "Ordenando %s.wikipedia.org [%d/%d]" % (lang, cc, len(pagesdic.items()))
	pageslist[lang] = [(visits, page) for page, visits in pages.items()]
	pageslist[lang].sort()
	pageslist[lang].reverse()
	pageslist[lang] = [(page, visits) for visits, page in pageslist[lang]]

pageselection={}
for lang, pages in pageslist.items():
	c=0
	pageselection[lang]=[]
	for page, visits in pages:
		if re.search(ur'(?im)(Special\:|sort_down\.gif|sort_up\.gif|sort_none\.gif|\&limit\=)', page): #ampliar con otros idiomas
			continue
		
		c+=1
		if c<=limite*2: #margen de error, pueden no existir las paginas, aunque seria raro
			pageselection[lang].append([urllib.quote(page), visits])
		else:
			break

for lang, list in pageselection.items():
	if tarea000.isExcluded('tarea037', 'wikipedia', lang):
		continue
	exitpage=u""
	if exitpages.has_key(lang):
		exitpage=exitpages[lang]
	else:
		exitpage=commonexitpage
	
	projsite=wikipedia.Site(lang, 'wikipedia')
	if lang=='es':
		salida=u"<noinclude>{{%s/begin|{{subst:CURRENTHOUR}}}}</noinclude>\n{| class=\"wikitable sortable\" style=\"text-align: center;\" width=350px \n|+ [[Plantilla:Artículos populares|Artículos populares]] en la última hora \n! # !! Artículo !! Visitas " % exitpage
	else:
		if hourly:
			salida=u"Popular articles in the last hour (%s).\n\nTotal hits to this project (including all pages): %d.\n\n{| class=\"wikitable sortable\" style=\"text-align: center;\" \n! # !! Article !! Hits " % (gz.split(".gz")[0], totalvisits[lang])
		else:
			salida=u"Popular articles in the last 24 hours.\n\nTotal hits to this project (including all pages): %d.\n\n{| class=\"wikitable sortable\" style=\"text-align: center;\" \n! # !! Article !! Hits " % (totalvisits[lang])

	list2=[]
	for quotedpage, visits in list:
		quotedpage=re.sub("%20", " ", quotedpage).strip()
		if quotedpage:
			list2.append(quotedpage)
	gen=pagegenerators.PagesFromTitlesGenerator(list2, projsite)
	pre=pagegenerators.PreloadingGenerator(gen, pageNumber=limite, lookahead=10)
	c=d=0
	sum=0
	ind=-1
	for page in pre:
		detalles=u''
		ind+=1
		if page.exists():
			wtitle=page.title()
			
			if page.isRedirectPage():
				detalles+=u' (#REDIRECT [[%s]]) ' % (page.getRedirectTarget().title())
			elif page.isDisambig():
				#detalles+=u'(Desambiguación) '
				pass #para evitar no ponerlo en el idioma loal
			else:
				pass
				"""tmpget=page.get()
				if re.search(ur'(?i)\{\{ *Artículo bueno', tmpget):
					detalles+='[[Image:Artículo bueno.svg|14px|Artículo bueno]]'
				if re.search(ur'(?i)\{\{ *(Artículo destacado|Zvezdica)', tmpget):
					detalles+='[[Image:Cscr-featured.svg|14px|Featured article]]'
				if re.search(ur'(?i)\{\{ *(Semiprotegida2?|Semiprotegido|Pp-semi-template)', tmpget):
					detalles+='[[Image:Padlock-silver-medium.svg|20px|Semiprotegida]]'
				if re.search(ur'(?i)\{\{ *(Protegida|Protegido|Pp-template)', tmpget):
					detalles+='[[Image:Padlock.svg|20px|Protegida]]'"""
			
			#wikipedia.output('%s - %d - %s' % (wtitle, visits, detalles))
			#continue
			
			if page.namespace() in [6, 14]:
				wtitle=u':%s' % wtitle
			c+=1
			if lang=='es':
				if c-1 in [3,5,10,15,20]:
					salida+=u"\n{{#ifexpr:{{{top|15}}} > %d|" % (c-1)
					d+=1
				salida+=u"\n{{!}}-\n{{!}} %d {{!}}{{!}} [[%s]]%s{{#if:{{{novistas|}}}||{{!}}{{!}} %s}} " % (c, wtitle, detalles, list[ind][1])
			else:
				salida+=u"\n|-\n| %d || [[%s]]%s || %s " % (c, wtitle, detalles, list[ind][1])
			sum+=int(list[ind][1])
			
			if c>=limite:
				break
			#except:
			#	wikipedia.output(u'Error al generar item en lista de %s:' % lang)
	
	iws=u''
	for iw in alllangs:
		if iw!=lang:
			if exitpages.has_key(iw):
				iws+=u'[[%s:%s]]\n' % (iw, exitpages[iw])
			else:
				iws+=u'[[%s:%s]]\n' % (iw, commonexitpage)
	#salida+="\n{{/end}}\n%s" % (iws)
	if lang=='es':
		salida+=u"\n%s\n{{%s/end|%d|%d|top={{{top|15}}}|fecha={{subst:CURRENTTIME}} ([[UTC]]) del {{subst:CURRENTDAY2}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}}}}\n|}\n<noinclude>{{documentación de plantilla}}\n%s</noinclude>" % ("}} "*d, exitpage, sum, totalvisits[lang], iws)
	else:
		salida+=u"\n|}\n\n%s" % (iws)
	wikipedia.output(salida)
	wiii=wikipedia.Page(projsite, exitpage)
	wiii.put(salida, u'BOT - Updating list')

