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
import datetime

def percent(c):
    if c % 1000 == 0:
        wikipedia.output(u'Llevamos %d' % c)

limit=14
conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT rc_timestamp from recentchanges where rc_user_text='AVBOT' and rc_namespace=0 and rc_deleted=0 and rc_timestamp>=date_add(now(), interval -%d day);" % limit)
result=cursor.fetchall()
days={}
c=0
for row in result:
    if len(row)==1:
        rc_timestamp=row[0][:8]
        if days.has_key(rc_timestamp):
            days[rc_timestamp]+=1
        else:
            days[rc_timestamp]=1
    c+=1
    percent(c)

l=[]
for day, edits in days.items():
    l.append([day, edits])
l.sort()
l.reverse()

site=wikipedia.Site('es', 'wikipedia')

weekday={0:u'lunes', 1:u'martes', 2:u'miércoles', 3:u'jueves', 4:u'viernes', 5:u'sábado', 6:u'domingo'}
monthname={1:u'enero', 2:u'febrero', 3:u'marzo', 4:u'abril', 5:u'mayo', 6:u'junio', 7:u'julio', 8:u'agosto', 9:u'septiembre', 10:u'octubre', 11:u'noviembre', 12:u'diciembre'}

output=u"{| class='wikitable sortable' align='right' style='text-align: center' \n! Día !! Ediciones "
for day, edits in l:
    date=datetime.datetime(year=int(day[0:4]), month=int(day[4:6]), day=int(day[6:8]))
    output+=u"\n|-\n| %s, [[%d de %s]] || %d " % (weekday[date.weekday()], date.day, monthname[date.month], edits)
output+=u"\n|-\n| colspan=2 | <small>''Esta tabla recoge la actividad de AVBOT<br/>en los últimos días''</small>\n|}"

wii=wikipedia.Page(site, u"User:AVBOT/Últimos días")
wii.put(output, u"BOT - Actualizando plantilla")
