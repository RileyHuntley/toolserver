# -*- coding: utf-8 -*-

import time, re
from xml.etree.cElementTree import iterparse
import bz2, sys, md5, os
import wikipedia

#llamado con 7za e -so eowiki-20091128-pages-meta-history.xml.7z | python stubmetahistory-fetch-celementtree.py eo

lang='es' #idioma que será analizado
if len(sys.argv)>=2:
	lang=sys.argv[1]

rawtotalrevisions=0.0
site=wikipedia.Site(lang, 'wikipedia')
data=site.getUrl("/wiki/Special:Statistics?action=raw")
rawtotalrevisions+=float(data.split("edits=")[1].split(";")[0])

source=sys.stdin
outputfile="/mnt/user-store/dump/%swiki-fetched.txt.bz" % (lang)
g=bz2.BZ2File(outputfile, "w")

context = iterparse(source, events=("start", "end"))
context = iter(context)

r_newlines=re.compile(ur"(?im)[\n\r\t\s]")
r_redirect=re.compile(ur"(?i)^\s*#\s*(REDIRECCIÓN|REDIRECT)\s*\[\[[^\]]+?\]\]")
r_disambig=re.compile(ur"(?i)\{\{\s*(d[ei]sambig|desambiguaci[oó]n|des|desamb)\s*[\|\}]")
r_links=re.compile(ur"\[\[\s*[^\]]+?\s*[\]\|]")
r_categories=re.compile(ur"(?i)\[\[\s*(category|categoría)\s*\:\s*[^\]\|]+\s*[\]\|]")
r_sections=re.compile(ur"(?im)^(\=+)[^\=]+?\1")
r_templates=""
r_interwikis=re.compile(ur"(?i)\[\[\s*[a-z]{2,3}(-[a-z]{2,3})?\s*\:")
r_externallinks=re.compile(ur"://")
r_bold=""
r_italic=""
r_images=re.compile("(?i)\[\[\s*(image|file|archivo|imagen)\s*\:")
#evolucion de la complejidad de la sintaxis: cada vez más <ref> {{code}} 
r_htmltags=""
r_htmltables="" #ha ido declinando en favor de {|
#media del thumb en px de las imagenes colocadas

page_title=''
page_id=''
rev_id=''
rev_timestamp=''
rev_author=''
rev_comment=''
rev_text=''
lock_page_id=False
lock_revision_id=False
lock_username_id=False
t1=time.time()
t2=time.time()
limit=1000
cpages=crevisions=cpagesprev=crevisionsprev=0.0
md5s=[]
md5sd={}
test=[1,2]
c=10
u=False
for event, elem in context:
	tag=elem.tag.split("}")[1]	

	"""if u:  testing code for nones, vars test=[1,2] and c=10 and u=False required
		c-=1
	if c==0:
		test=test[-20:]
		test.append([event, tag, elem.text])
		print test
		time.sleep(3)
		c=10
		u=False
	if tag=='id' and elem.text==None:
		u=True
		if elem.text and len(elem.text)>40:
			elem.text=elem.text[:39]
		test.append([event, tag, elem.text])
	else:
		if elem.text and len(elem.text)>40:
			elem.text=elem.text[:39]
		test.append([event, tag, elem.text])"""
	
	#captura de ids
	if tag=="id":
		if event=="start":
			if lock_revision_id:
				if elem.text:
					rev_id=int(elem.text)
					lock_revision_id=False
			elif lock_username_id:
				if elem.text:
					rev_author_id=int(elem.text)
					lock_username_id=False
			elif lock_page_id:
				if elem.text:
					page_id=int(elem.text)
					lock_page_id=False
		elif event=="end":
			if lock_revision_id:
				if elem.text:
					rev_id=int(elem.text)
					lock_revision_id=False
				else:
					print "Dump error:", page_id
					sys.exit()
			elif lock_username_id:
				if elem.text:
					rev_author_id=int(elem.text)
					lock_username_id=False
				else:
					print "Dump error:", page_id
					sys.exit()
			elif lock_page_id:
				if elem.text:
					page_id=int(elem.text)
					lock_page_id=False
				else:
					print "Dump error:", page_id
					sys.exit()


	if event=="start":
		#switch ordenado por frecuencia de aparición
		if tag=="revision":
			lock_revision_id=True
		elif tag=="timestamp":
			rev_timestamp=elem.text
		elif tag=="username":
			lock_username_id=True
			rev_author=elem.text
		elif tag=="ip":
			rev_author=elem.text
			rev_author_id=0
		elif tag=="comment":
			if elem.text:#evitando none de blanqueos, o hay veces que no captura bien el texto?
				rev_comment=elem.text
			else:
				rev_comment=''
		elif tag=="text":
			if elem.text:
				rev_text=elem.text
			else:
				rev_text=''
		elif tag=="title":
			page_title=elem.text
			#print page_title
		elif tag=="page":
			lock_page_id=True
	elif event=="end":
		if tag=="page":
			cpages+=1
			elem.clear()
		elif tag=="revision":
			elem.clear()
			crevisions+=1
			if page_id==None or rev_id==None:
				print page_title, page_id, rev_id, rev_timestamp, rev_author, rev_comment
				sys.exit()
			if crevisions % limit == 0:
				try:
					pagesspeed=(cpages-cpagesprev)/(time.time()-t2)
					revisionsspeed=(crevisions-crevisionsprev)/(time.time()-t2)
					secondsleft=((rawtotalrevisions-crevisions)/revisionsspeed)
					print u'Pages: %d | Revisions: %d | Rev/pag = %.2f | %.2f pags/s | %.2f revs/s | ETA %.0f minutes (%.2f hours, %.2f days)' % (cpages, crevisions, (crevisions/cpages), pagesspeed, revisionsspeed, secondsleft/60.0, secondsleft/3600.0, secondsleft/86400)
				except:
					pass
				t2=time.time()
				crevisionsprev=crevisions
				cpagesprev=cpages
			#output rev
			md5_=md5.new(rev_text.encode("utf-8")).hexdigest() #digest hexadecimal
			rev_comment=re.sub(r_newlines, " ", rev_comment) #eliminamos saltos de linea, curiosamente algunos comentarios tienen \n en el dump y causan problemas
			rev_len=len(rev_text)
			rev_links=len(re.findall(r_links, rev_text))
			rev_sections=len(re.findall(r_sections, rev_text))
			rev_images=len(re.findall(r_images, rev_text))
			rev_interwikis=len(re.findall(r_interwikis, rev_text))
			rev_externallinks=len(re.findall(r_externallinks, rev_text))
			rev_type=0
			if re.search(r_redirect, rev_text):
				rev_type=1
			elif re.search(r_disambig, rev_text):
				rev_type=2
			output='%s	%s	%s	%s	%s	%s	%s	%s	%s	%s	%s	%s	%s	%s\n' % (page_title, page_id, rev_id, rev_timestamp, rev_author, rev_comment, md5_, rev_len, rev_type, rev_links, rev_sections, rev_images, rev_interwikis, rev_externallinks)
			#print output
			g.write(output.encode('utf-8'))
			#print page_title, page_id, rev_id, rev_timestamp, len(rev_text)
			#limpiamos
			rev_id=''
			rev_timestamp=''
			rev_author=''
			rev_comment=''
			rev_text=''

source.close()
g.close()

def unique(list):
	dict={}
	for row in list:
		dict[row]=False
	list=[]
	for k, v in dict.items():
		list.append(k)
	return list

"""
#evolución de la media del tamaño de los artículos
#hay que tener en cuenta el estado de todos los artículos en el mes o día dado, no vale con contar solo las edicions de ese dia o mes
g=open(outputfile, 'r')
for l in g:
	l=unicode(l[:len(l)-1], "utf-8")
	t=l.split("	")
	rev_len=t[7]
	
g.close()
"""

"""
#usuarios con mas reversiones
os.system("sort +0 -1 %s > zzzsorted.txt" % outputfile) #
g=open("zzzsorted.txt", "r")
page_title=""
page_title_old=""
revs=[]
ranking={}
for l in g:
	l=unicode(l[:len(l)-1], "utf-8")
	t=l.split("	")
	#print t
	page_title=t[0]
	rev_timestamp=t[3]
	rev_author=t[4]
	md5_=t[6]
	if page_title_old==page_title:
		revs.append([rev_timestamp, rev_author, md5_])
	else: #evitamos primer caso vacio
		revs.sort()
		#print revs
		unique_md5=[]
		for rev in revs:
			#print rev
			if rev[2] in unique_md5:
				if ranking.has_key(rev[1]):
					ranking[rev[1]]+=1
				else:
					ranking[rev[1]]=1
			else:
				unique_md5.append(rev[2])
		page_title_old=page_title
		revs=[[rev_timestamp, rev_author, md5_]]
ranking_=[]
for k, v in ranking.items():
	ranking_.append([v, k])
ranking_.sort()
for k, v in ranking_:
	print k, v
g.close()
"""

"""
#paginas con mas reversiones

os.system("sort +0 -1 %s > zzzsorted.txt" % outputfile) #ordenamos por pagetitle
g=open("zzzsorted.txt", "r")
page_title=""
page_title_old=""
md5s=[]
ranking=[]
for l in g:
	l=unicode(l[:len(l)-1], "utf-8")
	t=l.split("	")
	#print t
	page_title=t[0]
	md5_=t[6]
	if page_title_old==page_title:
		md5s.append(md5_)
	else: #evitamos primer caso vacio
		ranking.append([len(md5s)-len(unique(md5s)), page_title_old])
		page_title_old=page_title
		md5s=[md5_]
	#el ultimo caso, que no coge un page_title nuevo tb hay que controlarlo
ranking.sort()
for k, v in ranking:
	print k, v
g.close()

"""


