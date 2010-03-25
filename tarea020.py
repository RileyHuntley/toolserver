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
from xml.etree.cElementTree import iterparse

#llamado con 7za e -so eswiki-latest-pages-meta-history.xml.7z | python tarea020.py es 500

lang='es' #idioma que será analizado
if len(sys.argv)>=2:
	lang=sys.argv[1]

toplimit=500 #límite de usuarios a listar, los X más creadores
if len(sys.argv)>=3:
	limite=int(sys.argv[2])

site=wikipedia.Site(lang, 'wikipedia')

translation={
'es': u'Wikipedia:Ranking de creaciones',
#'fr': u"Wikipédia:Liste des Wikipédiens par nombre d'articles créés",
#'sl': u'Wikipedija:Seznam Wikipedistov po ustvarjenih člankih',
}

titletrans=u'Wikipedia:List of Wikipedians by created articles'
if lang!='en' and translation.has_key(lang):
	titletrans=translation[lang]

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

source=sys.stdin
context = iterparse(source, events=("start", "end"))
context = iter(context)

r_newlines=re.compile(ur"(?im)[\n\r]")
r_links=re.compile(ur"\[\[ *[^\]]+? *[\]\|]")
r_categories=re.compile(ur"\[\[ *Category *\: *[^\]\|]+ *[\]\|]")
r_sections=re.compile(ur"(?im)^(\=+)[^\=]+\1")
r_templates=""
r_interwikis=""
r_externallinks=""
r_bold=""
r_italic=""
r_images="(?i)\[\[ *(image|file) *\:"

page_title=''
page_id=''
rev_id=''
rev_timestamp=''
rev_author=''
rev_comment=''
rev_text=''
lock_page_id=False
lock_revision_id=False
primera_rev=False
t1=time.time()
limit=1000
cpages=crevisions=0.0
md5s=[]
md5sd={}

user_creations={}
for event, elem in context:
	tag=elem.tag.split("}")[1]	
	
	if event=="start" and tag=="page":
		lock_page_id=True
		primera_rev=True
	if event=="start" and tag=="revision":
		lock_revision_id=True
	
	if tag=="id":
		if lock_page_id:
			page_id=elem.text
			lock_page_id=False
		if lock_revision_id:
			rev_id=elem.text
			lock_revision_id=False
	if tag=="title":
		page_title=elem.text
	
	if tag=="timestamp":
		rev_timestamp=elem.text
	
	if tag=="username" or tag=="ip":
		rev_author=elem.text
	
	if tag=="comment":
		if elem.text:
			rev_comment=elem.text
		else:
			rev_comment=''

	if tag=="text":
		if elem.text:
			rev_text=elem.text
		else:
			rev_text=''
	
	if event=="end" and tag=="page": #blanqueamos variable page_title y page_id?
		cpages+=1
		elem.clear()
		
	if event=="end" and tag=="revision":
		crevisions+=1
		elem.clear()
		if crevisions % limit == 0:
			try:
				print u'Pages: %d | Revisions: %d | Rev/pag = %.2f | %.2f pags/s | %.2f revs/s' % (cpages, crevisions, (crevisions/cpages), cpages/(time.time()-t1), (crevisions/(time.time()-t1)))
				#break
			except:
				pass
		#output rev
		#md5_=md5.new(rev_text.encode("utf-8")).hexdigest() #digest hexadecimal
		#rev_comment=re.sub(r_newlines, "", rev_comment) #eliminamos saltos de linea, curiosamente algunos comentarios tienen \n en el dump y causan problemas
		
		#rev_len=len(rev_text)
		#rev_links=len(re.findall(r_links, rev_text))
		#rev_sections=len(re.findall(r_sections, rev_text))
		#rev_images=len(re.findall(r_images, rev_text))
		#output='%s	%s	%s	%s	%s	%s	%s	%s	%s	%s	%s\n' % (page_title, page_id, rev_id, rev_timestamp, rev_author, rev_comment, md5_, rev_len, rev_links, rev_sections, rev_images)
		#print page_title, page_id, rev_id, rev_timestamp, len(rev_text)
		
		if primera_rev and not re.search(no_pattern, page_title): #es la primera red de este arbol <page>?
			primera_rev=False
			if user_creations.has_key(rev_author):
				user_creations[rev_author].append(page_title)
			else:
				user_creations[rev_author] = [page_title]
		
		#limpiamos
		rev_id=''
		rev_timestamp=''
		rev_author=''
		rev_comment=''
		rev_text=''

source.close()

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



