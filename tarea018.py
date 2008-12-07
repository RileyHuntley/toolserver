# -*- coding: utf-8 -*-
import wikipedia, gzip, os, re, datetime, sys
import urllib
import time

def htc(m):
	return chr(int(m.group(1),16))

def urldecode(url):
	rex=re.compile('%([0-9a-hA-H][0-9a-hA-H])',re.M)
	return rex.sub(htc,url)

#os.system('rm /home/emijrp/pagecounts*.gz*') #limpiamos antes de empezar
#os.system('rm /home/emijrp/python/pywikipedia/pagecounts*.gz*') #limpiamos antes de empezar

limite=15
if len(sys.argv)>=2:
	limite=int(sys.argv[1])

langs=['es', 'pl', 'sl']

#os.system('wget http://dammit.lt/wikistats/ -O /mnt/user-store/stats/tmpweb.html')
file=open('/mnt/user-store/stats/tmpweb.html', 'r')
wget=file.read()
ayer=datetime.date.today()-datetime.timedelta(days=1)
ayerano=str(ayer.year)
ayermes=str(ayer.month)
if len(ayermes)==1:
	ayermes='0%s' % ayermes
ayerdia=str(ayer.day)
if len(ayerdia)==1:
	ayerdia='0%s' % ayerdia
m=re.compile(ur'(?i)\"(pagecounts\-%s%s%s\-\d{6}\.gz)\"' % (ayerano, ayermes, ayerdia)).finditer(wget)
gzs=[]
for i in m:
	print i.group(1)
	gzs.append(i.group(1))
wikipedia.output("Elegidos %d ficheros..." % len(gzs))

pagesdic={}

langs_=''
langs__=''
namespaces=[]
for k in langs:
	langs_+='%s|' % k
	
	data=wikipedia.Site(k, 'wikipedia').getUrl("/w/index.php?title=Special:RecentChanges&limit=0")
	data=data.split('<select id="namespace" name="namespace" class="namespaceselector">')[1].split('</select>')[0]
	m=re.compile(ur'<option value="([1-9]\d*)">(.*?)</option>').finditer(data)
	
	for i in m:
		number=int(i.group(1))
		name=i.group(2)
		if namespaces.count(name)==0:
			namespaces.append(name)

for nm in namespaces:
	langs__+='%s|' % nm

langs_=langs_[:len(langs_)-1]
langs__=langs__[:len(langs__)-1]
langs__c=re.compile(ur'(%s)\:' % langs__)

wikipedia.output("Se van a analizar los idiomas: %s" % langs_)
wikipedia.output("%d excepciones: %s" % (len(namespaces), langs__))

"""
for gz in gzs:
	try:
		f=gzip.open('/mnt/user-store/stats/%s' % gz, 'r')
	except:
		os.system('wget http://dammit.lt/wikistats/%s -O /mnt/user-store/stats/%s' % (gz, gz))
		f=gzip.open('/mnt/user-store/stats/%s' % gz, 'r')
	
	#regex=re.compile(ur'(?im)^([a-z]{2}) (.*?) (\d{1,}) (\d{1,})$') #evitamos aa.b
	regex=re.compile(ur'(?im)^(%s) (.+) (\d{1,}) (\d{1,})$' % langs_) #evitamos aa.b
	
	line=re.sub('_', ' ', urldecode(f.readline()))
	c=0
	while line:
		c+=1
		if c % 250000 == 0:
			print "Analizadas %d de lineas" % c
			print "%d idiomas" % len(pagesdic.items())
			cc=0
			for proj, projpages in pagesdic.items():
				cc+=1
				if cc<=10:
					print "  %d) %s.wikipedia.org" % (cc, proj)
				
		m=regex.finditer(line)
		for i in m:
			pagelang=i.group(1)
			page=i.group(2)
			if re.search(langs__c, page):
				continue
			times=int(i.group(3))
			other=int(i.group(4))
			
			#lang
			if not pagesdic.has_key(pagelang):
				pagesdic[pagelang]={}
			
			#page
			if pagesdic[pagelang].has_key(page):
				pagesdic[pagelang][page]+=times
			else:
				pagesdic[pagelang][page]=times
		line=urldecode(f.readline())
	
	f.close()
	break

#ordenamos de mas visitas a menos, cada idioma
pageslist={}
cc=0
for k, v in pagesdic.items():
	cc+=1
	print "Ordenando %s.wikipedia.org [%d/%d]" % (k, cc, len(pagesdic.items()))
	pageslist[k] = [(v2, k2) for k2, v2 in v.items()]
	pageslist[k].sort()
	pageslist[k].reverse()
	pageslist[k] = [(k2, v2) for v2, k2 in pageslist[k]]

visitas={u'Total':0}
for k, v in pageslist.items():
	for k2, v2 in v:
		if visitas.has_key(k):
			visitas[k]+=v2
		else:
			visitas[k]=v2
		visitas[u'Total']+=v2

for k2, v2 in pageslist.items():
	projsite=wikipedia.Site(k2, 'wikipedia')
	#if k2!=u'es': 
	#	continue #saltamos
	#salida=u"{{/begin|%d|%s|%d|%.1f|%d}}" % (limite, k2, visitas[k2], visitas[k2]/(visitas[u'Total']/100.0), visitas[u'Total'])
	salida=u"{{/begin|%d|%s|%d}}" % (limite, k2, visitas[k2])
	#salida=u"La siguiente tabla muestra las '''%d páginas más visitadas''' (en el espacio de nombres '%s') de [[Wikipedia en español]] en el día de ayer (de 00:00 UTC a 23:59 UTC). Ayer hubo un total de {{subst:formatnum:%d}} visitas para este espacio de nombres, %.1f%s del total ({{subst:formatnum:%d}}).\n<center>[[Wikipedia:Ranking de visitas (Principal)|Principal]] · [[Wikipedia:Ranking de visitas (Usuario)|Usuario]] · [[Wikipedia:Ranking de visitas (Wikipedia)|Wikipedia]] · [[Wikipedia:Ranking de visitas (Plantilla)|Plantilla]] · [[Wikipedia:Ranking de visitas (Ayuda)|Ayuda]] · [[Wikipedia:Ranking de visitas (Categoría)|Categoría]] · [[Wikipedia:Ranking de visitas (Portal)|Portal]] · [[Wikipedia:Ranking de visitas (Wikiproyecto)|Wikiproyecto]] · [[Wikipedia:Ranking de visitas (Anexo)|Anexo]]</center>\n\n<center>\n{| class='wikitable sortable' style='text-align:center;'\n! #\n! Página\n! Visitas" % (limite, k2, visitas[k2], visitas[k2]/(visitas[u'Total']/100.0), u'%', visitas[u'Total'])
	#salida=u"<center>\n{| class='wikitable sortable' style='text-align:center;'\n! #\n! Página\n! Visitas"
	
	c=0
	for k, v in pageslist[k2]:
		try:
			if re.search(ur'(?im)(Special\:|sort_down\.gif|sort_up\.gif|sort_none\.gif|\&limit\=)', k):
				continue
			if re.search(langs__c, k):
				continue
			wikipedia.output(k)
			tmp=wikipedia.Page(projsite, k)
			detalles=u''
			if tmp.exists():
				if tmp.isRedirectPage():
					detalles+=u'(#REDIRECT [[%s]])' % (tmp.getRedirectTarget())
				elif tmp.isDisambig():
					detalles+=u'(Desambiguación)'
				else:
					tmpget=tmp.get()
					if re.search(ur'(?i)\{\{ *Artículo bueno', tmpget):
						detalles+=u'[[Image:Artículo bueno.svg|14px|Artículo bueno]]'
					if re.search(ur'(?i)\{\{ *(Artículo destacado|Zvezdica)', tmpget):
						detalles+=u'[[Image:Cscr-featured.svg|14px|Featured article]]'
					if re.search(ur'(?i)\{\{ *(Semiprotegida2?|Semiprotegido|Pp-semi-template)', tmpget):
						detalles+=u'[[Image:Padlock-silver-medium.svg|20px|Semiprotegida]]'
					if re.search(ur'(?i)\{\{ *(Protegida|Protegido|Pp-template)', tmpget):
						detalles+=u'[[Image:Padlock.svg|20px|Protegida]]'
					
			k=re.sub(ur'(?i)(Imagen?\:)', ur':\1', k)
			k=re.sub(ur'(?i)(Category|Categor%C3%ADa|Kategorija)\:', ur':\1:', k)
			k=re.sub('_', ' ', k)
			c+=1
			#salida+=u"\n|-\n| %d || [[%s]] %s || %s " % (c, k, detalles, v)
			salida+=u"\n|-\n| %d || [[%s]] %s || %s " % (c, tmp.title(), detalles, v)
			if c>=limite:
				break
		except:
			wikipedia.output(u'Error al generar item en lista de %s' % k2)
	
	salida+=u"\n{{/end}}"
	#salida+=u"\n|}\n</center>\n\n== Véase también ==\n*[[Wikipedia:Ranking de ediciones]]\n*[[Wikipedia:Ranking de ediciones (incluye bots)]]\n*[[Wikipedia:Ranking de ediciones anónimas por país]]\n*[[Wikipedia:Ranking de wikiproyectos]]\n\n[[Categoría:Wikipedia:Estadísticas|Ranking]]"
	#salida+=u"\n|}\n</center>"
	
	wikipedia.output(salida)
	#wiii=wikipedia.Page(projsite, u'Wikipedia:Ranking de visitas')
	#wiii.put(salida, u'BOT - Actualizando lista de páginas más visitadas')
	wiii=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'Usuario:Emijrp/Zona de pruebas/3')
	wiii.put(salida, u'BOT - Actualizando lista de páginas más visitadas')

#os.system('rm /home/emijrp/pagecounts*.gz*') #limpiamos antes de empezar
#os.system('rm /home/emijrp/python/pywikipedia/pagecounts*.gz*') #limpiamos antes de empezar

"""