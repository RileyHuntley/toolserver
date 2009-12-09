# -*- coding: utf-8 -*-

import re
import gzip
import sys
import wikipedia
import time, os

lang='es' #idioma que será analizado
if len(sys.argv)>=2:
	lang=sys.argv[1]

limite=500 #límite de usuarios a listar, los X más creadores
if len(sys.argv)>=3:
	limite=int(sys.argv[2])

translation={
'es': u'Wikipedia:Ranking de creaciones (sin redirecciones)',
'fr': u"Wikipédia:Liste des Wikipédiens par nombre d'articles créés",
'sl': u'Wikipedija:Seznam Wikipedistov po ustvarjenih člankih',
}

titletrans=u'Wikipedia:List of Wikipedians by created articles'
if lang!='en' and translation.has_key(lang):
	titletrans=translation[lang]

site=wikipedia.Site(lang, 'wikipedia')

pages={}
#page_id, page_title, page_length
os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title from page where page_namespace=0 and page_is_redirect=0;" > /home/emijrp/temporal/wikipage.txt' % (lang, lang))
f=open('/home/emijrp/temporal/wikipage.txt', 'r')
c=0
print 'Cargando paginas'
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
print 'Cargadas %d paginas de %s.wikipedia.org' % (c, lang)
f.close()

try:
	f = gzip.open('/mnt/user-store/%swiki-latest-stub-meta-history.xml.gz' % lang)
except:
	os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-stub-meta-history.xml.gz -O /mnt/user-store/%swiki-latest-stub-meta-history.xml.gz' % (lang, lang, lang))
	f = gzip.open('/mnt/user-store/%swiki-latest-stub-meta-history.xml.gz' % lang)

title_pattern = re.compile(ur'<title>(.*)</title>')
username_pattern = re.compile(ur'<username>(.*)</username>')
ip_pattern = re.compile(ur'<ip>(.*)</ip>')

data=site.getUrl("/w/index.php?title=Special:RecentChanges&limit=0")
data=data.split('<select id="namespace" name="namespace" class="namespaceselector">')[1].split('</select>')[0]
m=re.compile(ur'<option value="([1-9]\d*)">(.*?)</option>').finditer(data)
namespaces=u''
for i in m:
	number=i.group(1)
	name=i.group(2)
	namespaces+='%s|' % name
namespaces=namespaces[:len(namespaces)-1]

no_pattern = re.compile(ur'(%s)\:' % namespaces)

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
			print 'Leidas %d páginas, %f segundos' % (c, time.time()-t1)
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


limite2=1000 #paginas por lista
c=1
salida=u''
for user, number in l:
	if (c<=limite and number>=50) or c<=15:
		if len(user)<1:
			continue
		salida+=u'|-\n| %d || [[User:%s|%s]] || [[/%s/1|%d]]\n' % (c, user, user, user, number)
		if user_creations.has_key(user):
			ll=user_creations[user]
			ll.sort()
			cc=1
			salida2=u'{{Special:PrefixIndex/%s/%s/}}\n' % (titletrans, user)
			for art in ll:
				if not pages.has_key(art):
					continue
				salida2+=u'*%d) [[%s]]\n' % (cc, art)
				if cc % limite2 == 0:
					wiii=wikipedia.Page(site, u'%s/%s/%s' % (titletrans, user, cc/limite2))
					wiii.put(salida2, u'BOT - Updating ranking')
					salida2=u'{{Special:PrefixIndex/%s/%s/}}\n' % (titletrans, user)
				cc+=1
			wiii=wikipedia.Page(site, u'%s/%s/%s' % (titletrans, user, cc/limite2+1))
			wiii.put(salida2, u'BOT - Updating ranking')
		c+=1
	else:
		break
	
salida=u'{{/begin|%s}}\n%s{{/end|%s}}\n' % (c-1, salida, c-1)

wikipedia.output(salida)
wiii=wikipedia.Page(site, titletrans)
wiii.put(salida, u'BOT - Updating ranking')

#os.system('rm /home/emijrp/python/pywikipedia/eswiki-latest-stub-meta-history.xml.gz') #limpiamos
