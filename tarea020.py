# -*- coding: utf-8 -*-

import re
import gzip
import sys
import wikipedia
import time, os

pages={}
#page_id, page_title, page_length
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select page_title from page where page_namespace=0 and page_is_redirect=0;" > /home/emijrp/temporal/eswikipage.txt')
f=open('/home/emijrp/temporal/eswikipage.txt', 'r')
c=0
print 'Cargando paginas de eswiki'
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==1:
		page_title=trozos[0]
		c+=1
		pages[page_title]=0
print 'Cargadas %d paginas en eswiki' % c
f.close()

# Lo que debe recibir este script es un dump en XML de la tabla stub-meta-history,
# comprimido con gzip
#os.system('rm /home/emijrp/python/pywikipedia/eswiki-latest-stub-meta-history.xml.gz') #limpiamos antes de empezar
#os.system('wget http://download.wikimedia.org/eswiki/latest/eswiki-latest-stub-meta-history.xml.gz -O /home/emijrp/python/pywikipedia/eswiki-latest-stub-meta-history.xml.gz')

try:
	f = gzip.open('/home/emijrp/python/pywikipedia/eswiki-latest-stub-meta-history.xml.gz')
except:
	os.system('wget http://download.wikimedia.org/eswiki/latest/eswiki-latest-stub-meta-history.xml.gz -O /home/emijrp/python/pywikipedia/eswiki-latest-stub-meta-history.xml.gz')
	f = gzip.open('/home/emijrp/python/pywikipedia/eswiki-latest-stub-meta-history.xml.gz')

title_pattern = re.compile(ur'<title>(.*)</title>')
username_pattern = re.compile(ur'<username>(.*)</username>')
ip_pattern = re.compile(ur'<ip>(.*)</ip>')
no_pattern = re.compile(ur'(Discusión|Usuario|Usuario Discusión|Wikipedia|Wikipedia Discusión|Imagen|Imagen Discusión|MediaWiki|MediaWiki Discusión|Plantilla|Plantilla Discusión|Ayuda|Ayuda Discusión|Categoría|Categoría Discusión|Portal|Portal Discusión|Wikiproyecto|Wikiproyecto Discusión|Anexo Discusión)\:')

# Este diccionario acabará teniendo un usuario (o IP) como índice y una lista
# de artículos como valor
user_creations = {}

title_found = False
c=0
t1=time.time()
#skip=0
for line in f:
	#if skip>0:
	#	skip-=1
	#	continue
	line=unicode(line, 'utf-8')
	title = re.findall(title_pattern, line)
	if title and not re.search(no_pattern, title[0]):
		#print title[0]
		title_string = title[0]
		title_found = True
		#skip=4
		c+=1
		if c % 1000 == 0:
			print c
			print time.time()-t1
			t1=time.time()
			#break
	elif title_found:
		if pages.has_key(title_string):
			username = re.findall(username_pattern, line)
			if username:
				username_string = username[0]
				if user_creations.has_key(username_string):
					user_creations[username_string].append(title_string)
				else:
					user_creations[username_string] = [title_string,]
				title_found = False
				#skip=3
			else:
				ip = re.findall(ip_pattern, line)
				if ip:
					ip_string = ip[0]
					if user_creations.has_key(ip_string):
						user_creations[ip_string].append(title_string)
					else:
						user_creations[ip_string] = [title_string,]
					title_found = False
					#skip=3
f.close()

d={}
for user, creations in user_creations.items():
	d[user]=len(creations)

#ordenamos
l = [(v, k) for k, v in d.items()]
l.sort()
l.reverse()
l = [(k, v) for v, k in l]

limite=500
limite2=1000
c=1
salida=u'{{/begin|%s}}\n' % limite
for user, number in l:
	if c<=limite:
		salida+=u'|-\n| %d || [[Usuario:%s|%s]] || [[/%s/1|%d]]\n' % (c, user, user, user, number)
		if user_creations.has_key(user):
			ll=user_creations[user]
			ll.sort()
			cc=1
			salida2=u'{{Special:PrefixIndex/Wikipedia:Ranking de creaciones (sin redirecciones)/%s/}}\n' % user
			for art in ll:
				if not pages.has_key(art):
					continue
				salida2+=u'*%d) [[%s]]\n' % (cc, art)
				if cc % limite2 == 0:
					wiii=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'Wikipedia:Ranking de creaciones (sin redirecciones)/%s/%s' % (user, cc/limite2))
					#wiii.put(salida2, u'BOT - Actualizando ranking de creaciones de [[Usuario:%s|%s]]' % (user, user))
					salida2=u'{{Special:PrefixIndex/Wikipedia:Ranking de creaciones (sin redirecciones)/%s/}}\n' % user
				cc+=1
			wiii=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'Wikipedia:Ranking de creaciones (sin redirecciones)/%s/%s' % (user, cc/limite2+1))
			#wiii.put(salida2, u'BOT - Actualizando ranking de creaciones de [[Usuario:%s|%s]]' % (user, user))
		c+=1
	else:
		break
	
salida+=u'{{/end|%s}}\n' % limite

wikipedia.output(salida)
wiii=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'Wikipedia:Ranking de creaciones (sin redirecciones)')
wiii.put(salida, u'BOT - Actualizando ranking de creaciones')

#os.system('rm /home/emijrp/python/pywikipedia/eswiki-latest-stub-meta-history.xml.gz') #limpiamos
