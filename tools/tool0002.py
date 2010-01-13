#!/usr/bin/env python
# -*- coding: utf-8 -*-

#TODO:
#no contar aquellas páginas que fueron creadas como redirecciones: http://es.wikipedia.org/w/index.php?title=Luis_Martin&action=history
#evitar que cargue todas las paginas en memoria
#ocupa menos una lista que un diccionario? dic.has_key y l.count son igual de rápidas?
import re
import gzip
import sys
from tool0000 import *
import time, os
from xml.etree.cElementTree import iterparse

tool_id="0002"
tool_title="Usuarios por número de artículos creados"
tool_desc=""

lang='zu' #idioma que será analizado
family='wiki'
if len(sys.argv)>=2:
	lang=sys.argv[1]

limite=1000 #límite de usuarios a listar, los X más creadores
if len(sys.argv)>=3:
	limite=int(sys.argv[2])

wiki="%s%s" % (lang, family)
tool_path=generateToolPath(tool_id, wiki)

os.system("rm -dfr %s" % (tool_path)) #debemos borrar listas de creaciones de usuarios del anterior análisis
os.system("mkdir -p %s" % (tool_path))

pages=set()
#page_title
os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title from page where page_namespace=0 and page_is_redirect=0;" > /home/emijrp/temporal/wikipage-%s.txt' % (lang, lang, lang))
f=open('/home/emijrp/temporal/wikipage-%s.txt' % lang, 'r')
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
		pages.add(page_title)
print 'Cargadas %d paginas de %s.wikipedia.org' % (c, lang)
f.close()

if c==0:
	print "No se ha encontrado nada"
	sys.exit()

try:
	f = gzip.open('/mnt/user-store/dump/%swiki-latest-stub-meta-history.xml.gz' % lang)
except:
	os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-stub-meta-history.xml.gz -O /mnt/user-store/dump/%swiki-latest-stub-meta-history.xml.gz' % (lang, lang, lang))
	f = gzip.open('/mnt/user-store/dump/%swiki-latest-stub-meta-history.xml.gz' % lang)

title_pattern = re.compile(ur'<title>(.*)</title>')
username_pattern = re.compile(ur'<username>(.*)</username>')
ip_pattern = re.compile(ur'<ip>(.*)</ip>')

"""
data=site.getUrl("/w/index.php?title=Special:RecentChanges&limit=0")
data=data.split('<select id="namespace" name="namespace" class="namespaceselector">')[1].split('</select>')[0]
m=re.compile(ur'<option value="([1-9]\d*)">(.*?)</option>').finditer(data)
namespaces=u''
for i in m:
	number=i.group(1)
	name=i.group(2)
	namespaces+='%s|' % name
namespaces=namespaces[:len(namespaces)-1]
"""

os.system("""mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select ns_name from toolserver.namespacename where ns_id!=0 and dbname='%swiki_p';" > /home/emijrp/temporal/namespace-%s.txt""" % (lang, lang))
g=open("/home/emijrp/temporal/namespace-%s.txt" % lang, "r")
namespaces=g.read().splitlines()
g.close()
no_pattern = re.compile(ur'(%s)\:' % namespaces)

# Este diccionario acabará teniendo un usuario (o IP) como índice y una lista
# de artículos como valor
user_creations = {}

context = iterparse(f, events=("start", "end"))
context = iter(context)

page_title=''
page_id=''
rev_id=''
rev_timestamp=''
rev_author=''
rev_comment=''
rev_text=''
lock_page_id=False
lock_revision_id=False
t1=time.time()
limit=1000
cpages=crevisions=0.0
first_rev_author=""
first_rev_timestamp="3000" #año 3000
last_rev_timestamp="1000" #año 1000
last_rev_text=""
most_recent_timestamp="1000"
for event, elem in context:
	tag=elem.tag.split("}")[1]	
	
	if event=="start" and tag=="page":
		lock_page_id=True
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
		if rev_timestamp>most_recent_timestamp:
			most_recent_timestamp=rev_timestamp
	
	if tag=="username" or tag=="ip":
		rev_author=elem.text
	
	if tag=="comment":
		rev_comment=elem.text

	if tag=="text":
		if elem.text:
			rev_text=elem.text
		else:
			rev_text=''
	if event=="end" and tag=="page":
		cpages+=1
		#apuntamos el articulo al usuario
		if page_title in pages:
			if user_creations.has_key(first_rev_author):
				user_creations[first_rev_author].append(page_title)
			else:
				user_creations[first_rev_author]=[page_title]
		elem.clear()
		first_rev_author=""
		first_rev_timestamp="3000"
		last_rev_timestamp="1000"
		last_rev_text=""
		
	if event=="end" and tag=="revision":
		if rev_timestamp<first_rev_timestamp:
			first_rev_author=rev_author
			first_rev_timestamp=rev_timestamp
		if rev_timestamp>last_rev_timestamp:
			last_rev_text=rev_text
			last_rev_timestamp=rev_timestamp
		crevisions+=1
		elem.clear()
		if crevisions % limit == 0:
			try:
				print u'Pages: %d | Revisions: %d | Rev/pag = %.2f | %.2f pags/s | %.2f revs/s' % (cpages, crevisions, (crevisions/cpages), cpages/(time.time()-t1), (crevisions/(time.time()-t1)))		
			except:
				pass
		#output rev
		output='%s	%s	%s	%s	%s	%s	%s\n' % (page_title, page_id, rev_id, rev_timestamp, rev_author, rev_comment, len(rev_text))
		#g.write(output.encode('utf-8'))
		#print page_title, page_id, rev_id, rev_timestamp, len(rev_text)
		#limpiamos
		rev_id=''
		rev_timestamp=''
		rev_author=''
		rev_comment=''
		rev_text=''

f.close()

d={}
for user, creations in user_creations.items():
	d[user]=len(creations)

#ordenamos
l = [(v, k) for k, v in d.items()]
l.sort()
l.reverse()
l = [(k, v) for v, k in l]

c=1
salida=u''
date=most_recent_timestamp.split("T")[0]
date=datetime.date(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10])) #YYYY-MM-DD
tool_archive_path=generateToolArchivePath(tool_id, tool_subdir=wiki, tool_date=date)
if not os.path.exists(tool_archive_path):
	os.makedirs(tool_archive_path)
for user, number in l:
	if (c<=limite and number>=10) or c<=100:
		if len(user)<1:
			continue
		salida+=u'%s	%d\n' % (user, number)
		if user_creations.has_key(user):
			ll=user_creations[user]
			ll.sort()
			salida2=u''
			for art in ll:
				if art not in pages:
					continue
				salida2+=u'%s\n' % (art)
			
			filename="%s-%s.txt" % (wiki, user)
			writeToFile("%s/%s" % (tool_path, filename), salida2)
			filename2="%s/%s-%s-%s.txt" % (tool_archive_path, wiki, date.isoformat(), user)
			writeToFile(filename2, salida2)
		c+=1
	else:
		break

filename="%s/%s-list-of-users-by-article-count.txt" % (tool_path, wiki)
writeToFile(filename, salida)
filename2="%s/%s-%s-list-of-users-by-article-count.txt" % (tool_archive_path, wiki, date.isoformat())
writeToFile(filename2, salida)

#os.system('rm /home/emijrp/python/pywikipedia/eswiki-latest-stub-meta-history.xml.gz') #limpiamos

