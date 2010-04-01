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

import wikipedia,re,sys,os,gzip,time, datetime
import tarea000

def percent(c):
	if c % 1000 == 0:
		wikipedia.output(u'Llevamos %d' % c)

site=wikipedia.Site('es', 'wikipedia')

bots=tarea000.botList(site)
bots+=[u'BOTpolicia', u'AVBOT', u'CommonsDelinker', u'Eskimbot', u'EmxBot', u'YurikBot', u'H-Bot', u'Paulatz bot', u'TekBot', u'Alfiobot', u'RoboRex', u'Agtbot', u'Felixbot', u'Pixibot', u'Sz-iwbot', u'Timbot (Gutza)', u'Ginosbot', u'GrinBot', u'.anacondabot', u'Omdirigeringsrättaren', u'Rubinbot', u'HasharBot', u'NetBot', u"D'ohBot", u'Byrialbot', u'Broadbot', u'Guanabot', u'Chris G Bot 2', u'CCyeZBot', u'Soulbot', u'MSBOT', u'GnawnBot', u'Chris G Bot 3', u'Huzzlet the bot', u'JCbot', u'DodekBot', u'John Bot II', u'CyeZBot', u'Beefbot', u'Louperibot', u'SOTNBot', u'DirlBot', u'Obersachsebot', u'WikiDreamer Bot', u'YonaBot', u'Chlewbot', u'PixelBot', u'ToePeu.bot', u'HujiBot', u'Le Pied-bot', u'Ugur Basak Bot', u'NigelJBot', u'CommonsTicker', u'Tangobot', u'SeanBot', u'Corrector de redirecciones', u'HermesBot', u'Darkicebot', u'RedBot', u'HerculeBot', u'PatruBOT', u'RobotGMwikt', u'MonoBot', u'WikimediaNotifier', u'SBot39', u'DSisyphBot', u'GriffinBot1', u'WeggeBot', u'EhJBot3', u'Gerakibot', u'Picochip08', u'MondalorBot', u'Redirect fixer',]
admins=tarea000.adminList(site)
users={}
limite=7

os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select rc_user_text from recentchanges where (rc_namespace=0 or rc_namespace=104) and rc_type=0 and rc_bot=0 and rc_timestamp>=date_add(now(), interval -%d day);" > /home/emijrp/temporal/ultimasedicionesrc.txt' % limite)
f=open('/home/emijrp/temporal/ultimasedicionesrc.txt', 'r')
c=0
print 'Cargando ediciones de cambios recientes'
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==1:
		rc_user_text=trozos[0]
		
		if users.has_key(rc_user_text):
			users[rc_user_text]+=1
		else:
			users[rc_user_text]=1
		
		c+=1
		percent(c)
f.close()

users_list = [(v, k) for k, v in users.items()]
users_list.sort()
users_list.reverse()
users_list = [(k, v) for v, k in users_list]

c=0
multiplicador=10
s=u"{{/begin|%s|%s}}\n" % (limite, multiplicador)
for user, edits in users_list:
	if edits>=limite*multiplicador and bots.count(user)==0:
		c+=1
		#wikipedia.output(u'%d) %s - %d' % (c, user, edits))
		if admins.count(user):
			s+=u"|-\n| %s || [[User:%s|%s]] (Admin) || [[User talk:%s|Discusión]] || [[Special:Contributions/%s|%d]] \n" % (str(c),user,user,user,user,edits)
		else:
			s+=u"|-\n| %s || [[User:%s|%s]] || [[User talk:%s|Discusión]] || [[Special:Contributions/%s|%d]] \n" % (str(c),user,user,user,user,edits)

s+=u"{{/end}}"
page=wikipedia.Page(site, u'Wikipedia:Usuarios muy activos')
page.put(s, "BOT - Actualizando lista de usuarios muy activos [%d]" % c)

c=0
multiplicador=2
s=u"{{/begin|%s|%s}}\n" % (limite, multiplicador)
for user, edits in users_list:
	if edits>=limite*multiplicador and bots.count(user)==0:
		c+=1
		#wikipedia.output(u'%d) %s - %d' % (c, user, edits))
		if admins.count(user):
			s+=u"|-\n| %s || [[User:%s|%s]] (Admin) || [[User talk:%s|Discusión]] || [[Special:Contributions/%s|%d]] \n" % (str(c),user,user,user,user,edits)
		else:
			s+=u"|-\n| %s || [[User:%s|%s]] || [[User talk:%s|Discusión]] || [[Special:Contributions/%s|%d]] \n" % (str(c),user,user,user,user,edits)

s+=u"{{/end}}"
page=wikipedia.Page(site, u'Wikipedia:Usuarios activos')
page.put(s, "BOT - Actualizando lista de usuarios activos [%d]" % c)
