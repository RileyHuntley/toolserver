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

lang='es'
if len(sys.argv)>=2:
	lang=sys.argv[1]

limite=15
if len(sys.argv)>=3:
	limite=int(sys.argv[2])

site=wikipedia.Site(lang, 'wikipedia')

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

pagesdic={u'Principal':{}, u'Usuario':{}, u'Wikipedia':{}, u'Imagen':{}, u'Plantilla':{}, u'Ayuda':{}, u'Categoría':{}, u'Portal':{}, u'Wikiproyecto':{}, u'Anexo':{}}

data=site.getUrl("/w/index.php?title=Special:RecentChanges&limit=0")
data=data.split('<select id="namespace" name="namespace" class="namespaceselector">')[1].split('</select>')[0]
m=re.compile(ur'<option value="([1-9]\d*)">(.*?)</option>').finditer(data)
namespaces={}
for i in m:
	number=int(i.group(1))
	name=i.group(2)
	namespaces[number]=name

r={'Usuario':re.compile(ur'(?m)^%s %s:' % (lang, namespaces[2])),
'Wikipedia':re.compile(ur'(?m)^%s %s:' % (lang, namespaces[4])),
'Imagen':re.compile(ur'(?m)^%s %s:' % (lang, namespaces[6])),
'Plantilla':re.compile(ur'(?m)^%s %s:' % (lang, namespaces[10])),
'Ayuda':re.compile(ur'(?m)^%s %s' % (lang, namespaces[12])),
'Categoría':re.compile(ur'(?m)^%s %s:' % (lang, namespaces[14])), #Categor%C3%ADa
#'Portal':re.compile(ur'(?m)^%s %s:' % (lang, namespaces[100])),
#'Wikiproyecto':re.compile(ur'(?m)^%s %s:' % (lang, namespaces[102])),
#'Anexo':re.compile(ur'(?m)^%s Anexo:' % lang),
}

for gz in gzs:
	try:
		f=gzip.open('/mnt/user-store/stats/%s' % gz, 'r')
	except:
		os.system('wget http://dammit.lt/wikistats/%s -O /mnt/user-store/stats/%s' % (gz, gz))
		f=gzip.open('/mnt/user-store/stats/%s' % gz, 'r')
	
	regex=re.compile(ur'(?im)^%s (.*) (\d{1,}) (\d{1,})$' % lang)
	
	line=f.readline()
	line=urldecode(line)
	c=0
	while line:
		c+=1
		if c % 250000 == 0:
			print "Analizadas %d de lineas" % c
		m=regex.finditer(line)
		for i in m:
			page=i.group(1)
			times=int(i.group(2))
			
			nm=u'Principal'
			if re.search(r['Usuario'], line):
				nm=u'Usuario'
			elif re.search(r['Wikipedia'], line):
				nm=u'Wikipedia'
			elif re.search(r['Imagen'], line):
				nm=u'Imagen'
				continue #saltamos
			elif re.search(r['Plantilla'], line):
				nm=u'Plantilla'
			elif re.search(r['Ayuda'], line):
				nm=u'Ayuda'
			elif re.search(r['Categoría'], line):
				nm=u'Categoría'
			"""elif re.search(r['Portal'], line):
				nm=u'Portal'
			elif re.search(r['Wikiproyecto'], line):
				nm=u'Wikiproyecto'
			elif re.search(r['Anexo'], line):
				nm=u'Anexo'"""
			
			if pagesdic[nm].has_key(page):
				pagesdic[nm][page]+=times
			else:
				pagesdic[nm][page]=times
		line=f.readline()
	
	f.close()
	break

pageslist={}
for k, v in pagesdic.items():
	pageslist[k] = [(v2, k2) for k2, v2 in v.items()]
	pageslist[k].sort()
	pageslist[k].reverse()
	pageslist[k] = [(k2, v2) for v2, k2 in pageslist[k]]

visitas={u'Total':0, u'Principal':0, u'Usuario':0, u'Wikipedia':0, u'Imagen':0, u'Plantilla':0, u'Ayuda':0, u'Categoría':0, u'Portal':0, u'Wikiproyecto':0, u'Anexo':0}
for k, v in pageslist.items():
	for k2, v2 in v:
		visitas[k]+=v2
		visitas[u'Total']+=v2

for k2, v2 in pageslist.items():
	if k2!=u'Principal': #saltamos imagenes
		continue #saltamos
	#salida=u"{{/begin|%d|%s|%d|%.1f|%d}}" % (limite, k2, visitas[k2], visitas[k2]/(visitas[u'Total']/100.0), visitas[u'Total'])
	#salida=u"La siguiente tabla muestra las '''%d páginas más visitadas''' (en el espacio de nombres '%s') de [[Wikipedia en español]] en el día de ayer (de 00:00 UTC a 23:59 UTC). Ayer hubo un total de {{subst:formatnum:%d}} visitas para este espacio de nombres, %.1f%s del total ({{subst:formatnum:%d}}).\n<center>[[Wikipedia:Ranking de visitas (Principal)|Principal]] · [[Wikipedia:Ranking de visitas (Usuario)|Usuario]] · [[Wikipedia:Ranking de visitas (Wikipedia)|Wikipedia]] · [[Wikipedia:Ranking de visitas (Plantilla)|Plantilla]] · [[Wikipedia:Ranking de visitas (Ayuda)|Ayuda]] · [[Wikipedia:Ranking de visitas (Categoría)|Categoría]] · [[Wikipedia:Ranking de visitas (Portal)|Portal]] · [[Wikipedia:Ranking de visitas (Wikiproyecto)|Wikiproyecto]] · [[Wikipedia:Ranking de visitas (Anexo)|Anexo]]</center>\n\n<center>\n{| class='wikitable sortable' style='text-align:center;'\n! #\n! Página\n! Visitas" % (limite, k2, visitas[k2], visitas[k2]/(visitas[u'Total']/100.0), u'%', visitas[u'Total'])
	salida=u"<center>\n{| class='wikitable sortable' style='text-align:center;'\n! #\n! Página\n! Visitas"
	
	c=0
	for k, v in pageslist[k2]:
		try:
			if re.search(ur'(?im)(Special\:|sort_down\.gif|sort_up\.gif|sort_none\.gif|\&limit\=)', k):
				continue
			wikipedia.output(k)
			tmp=wikipedia.Page(site, k)
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
			salida+=u"\n|-\n| %d || [[:%s:%s]] %s || %s " % (c, lang, tmp.title(), detalles, v)
			if c>=limite:
				break
		except:
			wikipedia.output(u'Error al generar item en lista de %s' % k2)
	
	#salida+=u"{{/end}}"
	#salida+=u"\n|}\n</center>\n\n== Véase también ==\n*[[Wikipedia:Ranking de ediciones]]\n*[[Wikipedia:Ranking de ediciones (incluye bots)]]\n*[[Wikipedia:Ranking de ediciones anónimas por país]]\n*[[Wikipedia:Ranking de wikiproyectos]]\n\n[[Categoría:Wikipedia:Estadísticas|Ranking]]"
	salida+=u"\n|}\n</center>"
	
	wikipedia.output(salida)
	#wiii=wikipedia.Page(site, u'Wikipedia:Ranking de visitas (%s)' % k2)
	#wiii.put(salida, u'BOT - Actualizando lista de páginas más visitadas (%s)' % k2)
	wiii=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'Usuario:Emijrp/Zona de pruebas/3')
	wiii.put(salida, u'BOT - Actualizando lista de páginas más visitadas (%s)' % k2)

#os.system('rm /home/emijrp/pagecounts*.gz*') #limpiamos antes de empezar
#os.system('rm /home/emijrp/python/pywikipedia/pagecounts*.gz*') #limpiamos antes de empezar
