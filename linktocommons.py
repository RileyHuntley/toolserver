# -*- coding: utf-8 -*-

import wikipedia, os, sys, re, time

def percent(c):
	if c % 10000 == 0:
		print 'Llevamos %d' % c

lang='es'
if len(sys.argv)>=2:
	lang=sys.argv[1]

plantillas={
'af':[u'Commons', u'CommonsKategorie', u'Commonscat', u'CommonsKategorie-inlyn'],
'az':[u'Commons', u'Commons2', u'Commons3', u'CommonsKat', u'Commonscat', u'Commonskat', u'CommonsKat2', u'CommonsKat3'],
'de':[u'Commons', u'Commonscat', u'CommonsCat'],
'eo':[u'Commons', u'Commonscat'],
'es':[u'Commonscat', u'Commons cat', u'Ccat', u'Commons'],
'en':[u'Commons',u'Pic',u'Commonspar',u'Commonspiped',u'Commonsme',u'Siisterlinkswp',u'Wikicommons',u'Commons-gallery',u'Gallery-link',u'Commons cat',u'Commonscat',u'Commons2',u'CommonsCat',u'Cms-catlit-up',u'Catlst commons',u'Commonscategory',u'Commonscat',u'Commonscat-inline',u'Commons cat left',u'Commons cat multi',u'Commons page',u'Commons-inline',u'Commonstiny',u'Commonstmp',u'Sistercommons',u'Sisterlinks',u'Sisterlinks2'],
'hu':[u'Commons',u'Közvagyonkat',u'Commons-natúr'],
#'it':[u'Commons',u'Commonscat'],
'pt':[u'Commons',u'Commons1',u'Commonscat',u'Commons2',u'Correlato/commons',u'Correlatos'],
'sl':[u'Commons',u'Zbirka'],
'tr':[u'Commons',u'CommonsKatÇoklu',u'CommonsKat',u'Commonscat',u'Commons cat',u'CommonsKat-ufak',u'Commons1',u'Commons-ufak'],
}

regexp={
'af': ur'(?im)(^\=+ *Eksterne skakels *\=+$)',
'az': ur'(?im)(^\=+ *Xarici keçidlər *\=+$)',
'de': ur'(?im)(^\=+ *Weblinks *\=+$)',
'eo': ur'(?im)(^\=+ *Eksteraj ligoj *\=+$)',
'es': ur'(?im)(^\=+ *Enlaces externos *\=+$)',
'en': ur'(?im)(^\=+ *External links *\=+$)',
'hu': ur'(?im)(^\=+ *Külső hivatkozások *\=+$)',
'pt': ur'(?im)(^\=+ *\{\{ *Ligações externas *\}\} *\=+$)',
'sl': ur'(?im)(^\=+ *Zunanje povezave *\=+$)',
'tr': ur'(?im)(^\=+ *Dış bağlantılar *\=+$)',
}

resumes={
'es': u'Añadiendo enlace a Commons',
'pt': u'Adicionando ligação ao Commons',
}

os.system('mysql -h commonswiki-p.db.toolserver.org -e "use commonswiki_p;select page_id, page_title, ll_title from langlinks, page where ll_lang=\'%s\' and page_id=ll_from and page_namespace=0;" > /home/emijrp/temporal/commonswikipageid.txt' % lang)
f=open('/home/emijrp/temporal/commonswikipageid.txt', 'r')

c=0
commons={}
for line in f:
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==3:
		pageid=trozos[0]
		pagetitle=trozos[1]
		lltitle=trozos[2]
		if not commons.has_key(pageid):
			c+=1
			percent(c)
			commons[pageid]=[pagetitle, lltitle, 0]
print 'Cargados %d pageid/pagetitle/lltitle para commons con interwiki a %s:' % (c, lang)
f.close()

#que paginas de lang.wikipedia.org tienen ya enlace hacia commons?
evitar=u'' #lo dejamos en blanco para que falle si no tenemos plantillas para cierto idioma
if plantillas.has_key(lang):
	for k in plantillas[lang]:
		evitar+=u'tl_title=\'%s\' or ' % k
		if k!=re.sub(' ', '_', k):
			evitar+=u'tl_title=\'%s\' or ' % re.sub(' ', '_', k)
	evitar=evitar[:len(evitar)-4]

print evitar

os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id, page_title from templatelinks, page where tl_from=page_id and page_namespace=0 and page_is_redirect=0 and (%s);" > /home/emijrp/temporal/usocommons.txt' % (lang, lang, evitar.encode('utf-8')))
f=open('/home/emijrp/temporal/usocommons.txt', 'r')

c=0
usocommons={}
for line in f:
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==2:
		pageid=trozos[0]
		pagetitle=trozos[1]
		if not usocommons.has_key(pagetitle):
			c+=1
			percent(c)
			usocommons[pagetitle]=True
print 'Cargados %d pageid/pagetitle de paginas de %s: que ya apuntan a Commons' % (c, lang)
f.close()

#cuantas imagenes tienen las galerias? merece la pena enlazar?
try:
	f=open('/home/emijrp/temporal/commonsgalleries.txt', 'r')
except:
	os.system('mysql -h commonswiki-p.db.toolserver.org -e "use commonswiki_p;select il_from from imagelinks where il_from in (select page_id from page where page_namespace=0 and page_is_redirect=0);" > /home/emijrp/temporal/commonsgalleries.txt')
	f=open('/home/emijrp/temporal/commonsgalleries.txt', 'r')

c=0
for line in f:
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==1:
		pageid=trozos[0]
		if commons.has_key(pageid):
			c+=1
			percent(c)
			commons[pageid][2]+=1
print 'Cargadas %d imagenes en galerias' % (c)
f.close()

#salida

evitar='' #lo dejamos en blanco para que falle si no tenemos plantillas para cierto idioma
if plantillas.has_key(lang):
	for k2 in plantillas[lang]:
		evitar+='%s|' % k2
		if k2!=re.sub(' ', '_', k2):
			evitar+='%s|' % re.sub(' ', '_', k2)
	evitar=evitar[:len(evitar)-1]

print evitar

c=0
cc=0

resume=u'Adding link to Commons'
if resumes.has_key(lang):
	resume=resumes[lang]

for k, v in commons.items():
	if not usocommons.has_key(v[1]) and v[2]>=5:
		c+=1
		wikipedia.output(u'%d) %s %s %s [Llevamos %d de %d]' % (c, k, v[0], v[1], cc, c))
		
		if re.search(ur'(?i)(atlas)', v[0]):
			continue
		
		try:
			page=wikipedia.Page(wikipedia.Site(lang, 'wikipedia'), v[1])
			if page.exists() and not page.isRedirectPage() and not page.isDisambig():
				text=page.get()
				if evitar and not re.search(ur'(?i)(%s)' % evitar, text) and not re.search(ur'taxo', text): #taxobox
					if re.search(regexp[lang], text):
						newtext=re.sub(regexp[lang], ur'\1\n{{Commons|%s}}' % v[0], text)
						wikipedia.showDiff(text, newtext)
						#page.put(newtext, u'BOT - Adding link to Commons: [[:commons:%s|%s]] (TESTING SOME EDITS, SUPERVISED)' % (v[0], v[0]))
						page.put(newtext, u'BOT - %s: [[:commons:%s|%s]]' % (resume, v[0], v[0]))
						#time.sleep(10)
						cc+=1
		except:
			pass





