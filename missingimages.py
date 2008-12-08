# -*- coding: utf-8 -*-

import gzip
import re
import sys
import os
import md5

lenguajesobjetivos=[sys.argv[1]] # de momento probar con 1 solo a la vez
lenguajefuente='en' # mirar nota1 si meto una lista en vez de individual

#los False son para ahorrar memoria

def percent(c):
	if c % 100000 == 0:
		print 'Llevamos %d' % c

pageid2pagetitle={}
pagetitle2pageid={}
imagelinks={}
imagelinks_pattern=re.compile(ur'\((\d+)\,\'([^\']*?)\'\)')
exclusion_pattern=re.compile(ur'(?i)(\.(gif|mid|ogg|pne?g|svg)|[\'\(\)]|bandera|escudo|coa|blas[oó]n|icon|flag|coat|shield|wiki|logo|barnstar|dot|map|cover)')

#cargamos templates para descartar imagenes inutiles
templates={}
for lang in ['en']:
	print 'Cargando templates para %swiki' % (lang)
	templates[lang]={}
	try:
		f=open('/home/emijrp/temporal/%swikitemplatepageid.txt' % lang, 'r')
	except:
		os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id, page_title from page where page_namespace=10;" > /home/emijrp/temporal/%swikitemplatepageid.txt' % (lang, lang, lang)) # hay que  permitir las redireccinoes?
		f=open('/home/emijrp/temporal/%swikitemplatepageid.txt' % lang, 'r')
	c=0
	for line in f:
		line=unicode(line, 'utf-8')
		line=line[:len(line)-1] #evitamos \n
		line=re.sub('_', ' ', line)
		trozos=line.split('	')
		if len(trozos)>=2:
			pageid=trozos[0]
			pagetitle=trozos[1]
			c+=1
			percent(c)
			templates[lang][pageid]=False #intentando ahorrar memoria
	print 'Cargadas %d templates para %swiki' % (c, lang)
	f.close()

#cargamos pageid/pagetitles para lenguajes objetivos
for lang in lenguajesobjetivos:
	print 'Cargando pageid/pagetitles para %swiki' % (lang)
	pageid2pagetitle[lang]={}
	pagetitle2pageid[lang]={}
	try:
		f=open('/home/emijrp/temporal/%swikipageid.txt' % lang, 'r')
	except:
		os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id, page_title from page where page_namespace=0 and page_is_redirect=0;" > /home/emijrp/temporal/%swikipageid.txt' % (lang, lang, lang))
		f=open('/home/emijrp/temporal/%swikipageid.txt' % lang, 'r')
	c=0
	for line in f:
		line=unicode(line, 'utf-8')
		line=line[:len(line)-1] #evitamos \n
		line=re.sub('_', ' ', line)
		trozos=line.split('	')
		if len(trozos)==2:
			pageid=trozos[0]
			pagetitle=trozos[1]
			c+=1
			percent(c)
			pageid2pagetitle[lang][pageid]=pagetitle
			pagetitle2pageid[lang][pagetitle]=pageid
	print 'Cargados %d pageid/pagetitle para %swiki' % (c, lang)
	f.close()

#cargamos imagelinks para lenguajes objetivos
for lang in lenguajesobjetivos:
	print 'Cargando imagelinks para %swiki' % (lang)
	imagelinks[lang]={}
	try:
		f=gzip.open('/mnt/user-store/%swiki-latest-imagelinks.sql.gz' % lang, 'r')
	except:
		os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-imagelinks.sql.gz -O /mnt/user-store/%swiki-latest-imagelinks.sql.gz' % (lang, lang, lang))
		f=gzip.open('/mnt/user-store/%swiki-latest-imagelinks.sql.gz' % lang, 'r')
	c=0
	for line in f:
		line=re.sub('_', ' ', line)
		m=re.findall(imagelinks_pattern, line)
		for i in m:
			pageid=i[0]
			image=i[1]
			try:
				image=unicode(image, 'utf-8')
			except:
				continue
			#filtro
			if re.search(exclusion_pattern, image):
				continue
			c+=1
			percent(c)
			if imagelinks[lang].has_key(pageid):
				imagelinks[lang][pageid][image]=False
			else:
				imagelinks[lang][pageid]={image:False}
	print 'Cargados %d imagelinks para %swiki, quitando excluidas' % (c, lang)
	f.close()

#en imagelinks['es'] estan todos los pageid que contienen alguna imagen
#ahora rellenamos sinimagenes['es'] con pageids que no aparezcan en imagelinks['es']
sinimagenes={}
for lang in lenguajesobjetivos:
	c=0
	sinimagenes[lang]={}
	for pageid, basura in pageid2pagetitle[lang].items():
		if not imagelinks[lang].has_key(pageid):
			sinimagenes[lang][pageid]=False
			c+=1
	print 'Se encontraron %d articulos sin imagenes en %swiki' % (c, lang)

print 'Vaciamos imagelinks{}'
imagelinks={}

#cargamos interwikis a articulos en español carentes de imagenes
interwikis={}
for lang in lenguajesobjetivos:
	interwikis_pattern=re.compile(ur'\((\d+)\,\'%s\'\,\'([^\']*?)\'\)' % lang)
	# (2286,'aa','Category:User sk'),
	print 'Cargando interwikis para %swiki' % (lenguajefuente)
	interwikis[lenguajefuente]={}
	try:
		f=gzip.open('/mnt/user-store/%swiki-latest-langlinks.sql.gz' % lenguajefuente, 'r')
	except:
		os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-langlinks.sql.gz -O /mnt/user-store/%swiki-latest-langlinks.sql.gz' % (lenguajefuente, lenguajefuente, lenguajefuente))
		f=gzip.open('/mnt/user-store/%swiki-latest-langlinks.sql.gz' % lenguajefuente, 'r')
	c=0
	for line in f:
		line=re.sub('_', ' ', line)
		m=re.findall(interwikis_pattern, line)
		for i in m:
			pageid=i[0]
			interwiki=i[1]
			try:
				interwiki=unicode(interwiki, 'utf-8')
				c+=1
				percent(c)
			except:
				continue
			if pagetitle2pageid[lang].has_key(interwiki) and sinimagenes[lang].has_key(pagetitle2pageid[lang][interwiki]):
				interwikis[lenguajefuente][pageid]=interwiki
	print 'Cargadas %d interwikis para %swiki' % (c, lenguajefuente)
	f.close()

#nota1
#cargamos pageid y pagetitles solo para aquellos articulos que tienen interwiki a es:
for lang in lenguajesobjetivos:
	print 'Cargando pageid/pagetitles para %swiki que tengan iw a %s:' % (lenguajefuente, lang)
	pageid2pagetitle[lenguajefuente]={}
	pagetitle2pageid[lenguajefuente]={}
	try:
		f=open('/home/emijrp/temporal/%swikipageid.txt' % lenguajefuente, 'r')
	except:
		os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id, page_title from page where page_namespace=0 and page_is_redirect=0;" > /home/emijrp/temporal/%swikipageid.txt' % (lenguajefuente, lenguajefuente, lenguajefuente))
		f=open('/home/emijrp/temporal/%swikipageid.txt' % lenguajefuente, 'r')
	c=0
	for line in f:
		line=unicode(line, 'utf-8')
		line=line[:len(line)-1] #evitamos \n
		line=re.sub('_', ' ', line)
		trozos=line.split('	')
		if len(trozos)==2:
			pageid=trozos[0]
			pagetitle=trozos[1]
			if interwikis[lenguajefuente].has_key(pageid):
				c+=1
				percent(c)
				pageid2pagetitle[lenguajefuente][pageid]=pagetitle
				#pagetitle2pageid[lenguajefuente][pagetitle]=pageid
	print 'Cargados %d pageid/pagetitle para %swiki que tienen iw a %s:' % (c, lenguajefuente, lang)
	f.close()

#cargamos imagenes subidas a la inglesa
images={}
images_pattern=re.compile(ur'\(\'([^\']*?)\'\,\d+\,\d+\,\d+\,\'.*?\'\,\d+\,\'.*?\'\,\'.*?\'\,\'.*?\'\,\'.*?\'\,\d+\,\'.*?\'\,\'.*?\'\,\'.*?\'\)')
#('1merkel.jpg',28359,360,500,'0',8,'BITMAP','image','jpeg','',29,'Test user','20050925014209','tbx5vswxtokje1o8to0tl1o5ccnje3h')
images[lenguajefuente]={}
try:
	f=gzip.open('/mnt/user-store/%swiki-latest-image.sql.gz' % lenguajefuente, 'r')
except:
	os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-image.sql.gz -O /mnt/user-store/%swiki-latest-image.sql.gz' % (lenguajefuente, lenguajefuente, lenguajefuente))
	f=gzip.open('/mnt/user-store/%swiki-latest-image.sql.gz' % lenguajefuente, 'r')
c=0
for line in f:
	line=re.sub('_', ' ', line)
	m=re.findall(images_pattern, line)
	for i in m:
		image=i
		try:
			image=unicode(image, 'utf-8')
		except:
			continue
		#filtro
		if re.search(exclusion_pattern, image):
			continue
		c+=1
		percent(c)
		images[lenguajefuente][image]=False
		#print image.encode('utf-8')
print 'Cargadas %d images para %swiki' % (c, lenguajefuente)
f.close()

#cargamos las imagenes que se usan (y no estan subidas en la inglesa (están en Commons)) y en que articulos se usan
candidatas={}
listanegra={}
for lenguajeobjetivo in lenguajesobjetivos:
	candidatas[lenguajefuente]={}
	try:
		f=gzip.open('/mnt/user-store/%swiki-latest-imagelinks.sql.gz' % lenguajefuente, 'r')
	except:
		os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-imagelinks.sql.gz -O /mnt/user-store/%swiki-latest-imagelinks.sql.gz' % (lenguajefuente, lenguajefuente, lenguajefuente))
		f=gzip.open('/mnt/user-store/%swiki-latest-imagelinks.sql.gz' % lenguajefuente, 'r')
	c=0
	for line in f:
		line=re.sub('_', ' ', line)
		m=re.findall(imagelinks_pattern, line)
		for i in m:
			pageid=i[0]
			image=i[1]
			try:
				image=unicode(image, 'utf-8')
			except:
				continue
			
			#filtro
			if re.search(exclusion_pattern, image):
				continue
			
			if listanegra.has_key(image):
				continue
			if templates[lenguajefuente].has_key(pageid):
				listanegra[image]=False
				continue
			if not pageid2pagetitle[lenguajefuente].has_key(pageid):
				continue
			
			
			"""#filtro
			if re.search(exclusion_pattern, image):
				continue"""
			#print image.encode('utf-8')
			if images[lenguajefuente].has_key(image): #comprobamossi esta subida a la inglesa
				continue
			
			if not sinimagenes[lenguajeobjetivo].has_key(pagetitle2pageid[lenguajeobjetivo][interwikis[lenguajefuente][pageid]]):
				continue
			
			c+=1
			#if c % 100 == 0:
			#	print c
			#	linea='[[%s]] -> [[Image:%s]]' % (interwikis[lenguajefuente][pageid], image)
			#	print linea.encode('utf-8')
			if candidatas[lenguajefuente].has_key(pageid):
				candidatas[lenguajefuente][pageid][image]=False
			else:
				candidatas[lenguajefuente][pageid]={image:False}
	f.close()

print 'Vaciamos templates{}'
templates={}

#cargamos categorylinks de la inglesa que lleven a una categoria births o deaths, para cribar biografias
categories={}
categories_pattern=re.compile(ur'\((\d+)\,\'\d+ (births|deaths)\'\,\'[^\']*?\'\,\d+\)')
# (1031,'1950 births','Blabla, Antonio',20080805144158)
categories[lenguajefuente]={}
try:
	f=gzip.open('/mnt/user-store/%swiki-latest-categorylinks.sql.gz' % lenguajefuente, 'r')
except:
	os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-categorylinks.sql.gz -O /mnt/user-store/%swiki-latest-categorylinks.sql.gz' % (lenguajefuente, lenguajefuente, lenguajefuente))
	f=gzip.open('/mnt/user-store/%swiki-latest-categorylinks.sql.gz' % lenguajefuente, 'r')
c=0
for line in f:
	line=re.sub('_', ' ', line)
	m=re.findall(categories_pattern, line)
	for i in m:
		pageid=i[0]
		if categories[lenguajefuente].has_key(pageid):
			continue
		c+=1
		percent(c)
		categories[lenguajefuente][pageid]=False
print 'Cargadas %d categorylinks desde biografias para %swiki' % (c, lenguajefuente)
f.close()


c=0
for lenguajeobjetivo in lenguajesobjetivos:
	f=open('/home/emijrp/temporal/candidatas-%s.txt' % lenguajeobjetivo, 'w')
	g=open('/home/emijrp/temporal/candidatas-%s.sql' % lenguajeobjetivo, 'w')
	for k, v in candidatas[lenguajefuente].items():
		if not categories[lenguajefuente].has_key(k): #no es biografia?
			continue
		for k2, v2 in v.items():
			if not listanegra.has_key(k2):
				c+=1
				k2_=re.sub(' ', '_', k2)
				md5_=md5.new(k2_.encode('utf-8')).hexdigest()
				salida='%s;%s;%s;\n' % (pageid2pagetitle[lenguajefuente][k], interwikis[lenguajefuente][k], k2)
				salida=salida.encode('utf-8')
				
				salida2="INSERT INTO `imagesforbio` (`id`, `language`, `article`, `image`, `url`, `done`) VALUES (NULL, '%s', '%s', '%s', 'http://upload.wikimedia.org/wikipedia/commons/%s/%s/%s', 0);\n" % (lenguajeobjetivo, interwikis[lenguajefuente][k], k2, md5_[0], md5_[0:2], k2_)
				salida2=salida2.encode('utf-8')
				#print salida
				f.write(salida)
				g.write(salida2)
	f.close()
	g.close()

print 'Finalmente se encontraron %d articulos susceptibles de ser ilustrados en %s:' % (c, lenguajeobjetivo)
