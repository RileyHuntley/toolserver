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

#falta distinguir entre redirecciones y articulos (sql del toolserver?)

import gzip
import re
import sys
import time
import wikipedia

import tareas

lang='es'
if len(sys.argv)>1:
	lang=sys.argv[1]

site=wikipedia.Site(lang, 'wikipedia')

bots=tareas.getBotsDic(site)
admins=tareas.getAdminsDic(site)
namespacesreg=tareas.getNamespacesList(site)
namespacesreg='|'.join(namespacesreg)
namespacesreg=ur'(%s)' % namespacesreg
namespacesreg=re.compile(namespacesreg)

path='/mnt/user-store/stub-meta-history/fetch/'
filename = 'fetch-%swiki-latest-stub-meta-history.txt.gz' % (lang)
filename2 = ''
if len(sys.argv)>2:
	filename2 = sys.argv[2]
if filename2:
	f = gzip.open(filename2, 'r')
else:
	f = gzip.open('%s%s' % (path, filename), 'r')

timestamps={}
r_line=re.compile(ur'(.*?);;;(.*?);;;(.*?);;;(.*?);;;(.*?);;;(.*?);;;')
c=0
cc=0.0
ipregexp=re.compile(r'(?im)^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
revtoanonreg=re.compile(r'(?i)((posible|vandalismo|prueba|blanqueo|revertidos los cambios|deshecha la edición \d+|rev\. edición|rv\. edic\.) *[^\[]*? *(de|por) *\[\[(user\:|usuario\:|special\:contributions\/|especial\:contribuciones\/)\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
for l in f:
	c+=1
	if c==1:
		continue
	if c % 100000 == 0:
		print '%d lineas leidas (%d analizadas, %.2f%s)' % (c, cc, cc/(c/100), '%')
		#break
	
	l=unicode(l, 'utf-8')
	
	#t=re.findall(r_line, l)
	t=[l.split(';;;')]
	if t:
		cc+=1
		pagetitle=t[0][0]
		
		if re.search(namespacesreg, pagetitle):
			continue
		
		pageid=t[0][1]
		revisionid=t[0][2]
		timestamp=t[0][3]
		year=timestamp[:4]
		month=timestamp[5:7]
		day=timestamp[8:10]
		author=t[0][4]
		comment=t[0][5]
		
		timestamp2=year+'-'+month+'-'+day
		userclass='reg'
		
		if re.search(ipregexp, author):
			userclass='anon'
		elif admins.has_key(author):
			userclass='admin'
		elif bots.has_key(author):
			userclass='bot' 
		
		if not timestamps.has_key(timestamp2):
			timestamps[timestamp2]={
			'admin':{'edits':0,'users':{}},
			'bot':{'edits':0,'users':{}},
			'reg':{'edits':0,'users':{}},
			'anon':{'edits':0,'users':{}},
			'all':{'edits':0,'users':{}},
			'revtoanon':{'edits':0},
			}
		
		timestamps[timestamp2][userclass]['edits']+=1
		timestamps[timestamp2]['all']['edits']+=1
		
		#reversion a anonimo?
		if re.search(revtoanonreg, comment):
			timestamps[timestamp2]['revtoanon']['edits']+=1
		
		"""
		#control de actividad de bots para saber quien produce los picos
		if userclass=='bot':
			if timestamps[timestamp2][userclass]['users'].has_key(author):
				timestamps[timestamp2][userclass]['users'][author]+=1
				timestamps[timestamp2]['all']['users'][author]+=1
			else:
				timestamps[timestamp2][userclass]['users'][author]=1
				timestamps[timestamp2]['all']['users'][author]=1
		"""
		
f.close()

timestampslist=[]
for timestamp, dic in timestamps.items():
	timestampslist.append([timestamp, dic])

timestampslist.sort()

g=open('editsperuserclass-%s.txt' % lang, 'w')
g.write('timestamp;admin;bot;reg;anon;all;revtoanon;\n')
antes=0
salida=u''
maxs=[]
total=admin=bot=reg=anon=revtoanon=0.0
for timestamp, userclasses in timestampslist:
	maxs.append([userclasses['all']['edits'], timestamp]) #metemos todos los dias, y lluego escojemos los X con mas ediciones
	total+=userclasses['all']['edits']
	admin+=userclasses['admin']['edits']
	bot+=userclasses['bot']['edits']
	reg+=userclasses['reg']['edits']
	anon+=userclasses['anon']['edits']
	revtoanon+=userclasses['revtoanon']['edits']
	#g.write('%s;%s;%s;%s;%s;%s;\n' % (timestamp, userclasses['admin']['edits'], userclasses['bot']['edits'], userclasses['reg']['edits'], userclasses['anon']['edits'], userclasses['all']['edits']))
	g.write('%s;%s;%s;%s;%s;%s;%s;\n' % (timestamp, userclasses['admin']['edits'], userclasses['bot']['edits'], userclasses['reg']['edits'], userclasses['anon']['edits'], userclasses['all']['edits'], userclasses['revtoanon']['edits']))
g.write('Total=%d;Admin=%d (%f%%);Bot=%d (%f%%);Reg=%d (%f%%);Anon=%d (%f%%);Revtoanon=%d;' % (total, admin, admin/(total/100), bot, bot/(total/100), reg, reg/(total/100), anon, anon/(total/100), revtoanon))
g.close()

"""
maxs.sort()
maxs.reverse()

c=0
for max, timestamp in maxs:
	if c<10:
		c+=1
		templist=[]
		for user, useredits in timestamps[timestamp]['all']['users'].items():
			templist.append([useredits, user])
		templist.sort()
		templist.reverse()
		salida+=u'\n\n== %s (%d) ==' % (timestamp, timestamps[timestamp]['all']['edits'])
		trozos=timestamp.split('-')
		year=trozos[0]
		month=trozos[1]
		day=trozos[2]
		cc=0
		for useredits, user in templist:
			user_=re.sub(' ','_',user)
			if cc<=3:
				salida+=u'\n# [[User:%s]] ([http://%s.wikipedia.org/w/index.php?limit=50&title=Special:Contributions&contribs=user&target=%s&namespace=0&offset=%s%s%s235959 %d])' % (user, lang, user_, year, month, day, useredits)
			cc+=1
h=open('editsperuserclass-%s-explanation.txt' % lang, 'w')
h.write(salida.encode('utf-8'))
h.close()
"""

"""
wikipedia.output(salida)

wiii=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'User:Emijrp/Zona de pruebas/2')
wiii.put(salida, u'BOT')
"""
