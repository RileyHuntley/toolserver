# -*- coding: utf-8 -*-

import re
import gzip
import sys
sys.path.append('/home/emijrp/public_html/tool0000')
import tool0000
import time, os
from xml.etree.cElementTree import iterparse

tool_id="0002"
tool_title="Usuarios por número de artículos creados"
tool_desc=""
path=tool0000.generateToolPath(tool_id)

lang='zu' #idioma que será analizado
family='wiki'
if len(sys.argv)>=2:
	lang=sys.argv[1]

limite=500 #límite de usuarios a listar, los X más creadores
if len(sys.argv)>=3:
	limite=int(sys.argv[2])

pages={}
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
		pages[page_title]=0
print 'Cargadas %d paginas de %s.wikipedia.org' % (c, lang)
f.close()

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

os.system("mysql -h eswiki-p.db.toolserver.org -e \"use eswiki_p;select ns_name from toolserver.namespacename where ns_id!=0 and dbname='%swiki_p';\" > /home/emijrp/temporal/namespace-%s.txt" % (lang, lang))
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
first_rev_timestamp="3000"
last_rev_timestamp="1000"
last_rev_text=""
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
		if pages.has_key(page_title):
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


limite2=1000 #paginas por lista
c=1
salida=u''
os.system("rm -dfr %s%s%s" % (path, lang, family))
os.system("mkdir -p %s%s%s" % (path, lang, family))
for user, number in l:
	if (c<=limite and number>=50) or c<=15:
		if len(user)<1:
			continue
		salida+=u'%s	%d\n' % (user, number)
		if user_creations.has_key(user):
			ll=user_creations[user]
			ll.sort()
			salida2=u''
			for art in ll:
				if not pages.has_key(art):
					continue
				salida2+=u'%s\n' % (art)
			
			g=open("%s%s%s/%s%s-%s.txt" % (path, lang, family, lang, family, user), "w")
			g.write(salida2.encode("utf-8"))
			g.close()
		c+=1
	else:
		break

f=open("%slist-of-wikipedians-by-article-count-%s-%s.txt" % (path, lang, family), "w")
f.write(salida.encode("utf-8"))
f.close()
#os.system('rm /home/emijrp/python/pywikipedia/eswiki-latest-stub-meta-history.xml.gz') #limpiamos
