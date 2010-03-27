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

import bz2, wikipedia, re, sys

def percent(c):
	if c % 100000 == 0:
		wikipedia.output(u'Llevamos %d' % c)

lang="es"
if len(sys.argv)>1:
	lang=sys.argv[1]

limit=100
if len(sys.argv)>=3:
	limit=int(sys.argv[2])

site=wikipedia.Site(lang, 'wikipedia')

days={}
nicks={}
c=0
f=bz2.BZ2File("/mnt/user-store/dump/%swiki-fetched.txt.bz" % lang, "r")
for l in f.xreadlines():
	c+=1
	percent(c)
	l=unicode(l, "utf-8").strip()
	t=l.strip().split("	")
	if len(t)>5:
		nick=t[3]
		if nicks.has_key(nick):
			nicks[nick]+=1
		else:
			nicks[nick]=1
		date=t[4]
		day=date[:8]
		if days.has_key(day):
			if days[day].count(nick)==0:
				days[day].append(nick)
		else:
			days[day]=[nick]
f.close()

print '%d nicks distintos' % len(nicks.items())

#ordenamos los dias
dayslist=[]
for k, v in days.items():
	dayslist.append(k)
dayslist.sort()

records={}
for nick, edits in nicks.items():
	if edits<50: #quitar?
		continue
	acumulado=0
	continuo=False
	origen=''
	final=''
	for day in dayslist:
		if days[day].has_key(nick): #editó ese dia
			if not continuo:
				continuo=True
				origen=day
			acumulado+=1
		else:
			#guardamos si es record
			continuo=False
			final=day
			
			if records.has_key(nick):
				if records[nick]['acumulado']<acumulado:
					records[nick]={'origen':origen,'final':final,'acumulado':acumulado,'ediciones':edits}
					#linea= '%s - %d dias seguidos - inicio: %s - fin: %s' % (nick, acumulado, origen, final)
					#if acumulado>3:
					#	print linea.encode('utf-8')
			else:
				records[nick]={'origen':origen,'final':final,'acumulado':acumulado,'ediciones':edits}
			acumulado=0 #reseteamos

recordslist=[]
for k, v in records.items():
	recordslist.append([v['acumulado'], k, v['origen'], v['final'], v['ediciones']])

recordslist.sort()
recordslist.reverse()

c=0
for i in recordslist:
	c+=1
	if c<=10:
		print i
	else:
		break

salida=u'{{begin/%s}}\n' % limit
c=0
for i in recordslist:
	c+=1
	if c<=10:
		print i
	
	dias=i[0]
	nick=i[1]
	inicio=i[2]
	inicio='%s-%s-%s' % (inicio[:4], inicio[4:6], inicio[6:])
	fin=i[3]
	fin='%s-%s-%s' % (fin[:4], fin[4:6], fin[6:])
	salida+=u'|-\n| %d || [[User:%s|%s]] || %s || %s || %s \n' % (c, nick, nick, inicio, fin, dias)
salida+=u'{{/end}}'

wiii=wikipedia.Page(site, u'Wikipedia:Usuarios que han editado más días ininterrumpidamente')
wiii.put(salida, u'BOT - Updating ranking')


