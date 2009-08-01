# -*- coding: utf-8 -*-

import gzip
import re
import sys
import os
import md5

lenguajesobjetivos=[sys.argv[1]] # de momento probar con 1 solo a la vez
lenguajefuente='en' # mirar nota1 si meto una lista en vez de individual

def percent(c):
	if c % 1000 == 0:
		#print '\nLlevamos %d' % c
		sys.stderr.write(".")

pageid2pagetitle={}
pagetitle2pageid={}
imagelinks={}
imagelinks_pattern=re.compile(ur'\((\d+)\,\'([^\']*?)\'\)')
exclusion_pattern=re.compile(ur'(?i)(\.(gif|mid|ogg|pne?g|svg)|bandera|escudo|herb|coa|blas[oó]n|icon|flag|coat|shield|wiki|logo|barnstar|dot|map|cover|tomb|tumb|grave|50 ?cent|hitler|abu|gadd?afi)') # los ' y " los filtramos al final

#cargamos templates para descartar imagenes inutiles
templates={}
print '-'*70
print 'Cargando plantillas de %s:' % (lenguajefuente)
templates[lenguajefuente]={}
os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id, page_title from page where page_namespace=10;" > /home/emijrp/temporal/%swikitemplatepageid.txt' % (lenguajefuente, lenguajefuente, lenguajefuente)) # hay que  permitir las redireccinoes? no, seria raro que una imagen estuviera en 1 red
f=open('/home/emijrp/temporal/%swikitemplatepageid.txt' % lenguajefuente, 'r')
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
		templates[lenguajefuente][pageid]=False #intentando ahorrar memoria
print '\nCargadas %d plantillas de %s:' % (c, lenguajefuente)
f.close()

#cargamos pageid/pagetitles para lenguajes objetivos
for lang in lenguajesobjetivos:
	print '-'*70
	print 'Cargando pageid/pagetitles para %s:' % (lang)
	pageid2pagetitle[lang]={}
	pagetitle2pageid[lang]={}
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
	print '\nCargados %d pageid/pagetitle para %s:' % (c, lang)
	f.close()

#cargamos imagelinks para lenguajes objetivos
for lang in lenguajesobjetivos:
	print '-'*70
	print 'Cargando imagelinks de %s:' % (lang)
	imagelinks[lang]={}
	os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select il_from, il_to from imagelinks where il_from in (select page_id from page where page_namespace=0 and page_is_redirect=0);" > /home/emijrp/temporal/%swikiimagelinks.txt' % (lang, lang, lang))
	f=open('/home/emijrp/temporal/%swikiimagelinks.txt' % lang, 'r')
	c=0
	for line in f:
		try:
			line=unicode(line, 'utf-8')
		except:
			continue
		line=line[:len(line)-1] #evitamos \n
		line=re.sub('_', ' ', line)
		trozos=line.split('	')
		if len(trozos)==2:
			pageid=trozos[0]
			image=trozos[1]
			
			#filtro
			if re.search(exclusion_pattern, image):
				continue
			
			c+=1
			percent(c)
			if imagelinks[lang].has_key(pageid):
				imagelinks[lang][pageid][image]=False
			else:
				imagelinks[lang][pageid]={image:False}
	
	print '\nCargados %d imagelinks de %s:, quitando excluidas e imagenes enlazadas desde nm!=0' % (c, lang)
	f.close()

#en imagelinks['es'] estan todos los pageid que contienen alguna imagen
#ahora rellenamos sinimagenes['es'] con pageids que no aparezcan en imagelinks['es']
sinimagenes={}
for lang in lenguajesobjetivos:
	c=0
	sinimagenes[lang]={}
	for pageid, pagetitle in pageid2pagetitle[lang].items():
		if not imagelinks[lang].has_key(pageid):
			sinimagenes[lang][pageid]=False
			c+=1
	print '\nSe encontraron %d articulos "sin imagenes utiles" en %s:' % (c, lang)

print 'Vaciamos imagelinks{}'
imagelinks={}

#cargamos interwikis a articulos de lang: carentes de imagenes
interwikis={}
for lang in lenguajesobjetivos:
	print '-'*70
	print 'Cargando interwikis de %s: hacia %s:' % (lenguajefuente, lang)
	interwikis[lenguajefuente]={}
	os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select ll_from, ll_title from langlinks where ll_lang=\'%s\';" > /home/emijrp/temporal/%swikiinterwikis-to-%s.txt' % (lenguajefuente, lenguajefuente, lang, lenguajefuente, lang))
	f=open('/home/emijrp/temporal/%swikiinterwikis-to-%s.txt' % (lenguajefuente, lang), 'r')
	c=0
	for line in f:
		try:
			line=unicode(line, 'utf-8')
		except:
			continue
		line=line[:len(line)-1] #evitamos \n
		line=re.sub('_', ' ', line)
		trozos=line.split('	')
		if len(trozos)==2:
			pageid=trozos[0]
			interwiki=trozos[1]
			
			c+=1
			percent(c)
			if pagetitle2pageid[lang].has_key(interwiki) and sinimagenes[lang].has_key(pagetitle2pageid[lang][interwiki]):
				interwikis[lenguajefuente][pageid]=interwiki
	print '\nCargados %d interwikis desde %s: hacia %s:' % (c, lenguajefuente, lang)
	f.close()

#nota1
#cargamos pageid y pagetitles solo para aquellos articulos que tienen interwiki a lang:
for lang in lenguajesobjetivos:
	print '-'*70
	print 'Cargando pageid/pagetitles de %swiki que tengan iw hacia articulos de %s: sin imagenes' % (lenguajefuente, lang)
	pageid2pagetitle[lenguajefuente]={}
	pagetitle2pageid[lenguajefuente]={}
	os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id, page_title from page where page_namespace=0 and page_is_redirect=0 and page_id in (select ll_from from langlinks where ll_lang=\'%s\');" > /home/emijrp/temporal/%swikipageid-to-%s.txt' % (lenguajefuente, lenguajefuente, lang, lenguajefuente, lang))
	f=open('/home/emijrp/temporal/%swikipageid-to-%s.txt' % (lenguajefuente, lang), 'r')
	c=0
	for line in f:
		try:
			line=unicode(line, 'utf-8')
		except:
			continue
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
	print '\nCargados %d pageid/pagetitle de %swiki que tienen iw hacia articulos de %s: sin imagenes' % (c, lenguajefuente, lang)
	f.close()

#cargamos imagenes subidas a la inglesa y que cumplan los filtros
print '-'*70
print 'Cargando imagenes de %s:' % lenguajefuente
images={}
images[lenguajefuente]={}
try:
	f=open('/home/emijrp/temporal/%swiki-images.txt' % lenguajefuente, 'r')
except:
	os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select img_name from image;" > /home/emijrp/temporal/%swiki-images.txt' % (lenguajefuente, lenguajefuente, lenguajefuente)) #no poner img_width<img_height, ya que hay que tenerlas para descartarlas
	f=open('/home/emijrp/temporal/%swiki-images.txt' % lenguajefuente, 'r')
c=0
for line in f:
	try:
		line=unicode(line, 'utf-8')
	except:
		continue
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==1:
		image=trozos[0]
		#filtro
		if re.search(exclusion_pattern, image):
			continue
		c+=1
		percent(c)
		images[lenguajefuente][image]=False
		#print image.encode('utf-8')
print '\nCargadas %d images de %swiki (descartando iconos, escudos... )' % (c, lenguajefuente)
f.close()

#cargamos las imagenes que se usan (y no estan subidas en la inglesa (están en Commons)) y en que articulos se usan
print '-'*70
print 'Cargamos imagenes que se usan en %s: y en que articulos' % lenguajefuente
candidatas={}
listanegra={}
for lang in lenguajesobjetivos:
	candidatas[lenguajefuente]={}
	try:
		f=open('/home/emijrp/temporal/%swikiimagelinks.txt' % lenguajefuente, 'r')
	except:
		os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select il_from, il_to from imagelinks where il_from in (select page_id from page where (page_namespace=0 or page_namespace=10) and page_is_redirect=0);" > /home/emijrp/temporal/%swikiimagelinks.txt' % (lenguajefuente, lenguajefuente, lenguajefuente)) #el nm 10 hace falta para descartar las imagenes de las plantillas stub, etc, y meterlas en  listanegra
		f=open('/home/emijrp/temporal/%swikiimagelinks.txt' % lenguajefuente, 'r')
	c=0
	for line in f:
		try:
			line=unicode(line, 'utf-8')
		except:
			continue
		line=line[:len(line)-1] #evitamos \n
		line=re.sub('_', ' ', line)
		trozos=line.split('	')
		if len(trozos)==2:
			pageid=trozos[0]
			image=trozos[1]
			
			if listanegra.has_key(image): #debe estar lo primero
				continue
			if templates[lenguajefuente].has_key(pageid):
				listanegra[image]=False
				continue
			
			#filtro
			if re.search(exclusion_pattern, image):
				continue
				
			#print image.encode('utf-8')
			if images[lenguajefuente].has_key(image): #comprobamossi esta subida a la inglesa
				listanegra[image]=False
				continue
			
			if not pageid2pagetitle[lenguajefuente].has_key(pageid):
				continue
			if not sinimagenes[lang].has_key(pagetitle2pageid[lang][interwikis[lenguajefuente][pageid]]):
				continue
			
			
			c+=1
			percent(c)
			#if c % 100 == 0:
			#	print c
			#	linea='[[%s]] -> [[Image:%s]]' % (interwikis[lenguajefuente][pageid], image)
			#	print linea.encode('utf-8')
			if candidatas[lenguajefuente].has_key(pageid):
				candidatas[lenguajefuente][pageid][image]=False
			else:
				candidatas[lenguajefuente][pageid]={image:False}
	f.close()
print '\nCargadas %d imagenes que se usan en articulos de %s:' % (c, lenguajefuente)
print 'Vaciamos templates{}'
templates={}

#cargamos categorylinks de la inglesa que lleven a una categoria births o deaths, para cribar biografias
categories={}
categories_pattern=re.compile(ur'\((\d+)\,\'\d+ (births|deaths)\'\,\'[^\']*?\'\,\d+\)') #no hace falta (?i)
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
		pageid=str(i[0])
		if categories[lenguajefuente].has_key(pageid):
			continue
		c+=1
		percent(c)
		categories[lenguajefuente][pageid]=False
print '\nCargadas %d categorylinks desde biografias para %swiki' % (c, lenguajefuente)
f.close()


#cargamos imagenes subidas a commons y que cumplan los filtros
images={}
images['commons']={}
try:
	f=open('/home/emijrp/temporal/commonswiki-images.txt', 'r')
except:
	os.system('mysql -h commonswiki-p.db.toolserver.org -e "use commonswiki_p;select img_name from image where img_width<img_height;" > /home/emijrp/temporal/commonswiki-images.txt')
	f=open('/home/emijrp/temporal/commonswiki-images.txt', 'r')
c=0
for line in f:
	try:
		line=unicode(line, 'utf-8')
	except:
		continue
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==1:
		image=trozos[0]
		#filtro
		if re.search(exclusion_pattern, image):
			continue
		c+=1
		percent(c)
		images['commons'][image]=False
		#print image.encode('utf-8')
print '\nCargadas %d images de commons (descartando iconos, escudos... y width>height)' % (c)
f.close()


c=0
cc=0
for lang in lenguajesobjetivos:
	f=open('/home/emijrp/temporal/candidatas-%s.txt' % lang, 'w')
	g=open('/home/emijrp/temporal/candidatas-%s.sql' % lang, 'w')
	for pageid, v in candidatas[lenguajefuente].items():
		article=pageid2pagetitle[lenguajefuente][pageid]
		if not categories[lenguajefuente].has_key(pageid): #no es biografia?
			continue
		c+=1
		for image, v2 in v.items():
			iw=interwikis[lenguajefuente][pageid]
			if re.search(ur"(?i)(abu|nidal|gadd?afi|cent)", iw):  #evitamos imagenes y articulos que no sirven o erroneas que ya se han comprobado en otras actualizacione
				continue
			trocear=u'%s %s' % (iw, article) #para aquellos idiomas como ar: con alfabetos distintos
			trocear=re.sub(ur'[\(\)]', ur'', trocear)
			trozos=trocear.split(' ')
			temp=u''
			for t in trozos:
				if len(t)>=3:
					temp+=u'%s|' % t
			
			if len(temp)>=3:
				temp=temp[:len(temp)-1]
				if not listanegra.has_key(image):
					if images['commons'].has_key(image):
						if not re.search(exclusion_pattern, image): #evitamos imagenes que no sirven o erroneas que ya se han comprobado en otras actualizaciones
							if not re.search(ur'([\'\"]|[^\d]0\d\d[^\d])', u'%s %s' % (iw, image)):
								if re.search(ur"(?i)(%s)" % temp, image):
									cc+=1
									image_=re.sub(' ', '_', image)
									md5_=md5.new(image_.encode('utf-8')).hexdigest()
									
									salida='%s;%s;%s;\n' % (article, iw, image)
									salida=salida.encode('utf-8')
									
									salida2="INSERT INTO `imagesforbio` (`id`, `language`, `article`, `image`, `url`, `done`) VALUES (NULL, '%s', '%s', '%s', 'http://upload.wikimedia.org/wikipedia/commons/%s/%s/%s', 0);\n" % (lang, iw, image, md5_[0], md5_[0:2], image_)
									salida2=salida2.encode('utf-8')
									
									try:
										f.write(salida)
									except:
										pass
									try:
										g.write(salida2)
									except:
										pass
	f.close()
	g.close()

#print '\nFinalmente se encontraron %d articulos susceptibles de ser ilustrados con %d imagenes, en %s:' % (c, cc, lang)
print '\n---->(((((Finalmente se encontraron %d imagenes, en %s:)))))<----' % (cc, lang)

