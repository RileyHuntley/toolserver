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

import gzip
import re
import sys
import os
import md5
import time

lenguajeobjetivo=sys.argv[1] # de momento probar con 1 solo a la vez
lenguajefuente='en' # mirar nota1 si meto una lista en vez de individual

def percent(c):
	if c % 1000 == 0:
		#print '\nLlevamos %d' % c
		sys.stderr.write(".")

pagetitle2pageid={}
pageid2pagetitle={}
imagelinks={}
imagelinks_pattern=re.compile(ur'\((\d+)\,\'([^\']*?)\'\)')
exclusion_pattern=re.compile(ur'(?i)(\.(gif|mid|ogg|pne?g|svg)|bandera|escudo|herb|coa|blas[oó]n|icon|flag|coat|shield|wiki|logo|barnstar|dot|map|cover|tomb|tumb|grave|50 ?cent|hitler|abu|gadd?afi)') # los ' y " los filtramos al final

#cargamos templates para descartar imagenes inutiles
templates=set()
print '-'*70
print 'Cargando plantillas de %s:' % (lenguajefuente)
#nota1 templates[lenguajefuente]=[]
filename='/home/emijrp/temporal/%swikitemplatepageid.txt' % lenguajefuente
os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id from page where page_namespace=10;" > %s' % (lenguajefuente, lenguajefuente, filename)) # hay que  permitir las redireccinoes? no, seria raro que una imagen estuviera en 1 red
f=open(filename, 'r')
c=0
for line in f:
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	#line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==1:
		pageid=trozos[0]
		#pagetitle=trozos[1] #page_title no sirve de momento
		c+=1
		percent(c)
		templates.add(pageid)
print '\nCargadas %d plantillas de %s:' % (c, lenguajefuente)
f.close()

#cargamos pageid/pagetitles para lenguajes objetivos
print '-'*70
print 'Cargando pageid/pagetitles para %s:' % (lenguajeobjetivo)
filename='/home/emijrp/temporal/%swikipageid.txt' % lenguajeobjetivo
os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id, page_title from page where page_namespace=0 and page_is_redirect=0;" > %s' % (lenguajeobjetivo, lenguajeobjetivo, filename))
f=open(filename, 'r')
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
		pageid2pagetitle[pageid]=pagetitle
		pagetitle2pageid[pagetitle]=pageid
print '\nCargados %d pageid/pagetitle para %s:' % (c, lenguajeobjetivo)
f.close()

if c==0:
	sys.exit()

#cargamos imagelinks para lenguajes objetivos
print '-'*70
print 'Cargando imagelinks de %s:' % (lenguajeobjetivo)
imagelinks=set()
filename='/home/emijrp/temporal/%swikiimagelinks.txt' % lenguajeobjetivo
os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select il_from, il_to from imagelinks inner join page on il_from=page_id where page_namespace=0 and page_is_redirect=0;" > %s' % (lenguajeobjetivo, lenguajeobjetivo, filename))
f=open(filename, 'r')
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
		if not pageid in imagelinks:
			imagelinks.add(pageid)

print '\nCargados %d imagelinks de %s:, quitando excluidas e imagenes enlazadas desde nm!=0' % (c, lenguajeobjetivo)
f.close()

#en imagelinks estan todos los pageid que contienen alguna imagen
#ahora rellenamos sinimagenes con pageids que no aparezcan en imagelinks
sinimagenes=set()
c=0
for pageid, pagetitle in pageid2pagetitle.items():
	if not pageid in imagelinks:
		sinimagenes.add(pageid)
		c+=1
print '\nSe encontraron %d articulos "sin imagenes utiles" en %s:' % (c, lenguajeobjetivo)

print 'Vaciamos imagelinks'
imagelinks.clear() # no sirve?

#cargamos interwikis a articulos de lenguajeobjetivo carentes de imagenes
print '-'*70
print 'Cargando interwikis de %s: hacia %s:' % (lenguajefuente, lenguajeobjetivo)
interwikis={}
filename='/home/emijrp/temporal/%swikiinterwikis-to-%s.txt' % (lenguajefuente, lenguajeobjetivo)
os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select ll_from, ll_title from langlinks where ll_lang=\'%s\';" > %s' % (lenguajefuente, lenguajefuente, lenguajeobjetivo, filename))
f=open(filename, 'r')
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
		if pagetitle2pageid.has_key(interwiki) and pagetitle2pageid[interwiki] in sinimagenes:
			interwikis[pageid]=interwiki
print '\nCargados %d interwikis desde %s: hacia %s:' % (c, lenguajefuente, lenguajeobjetivo)
f.close()

#nota1
#cargamos pageid y pagetitles solo para aquellos articulos que tienen interwiki a lang:
print '-'*70
print 'Cargando pageid/pagetitles de %swiki que tengan iw hacia articulos de %s: sin imagenes' % (lenguajefuente, lenguajeobjetivo)
pageid2pagetitle2={}
pagetitle2pageid2={}
filename='/home/emijrp/temporal/%swikipageid-to-%s.txt' % (lenguajefuente, lenguajeobjetivo)
os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id, page_title from page inner join langlinks on ll_from=page_id where page_namespace=0 and page_is_redirect=0 and ll_lang=\'%s\';" > %s' % (lenguajefuente, lenguajefuente, lenguajeobjetivo, filename))
#os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id, page_title from page where page_namespace=0 and page_is_redirect=0 and page_id in (select ll_from from langlinks where ll_lang=\'%s\');" > %s' % (lenguajefuente, lenguajefuente, lenguajeobjetivo, filename))
f=open(filename, 'r')
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
		if interwikis.has_key(pageid):
			c+=1
			percent(c)
			pageid2pagetitle2[pageid]=pagetitle
			#pagetitle2pageid2[pagetitle]=pageid
print '\nCargados %d pageid/pagetitle de %swiki que tienen iw hacia articulos de %s: sin imagenes' % (c, lenguajefuente, lenguajeobjetivo)
f.close()

#cargamos imagenes subidas a la inglesa y que cumplan los filtros
print '-'*70
print 'Cargando imagenes de %s:' % lenguajefuente
images=set()
filename='/home/emijrp/temporal/%swiki-images.txt' % lenguajefuente
try:
	f=open(filename, 'r')
except:
	os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select img_name from image;" > %s' % (lenguajefuente, lenguajefuente, filename)) #no poner img_width<img_height, ya que hay que tenerlas para descartarlas
	f=open(filename, 'r')
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
		images.add(image)
		#print image.encode('utf-8')
print '\nCargadas %d images de %swiki (descartando iconos, escudos... )' % (c, lenguajefuente)
f.close()

#cargamos las imagenes que se usan (y no estan subidas en la inglesa (están en Commons)) y en que articulos se usan
print '-'*70
print 'Cargamos imagenes que se usan en %s: y en que articulos' % lenguajefuente
candidatas={}
listanegra=set()
filename='/home/emijrp/temporal/%swikiimagelinks.txt' % lenguajefuente
try:
	f=open(filename, 'r')
except:
	os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select il_from, il_to from imagelinks inner join page on il_from=page_id where (page_namespace=0 or page_namespace=10) and page_is_redirect=0;" > %s' % (lenguajefuente, lenguajefuente, filename)) #el nm 10 hace falta para descartar las imagenes de las plantillas stub, etc, y meterlas en  listanegra
	#os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select il_from, il_to from imagelinks where il_from in (select page_id from page where (page_namespace=0 or page_namespace=10) and page_is_redirect=0);" > %s' % (lenguajefuente, lenguajefuente, filename)) #el nm 10 hace falta para descartar las imagenes de las plantillas stub, etc, y meterlas en  listanegra
	f=open(filename, 'r')
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
		
		if image in listanegra: #debe estar lo primero
			continue
		if pageid in templates:
			listanegra.add(image)
			continue
		
		#filtro
		if re.search(exclusion_pattern, image):
			continue
			
		#print image.encode('utf-8')
		if image in images: #comprobamos si esta subida a la inglesa
			listanegra.add(image)
			continue
		
		if not pageid2pagetitle2.has_key(pageid):
			continue
		if not pagetitle2pageid[interwikis[pageid]] in sinimagenes:
			continue
		
		
		c+=1
		percent(c)
		#if c % 100 == 0:
		#	print c
		#	linea='[[%s]] -> [[Image:%s]]' % (interwikis[pageid], image)
		#	print linea.encode('utf-8')
		if candidatas.has_key(pageid):
			candidatas[pageid].append(image)
		else:
			candidatas[pageid]=[image]
f.close()
print '\nCargadas %d imagenes que se usan en articulos de %s: y nos pueden servir quizas (candidatas)' % (c, lenguajefuente)
print 'Vaciamos templates'
templates.clear()


#cargamos categorylinks de la inglesa que lleven a una categoria births o deaths, para cribar biografias
categories=set()
categories_pattern=re.compile(ur"\((\d+)\,\'\d+ (births|deaths)\'\,\'[^\']*?\'\,\d+\)") #no hace falta (?i)
# (1031,'1950 births','Blabla, Antonio',20080805144158)
filename='/mnt/user-store/%swiki-latest-categorylinks.sql.gz' % lenguajefuente
try:
	f=gzip.open(filename, 'r')
except:
	os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-categorylinks.sql.gz -O %s' % (lenguajefuente, lenguajefuente, filename))
	f=gzip.open(filename, 'r')
c=0
for line in f:
	line=re.sub('_', ' ', line)
	m=re.findall(categories_pattern, line)
	for i in m:
		pageid=str(i[0])
		if pageid in categories:
			continue
		c+=1
		percent(c)
		categories.add(pageid)
print '\nCargadas %d categorylinks desde biografias para %swiki' % (c, lenguajefuente)
f.close()


#cargamos imagenes subidas a commons y que cumplan los filtros
images.clear()
imagescommons=set()
filename='/home/emijrp/temporal/commonswiki-images.txt'
try:
	f=open(filename, 'r')
except:
	os.system('mysql -h commonswiki-p.db.toolserver.org -e "use commonswiki_p;select img_name from image where img_width<img_height;" > %s' % filename)
	f=open(filename, 'r')
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
		imagescommons.add(image)
		#print image.encode('utf-8')
print '\nCargadas %d images de commons (descartando iconos, escudos... y width>height)' % (c)
f.close()


c=0
cc=0
f=open('/home/emijrp/temporal/candidatas-%s.txt' % lenguajeobjetivo, 'w')
g=open('/home/emijrp/temporal/candidatas-%s.sql' % lenguajeobjetivo, 'w')
for pageid, v in candidatas.items():
	article=pageid2pagetitle2[pageid]
	if not pageid in categories: #no es biografia?
		continue
	c+=1
	for image in v:
		iw=interwikis[pageid]
		if re.search(ur"(?i)(abu|nidal|gadd?afi|cent)", iw):  #evitamos imagenes y articulos que no sirven o erroneas que ya se han comprobado en otras actualizacione
			continue
		trocear=u'%s %s' % (iw, article) #para aquellos idiomas como ar: con alfabetos distintos
		trocear=re.sub(ur'[\(\)]', ur'', trocear)
		trozos=trocear.split(' ')
		trozos2=[]
		for t in trozos:
			if len(t)>=3:
				trozos2.append(t)
		temp="|".join(trozos2)
		
		if len(temp)>=3:
			if not image in listanegra:
				if image in imagescommons:
					if not re.search(exclusion_pattern, image): #evitamos imagenes que no sirven o erroneas que ya se han comprobado en otras actualizaciones
						if not re.search(ur'([\'\"]|[^\d]0\d\d[^\d])', u'%s %s' % (iw, image)): #?
							if re.search(ur"(?i)(%s)" % temp, image):
								cc+=1
								image_=re.sub(' ', '_', image)
								md5_=md5.new(image_.encode('utf-8')).hexdigest()
								
								salida='%s;%s;%s;\n' % (article, iw, image)
								salida=salida.encode('utf-8')
								
								salida2="INSERT INTO `imagesforbio` (`id`, `language`, `article`, `image`, `url`, `done`) VALUES (NULL, '%s', '%s', '%s', 'http://upload.wikimedia.org/wikipedia/commons/%s/%s/%s', 0);\n" % (lenguajeobjetivo, iw, image, md5_[0], md5_[0:2], image_)
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

#print '\nFinalmente se encontraron %d articulos susceptibles de ser ilustrados con %d imagenes, en %s:' % (c, cc, lenguajeobjetivo)
print '\n---->(((((Finalmente se encontraron %d imagenes posiblemente utiles, en %s:)))))<----' % (cc, lenguajeobjetivo)

