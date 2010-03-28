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
import sets
import MySQLdb

def percent(c):
	if c % 100000 == 0:
		wikipedia.output(u'Llevamos %d' % c)

lang="es"
if len(sys.argv)>1:
	lang=sys.argv[1]

limit=500
if len(sys.argv)>=3:
	limit=int(sys.argv[2])

site=wikipedia.Site(lang, 'wikipedia')


conn = MySQLdb.connect(host='sql-s3', db='%swiki_p' % lang, read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
minimo=25
cursor.execute("SELECT user_name from user where user_editcount>%s;" % minimo)
result=cursor.fetchall()
nicks=sets.Set()
for row in result:
	if len(row)==1:
		nicks.add(unicode(row[0], "utf-8"))
wikipedia.output(u"%s usuarios con mas de %s ediciones " % (len(nicks), minimo))

cursor.close()
conn.close()

days={}
c=0
f=bz2.BZ2File("/mnt/user-store/dump/%swiki-fetched.txt.bz" % lang, "r")
for l in f.xreadlines():
	c+=1
	percent(c)
	l=unicode(l, "utf-8").strip()
	t=l.strip().split("	")
	if len(t)>5:
		nick=t[4]
		if nick in nicks:
			date=t[3]
			day=date[:10]
			if days.has_key(day):
				if nick not in days[day]:
					days[day].add(nick)
					#print len(days[day]), day
			else:
				days[day]=sets.Set()
				days[day].add(nick)

f.close()

print '%d nicks distintos' % len(nicks)

#ordenamos los dias
dayslist=[]
for k, v in days.items():
	dayslist.append(k)
dayslist.sort()

records={}
c=0
for nick in nicks:
	c+=1
	if c % 1000 == 0:
		print c, "de", len(nicks)	
	acumulado=0
	continuo=False
	origen=''
	final=''
	for day in dayslist:
		if nick in days[day]: #editó ese dia
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
					records[nick]={'origen':origen,'final':final,'acumulado':acumulado}
			else:
				records[nick]={'origen':origen,'final':final,'acumulado':acumulado}
			acumulado=0 #reseteamos

recordslist=[]
for k, v in records.items():
	recordslist.append([v['acumulado'], k, v['origen'], v['final']])

recordslist.sort()
recordslist.reverse()

salida=u'{{/begin|%s}}\n' % limit
c=0
for i in recordslist:
	c+=1
	dias=i[0]
	nick=i[1]
	inicio=i[2]
	fin=i[3]
	
	if c<=10:
		print i
	if c>limit or dias<30:
		break
	
	salida+=u'|-\n| %d || [[User:%s|%s]] || %s || %s || %s \n' % (c, nick, nick, inicio, fin, dias)
salida+=u'{{/end}}'

wiii=wikipedia.Page(site, u'Wikipedia:Usuarios que han editado más días ininterrumpidamente')
wiii.put(salida, u'BOT - Updating ranking')


