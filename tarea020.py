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

import re
import gzip
import sys
import wikipedia
import time, os
import bz2
import tarea000

# Este script necesita un dump pre-procesado con stubmetahistory-fetch-celementtree.py. Este código está en el repositorio también

def percent(c):
	if c % 100000 == 0:
		wikipedia.output(u'Llevamos %d' % c)

lang='es' #idioma que será analizado
if len(sys.argv)>=2:
	lang=sys.argv[1]

toplimit=500 #límite de usuarios a listar, los X más creadores
if len(sys.argv)>=3:
	limite=int(sys.argv[2])

site=wikipedia.Site(lang, 'wikipedia')

traslation={
'page_title': {
	'en': u'User:Emijrp/List of Wikipedians by page count',
	'es': u'Wikipedia:Ranking de creaciones',
	#'fr': u"Wikipédia:Liste des Wikipédiens par nombre d'articles créés",
	#'sl': u'Wikipedija:Seznam Wikipedistov po ustvarjenih člankih',
	},
}

data=site.getUrl("/w/index.php?title=Special:RecentChanges&limit=0")
data=data.split('<select id="namespace" name="namespace" class="namespaceselector">')[1].split('</select>')[0]
namespaces=re.findall(ur'<option value="[1-9]\d*">(.*?)</option>', data)
no_pattern = re.compile(ur'(%s)\:' % '|'.join(namespaces))

bots=[]
data=site.getUrl("/w/index.php?title=Special:Listusers&limit=5000&group=bot")
data=data.split('<!-- start content -->')
data=data[1].split('<!-- end content -->')[0]
m=re.compile(ur' title=".*?:(?P<botname>.*?)">').finditer(data)
for i in m:
	bots.append(i.group("botname"))


f=bz2.BZ2File("/mnt/user-store/dump/%swiki-fetched.txt.bz" % lang, "r")
prev_title=""
revs=[]
user_creations={}
c=0
for l in f.xreadlines():
	c+=1
	percent(c)
	l=unicode(l, "utf-8")
	t=l.strip().split("	")
	if len(t)>9:
		[page_title, page_id, rev_id, rev_timestamp, rev_author, rev_comment, md5_, rev_len, rev_type]=t[0:9]
	else:
		continue
	if not re.search(no_pattern, page_title):
		item=[rev_timestamp, rev_author, rev_type]
		if page_title!=prev_title and revs:#fix funciona si el dump muestra todas las revisiones de una misma pagina juntas, hacerlo independiente de esto
			revs.sort()			
			[rev_timestamp, rev_author, rev_type]=revs[0][0:3]
			#item2=[prev_title, rev_type]
			if user_creations.has_key(rev_author):
				user_creations[rev_author][rev_type]+=1
			else:
				user_creations[rev_author] = {'0':0,'1':0,'2':0}
				user_creations[rev_author][rev_type]+=1
			revs=[item]
			prev_title=page_title
		else:
			revs.append(item)
f.close()

d={}
for user, creations in user_creations.items():
	d[user]=creations['0']

#ordenamos
l = [(v, k) for k, v in d.items()]
l.sort()
l.reverse()
l = [(k, v) for v, k in l]
for user, number in l[0:10]:
	print user, number

limite2=1000 #paginas por lista
c=1
salida=u'{{/begin|%s}}\n' % (toplimit)
for user, numberofarticles in l:
	if (c<=toplimit and number>=50) or c<=15:
		if len(user)<1:
			continue
		add=user_creations[user]['0']+user_creations[user]['1']+user_creations[user]['2']
		salida+=u'|-\n| %d || [[User:%s|%s]] || %d || %d || %d || %d \n' % (c, user, user, user_creations[user]['0'], user_creations[user]['1'], user_creations[user]['2'], add)
		#salida+=u'|-\n| %d || [[User:%s|%s]] || [[/%s/1|%d]]\n' % (c, user, user, user, number)
		c+=1
	else:
		break
	
#salida=u'{{/begin|%s}}\n%s{{/end|%s}}\n' % (c-1, salida, c-1)
salida+=u"{{/end}}"

wikipedia.output(salida)
wiii=wikipedia.Page(site, traslation['page_title'][lang])
msg=u""
if bots.count("BOTijo")==0:
	msg+=u"(This bot only edits user subpages. If flag if needed for this, please, send a message to [[:es:User talk:Emijrp]].)"
wiii.put(salida, u'BOT - Updating ranking %s' % msg)

"""
#ranking de creaciones sin redirecciones
#revisar

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



#os.system('rm /home/emijrp/python/pywikipedia/eswiki-latest-stub-meta-history.xml.gz') #limpiamos"""



