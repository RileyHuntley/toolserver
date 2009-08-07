# -*- coding: utf-8 -*-

import os, re, wikipedia

lang="es"
#pages
os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title from page where page_namespace=0 and page_is_redirect=0;" > /home/emijrp/temporal/%swikipage.txt' % (lang, lang, lang))
f=open('/home/emijrp/temporal/%swikipage.txt' % lang, 'r')
c=0
print 'Cargando paginas de %swiki' % lang
pages={}
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==1:
		c+=1
		page_title=trozos[0]
		pages[page_title]=False
print 'Cargadas %d paginas de %swiki' % (c, lang)
f.close()

#redirects
os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title from page where page_namespace=0 and page_is_redirect=1;" > /home/emijrp/temporal/%swikipage.txt' % (lang, lang, lang))
f=open('/home/emijrp/temporal/%swikipage.txt' % lang, 'r')
c=0
print 'Cargando redirecciones de %swiki' % lang
reds={}
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==1:
		c+=1
		page_title=trozos[0]
		reds[page_title]=False
print 'Cargadas %d redirecciones de %swiki' % (c, lang)
f.close()

c=0
for page, v in pages.items():
	if not re.search(ur"(?i)[^a-záéíóú0-9\-\. ]", page): #no meter (    ), A (desambiguacion) Pi (pelicula)
		page2=page
		page2=re.sub(ur"Á", ur"A", page2)
		page2=re.sub(ur"É", ur"E", page2)
		page2=re.sub(ur"Í", ur"I", page2)
		page2=re.sub(ur"Ó", ur"O", page2)
		page2=re.sub(ur"Ú", ur"U", page2)
		
		page2=re.sub(ur"á", ur"a", page2)
		page2=re.sub(ur"é", ur"e", page2)
		page2=re.sub(ur"í", ur"i", page2)
		page2=re.sub(ur"ó", ur"o", page2)
		page2=re.sub(ur"ú", ur"u", page2)
		
		if page!=page2 and not reds.has_key(page2) and not pages.has_key(page2):
			c+=1
			
			if c % 50 == 0:
				print c
				wikipedia.output(page)
			
			page2page=wikipedia.Page(wikipedia.Site(lang, 'wikipedia'), page2)
			if not page2page.exists():
				salida=u"#REDIRECT [[%s]]" % page
				wikipedia.output(salida)
				page2page.put(salida, u"BOT - %s" % salida)
				
