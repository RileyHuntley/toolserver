# -*- coding: utf-8 -*-

import os, re, wikipedia

#pages
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select page_title from page where page_namespace=0 and page_is_redirect=0;" > /home/emijrp/temporal/eswikipage.txt')
f=open('/home/emijrp/temporal/eswikipage.txt', 'r')
c=0
print 'Cargando paginas de eswiki'
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
print 'Cargadas %d paginas de eswiki' % c
f.close()

#redirects
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select page_title from page where page_namespace=0 and page_is_redirect=1;" > /home/emijrp/temporal/eswikipage.txt')
f=open('/home/emijrp/temporal/eswikipage.txt', 'r')
c=0
print 'Cargando redirecciones de eswiki'
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
print 'Cargadas %d redirecciones de eswiki' % c
f.close()

c=0
for red, v in reds.items():
	if not re.search(ur"(?i)[^a-záéíóú ]", red):
		red2=red
		red2=re.sub(ur"Á", ur"A", red2)
		red2=re.sub(ur"É", ur"E", red2)
		red2=re.sub(ur"Í", ur"I", red2)
		red2=re.sub(ur"Ó", ur"O", red2)
		red2=re.sub(ur"Ú", ur"U", red2)
		
		red2=re.sub(ur"á", ur"a", red2)
		red2=re.sub(ur"é", ur"e", red2)
		red2=re.sub(ur"í", ur"i", red2)
		red2=re.sub(ur"ó", ur"o", red2)
		red2=re.sub(ur"ú", ur"u", red2)
		
		if red!=red2 and not pages.has_key(red2) and not reds.has_key(red2):
			c+=1
			
			if c % 50 == 0:
				print c
				wikipedia.output(red)
			"""
			redpage=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), red)
			red2page=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), red2)
			if redpage.isRedirectPage() and not red2page.exists():
				salida=u"#REDIRECT [[%s]]" % redpage.getRedirectTarget().title()
				wikipedia.output(salida)
				red2page.put(salida, u"BOT - %s" % salida)"""
				
