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

import wikipedia,re,sys,os,gzip,time
import MySQLdb
import math

def percent(c):
	if c % 1000 == 0:
		wikipedia.output(u'Llevamos %d' % c)

def distancia(punto1, punto2):
	#1º = 111 km
	conv=111.0
	punto3={'lat':punto1['lat'],'lon':punto2['lon']}
	punto4={'lat':punto2['lat'],'lon':punto1['lon']}

	a=0
	b=0
	if punto1['lon']>punto3['lon']:
		a=(punto1['lon']-punto3['lon'])*conv
	else:
		a=(punto3['lon']-punto1['lon'])*conv

	if punto1['lat']>punto4['lat']:
		b=(punto1['lat']-punto4['lat'])*conv
	else:
		b=(punto4['lat']-punto1['lat'])*conv

	if a!=0 and b!=0:
		return math.sqrt(a**2+b**2)
	else:
		return 999999
	

lang="es"
if len(sys.argv)>1:
	lang=sys.argv[1]


objs={}

site=wikipedia.Site("es", "wikipedia")
objspage=wikipedia.Page(site, u"User:Emijrp/Imágenes requeridas por zona/Objetivos conocidos")
l=[]
for line in objspage.get().splitlines():
	l.append(line)	
	t=line.strip().split(";")
	if len(t)==3:
		objname=t[0].strip()
		objlat=float(t[1].strip())
		objlon=float(t[2].strip())
		objs[objname]={'lat': objlat, 'lon': objlon}
l.sort()
objspage.put("\n".join(l), u"BOT - Ordenando alfabéticamente")
print objs

candidatos={}
#page_id, page_title, page_length
conn = MySQLdb.connect(host='sql-s3', db='%swiki_p' % lang, read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT distinct page_title, gc_lat, gc_lon from u_dispenser_p.coord_eswiki join page on page_id=gc_from where page_namespace=0 and gc_from not in (select distinct il_from from imagelinks);")
result=cursor.fetchall()
limit=25 #km
nodupes=[]
for row in result:
	if len(row)==3:
		page_title=re.sub('_', ' ', unicode(row[0], "utf-8"))
		if nodupes.count(page_title)==0:
			nodupes.append(page_title)
		else:
			continue
		gc_lat=float(row[1])
		gc_lon=float(row[2])
		
		min=999999
		objeleg=""
		for obj, coord in objs.items():
			d=distancia(coord, {'lat': gc_lat, 'lon': gc_lon})
			if d<min:
				min=d
				objeleg=obj

		if min<limit:
			print page_title, "esta cerca de", objeleg
			l=u"| [[%s]] || %.2f || {{Coord|%s|%s}} " % (page_title, min, gc_lat, gc_lon)
			if candidatos.has_key(objeleg):
				candidatos[objeleg].append(l)
			else:
				candidatos[objeleg]=[l]
		else:
			pass
			#print "Demasiado lejos de cualquier objetivo conocido", page_title

cursor.close()
conn.close()

output=u"{{/begin|%s}}" % limit
c=0
candidatos_l=[]
for zona, l in candidatos.items():
	candidatos_l.append([zona, l])
candidatos_l.sort()

for zona, l in candidatos_l:
	l.sort()
	output+=u"\n\n== [[%s]] ==\n<center>\n{| class='wikitable sortable' style='text-align: center;' \n! Artículo !! Distancia (km) !! Coordenadas \n|-\n%s \n|}\n</center>" % (zona, "\n|-\n".join(l))
	c+=len(l)

output+=u"{{/end}}"
outputpage=wikipedia.Page(site, u"User:Emijrp/Imágenes requeridas por zona")
outputpage.put(output, u"BOT - Actualizando, se necesitan %s imágenes" % c)


