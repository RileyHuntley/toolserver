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
import wikipedia
import MySQLdb
import tarea000

lenguajeobjetivo=sys.argv[1] # de momento probar con 1 solo a la vez
lenguajefuente='en' # mirar nota1 si meto una lista en vez de individual
family='wikipedia'

def percent(c):
	if c % 1000 == 0:
		#print '\nLlevamos %d' % c
		sys.stderr.write(".")

pagetitle2pageid={}
pageid2pagetitle={}
pageid2pagetitle2={}
pagetitle2pageid2={}
sinimagenes=set()
interwikis={}
imagescommons=set()
imagelinks_pattern=re.compile(ur"\((\d+)\,\'([^\']+?)\'\)")
ex=ur'(?i)(%s)' % ('|'.join(wikipedia.Page(wikipedia.Site("en", "wikipedia"), u"User:Emijrp/Images for biographies/Exclusions").get().splitlines()))
exclusion_pattern=re.compile(ex) # los ' y " los filtramos al final
print "Excluyendo", ex

#cargamos pageid/pagetitles para lenguajes objetivos
print '-'*70
print 'Cargando pageid/pagetitles para %s:' % (lenguajeobjetivo)
dbname=tarea000.getDbname(lenguajeobjetivo, family)
server=tarea000.getServer(lenguajeobjetivo, family)
conn = MySQLdb.connect(host='sql-s%s' % server, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("select page_id, page_title from page where page_namespace=0 and page_is_redirect=0;")
row=cursor.fetchone()
c=0
while row:
	pageid=int(row[0])
	pagetitle=re.sub('_', ' ', row[1])
	c+=1
	percent(c)
	pageid2pagetitle[pageid]=pagetitle
	pagetitle2pageid[pagetitle]=pageid
	row=cursor.fetchone()
cursor.close()
conn.close()
print '\nCargados %d pageid/pagetitle para %s:' % (c, lenguajeobjetivo)

if c==0: #f
	sys.exit()

#ahora rellenamos sinimagenes con page_ids que no tengan ningún imagelink
print '-'*70
print 'Cargando imagelinks de %s:' % (lenguajeobjetivo)
dbname=tarea000.getDbname(lenguajeobjetivo, family)
server=tarea000.getServer(lenguajeobjetivo, family)
conn = MySQLdb.connect(host='sql-s%s' % server, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("select page_id from page where page_namespace=0 and page_is_redirect=0 and page_id not in (select distinct il_from from imagelinks inner join page on il_from=page_id where page_namespace=0 and page_is_redirect=0);")
row=cursor.fetchone()
c=0
while row:
	pageid=int(row[0])
	c+=1
	percent(c)
	sinimagenes.add(pageid)
	row=cursor.fetchone()
cursor.close()
conn.close()
print '\nSe encontraron %d articulos sin imagenes en %s:' % (c, lenguajeobjetivo) #sin ninguna, hasta las que tienen commons.svg se excluyen ?

#cargamos interwikis a articulos de lenguajeobjetivo carentes de imagenes
print '-'*70
print 'Cargando interwikis de %s: hacia %s:' % (lenguajefuente, lenguajeobjetivo)
dbname=tarea000.getDbname(lenguajefuente, family)
server=tarea000.getServer(lenguajefuente, family)
conn = MySQLdb.connect(host='sql-s%s' % server, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("select ll_from, page_title, ll_title from langlinks inner join page on ll_from=page_id where ll_lang=\'%s\';" % lenguajeobjetivo)
row=cursor.fetchone()
c=0
while row:
	pageid=int(row[0])
	pagetitle=row[1]
	interwiki=re.sub('_', ' ', row[2])
	c+=1
	percent(c)
	if pagetitle2pageid.has_key(interwiki) and pagetitle2pageid[interwiki] in sinimagenes:
		#si la pagina a la que apunta el iw existe en el lenguajeobjetivo, y no tiene imagenes...
		interwikis[pageid]=interwiki
		pageid2pagetitle2[pageid]=pagetitle
			#pagetitle2pageid2[pagetitle]=pageid
	row=cursor.fetchone()
cursor.close()
conn.close()
print '\nCargados %d pageid/pagetitle (y su interwiki a %s:) de %swiki que tienen iw hacia articulos de %s: sin imagenes' % (c, lenguajeobjetivo, lenguajefuente, lenguajeobjetivo)

#cargamos imágenes subidas a la inglesa y que cumplan los filtros
print '-'*70
print 'Cargando imagenes locales de %s:' % lenguajefuente
images=set()
dbname=tarea000.getDbname(lenguajefuente, family)
server=tarea000.getServer(lenguajefuente, family)
conn = MySQLdb.connect(host='sql-s%s' % server, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("select img_name from image;") #no poner img_width<img_height, ya que hay que tenerlas para descartarlas
row=cursor.fetchone()
c=0
while row:
	image=re.sub('_', ' ', row[0])
	#filtro
	if re.search(exclusion_pattern, image):
		continue
	c+=1
	percent(c)
	images.add(image)
	#print image.encode('utf-8')
	row=cursor.fetchone()
cursor.close()
conn.close()
print '\nCargadas %d imagenes locales de %swiki (descartando iconos, escudos... )' % (c, lenguajefuente)

#cargamos las imagenes que se usan (y no estan subidas en la inglesa (están en Commons)) y en que articulos se usan
print '-'*70
print 'Cargamos imagenes que se usan en %s: y en que articulos' % lenguajefuente #pesado
candidatas={}
listanegra=set()
dbname=tarea000.getDbname(lenguajefuente, family)
server=tarea000.getServer(lenguajefuente, family)
conn = MySQLdb.connect(host='sql-s%s' % server, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("select il_from, il_to, page_namespace from imagelinks inner join page on il_from=page_id where (page_namespace=0 or page_namespace=10) and page_is_redirect=0;") #el nm 10 hace falta para descartar las imagenes de las plantillas stub, etc, y meterlas en listanegra
row=cursor.fetchone()
c=0
while row:
	pageid=int(row[0])
	image=re.sub('_', ' ', row[1])
	pagenamespace=int(row[2])
	
	if image in listanegra: #debe estar lo primero
		continue
	if pagenamespace==10:
		listanegra.add(image)
		continue
	#filtro
	if re.search(exclusion_pattern, image):
		continue
	#print image.encode('utf-8')
	if image in images: #comprobamos si esta subida a la inglesa
		listanegra.add(image)
		continue
	if not pageid2pagetitle2.has_key(pageid): #si no existe tal pagina en la inglesa, hace falta?
		continue
	if pagetitle2pageid[interwikis[pageid]] not in sinimagenes: #si ya tiene imagen no hace falta seguir
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
	row=cursor.fetchone()
cursor.close()
conn.close()
print '\nCargadas %d imagenes que se usan en articulos de %s: y nos pueden servir quizas (candidatas)' % (c, lenguajefuente)

#cargamos categorylinks de la inglesa que lleven a una categoria births o deaths, para cribar biografias
categories=set()
categories_pattern=re.compile(ur"\((?P<pageid>\d+)\,\'\d+ (births|deaths)\'\,\'[^\']*?\'\,\d+\)") #no hace falta (?i)
# (1031,'1950 births','Blabla, Antonio',20080805144158)
filename='/mnt/user-store/%swiki-latest-categorylinks.sql.gz' % lenguajefuente
f=""
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
		pageid=int(i.group("pageid"))
		c+=1
		percent(c)
		categories.add(pageid)
print '\nCargadas %d categorylinks desde biografias para %swiki' % (c, lenguajefuente)
f.close()

#cargamos imagenes subidas a commons y que cumplan los filtros
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
for pageid, imagenescandidatas in candidatas.items():
	if pageid not in categories: #no es biografia?
		continue
	article=pageid2pagetitle2[pageid]
	c+=1
	for image in imagenescandidatas:
		iw=interwikis[pageid]
		if re.search(exclusion_pattern, iw):#evitamos imagenes y articulos que no sirven o erroneas que ya se han comprobado en otras actualizacione
			continue
		trocear=' '.join([iw, article]) #para aquellos idiomas como ar: con alfabetos distintos incluimos el nombre en inglés también
		trozos=re.sub(ur'[\(\)]', ur'', trocear).split(' ')
		trozos2=[]
		for t in trozos:
			t=t.strip()
			if len(t)>=3:
				trozos2.append(t)
		temp="|".join(trozos2)
		
		if re.findall(ur'\|', temp)>=1: #al menos dos palabras para buscar (una|otra)
			if image not in listanegra:
				if image in imagescommons:
					if not re.search(exclusion_pattern, image): #evitamos imagenes que no sirven o erroneas que ya se han comprobado en otras actualizaciones
						if not re.search(ur'([\'\"]|[^\d]0\d\d[^\d])', ' '.join([iw, image])): #?
							if len(re.findall(ur"(?i)(%s)" % temp, image))>=2: #al menos dos ocurrencias en el nombre del fich
								cc+=1
								image_=re.sub(' ', '_', image)
								md5_=md5.new(image_.encode('utf-8')).hexdigest()
								
								salida='%s;%s;%s;\n' % (article, iw, image)
								salida=salida.encode('utf-8')
								
								salida2="INSERT INTO `imagesforbio` (`id`, `language`, `article`, `image`, `url`, `done`) VALUES (NULL, '%s', '%s', '%s', 'http://upload.wikimedia.org/wikipedia/commons/%s/%s/%s', 0);\n" % (lenguajeobjetivo, iw, image, md5_[0], md5_[0:2], image_)
								salida2=salida2.encode('utf-8')
								
								try:
									f.write(salida)
									g.write(salida2)
								except:
									pass
f.close()
g.close()

#print '\nFinalmente se encontraron %d articulos susceptibles de ser ilustrados con %d imagenes, en %s:' % (c, cc, lenguajeobjetivo)
print '\n---->(((((Finalmente se encontraron %d imagenes posiblemente utiles, en %s:)))))<----' % (cc, lenguajeobjetivo)

