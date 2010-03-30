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

import re
import gzip
import sys
import wikipedia
import time, os
import bz2
import tarea000

# Este script necesita un dump pre-procesado con stubmetahistory-fetch-celementtree.py. Este código está en el repositorio también

#fix: el page_id de algunos artículos sale 'None', está mal el dump o mi parseador?

def percent(c):
	if c % 100000 == 0:
		wikipedia.output(u'Llevamos %d' % c)

lang='es' #idioma que será analizado
if len(sys.argv)>=2:
	lang=sys.argv[1]

site=wikipedia.Site(lang, 'wikipedia')

traslation={
'page_title': {
	'en': u'User:Emijrp/List of pages by edit count',
	'es': u'Wikipedia:Artículos más editados',
	},
}

data=site.getUrl("/w/index.php?title=Special:RecentChanges&limit=0")
data=data.split('<select id="namespace" name="namespace" class="namespaceselector">')[1].split('</select>')[0]
namespaces=re.findall(ur'<option value="[1-9]\d*">(.*?)</option>', data)
no_pattern = re.compile(ur'(%s)\:' % '|'.join(namespaces))

bots=[]
data=site.getUrl("/w/index.php?title=Special:Listusers&limit=5000&group=bot")
data=data.split('<!-- start content -->')
data=data[1].split('<!-- end content -->')[0]
m=re.compile(ur' title=".*?:(?P<botname>.*?)">').finditer(data)
for i in m:
	bots.append(i.group("botname"))


f=bz2.BZ2File("/mnt/user-store/dump/%swiki-fetched.txt.bz" % lang, "r")
anyos={'Total':{}}
c=0
for l in f.xreadlines():
	c+=1
	percent(c)
	l=unicode(l, "utf-8")
	t=l.strip().split("	")
	if len(t)>9:
		[page_title, page_id, rev_id, rev_timestamp, rev_author, rev_comment, md5_, rev_len, rev_type]=t[0:9]
	else:
		continue
	try:
		page_id=int(page_id)
	except:
		print t
		#sys.exit()
	if not re.search(no_pattern, page_title):
		year=rev_timestamp[0:4]
		if anyos.has_key(year):
			if anyos[year].has_key(page_id):
				anyos[year][page_id]+=1
				anyos['Total'][page_id]+=1
			else:
				anyos[year][page_id]=1
				anyos['Total'][page_id]=1
		else:
			anyos[year]={page_id:1}
			anyos['Total'][page_id]=1
f.close()

wtitle="User:Emijrp/List of pages by edit count"
if traslation['page_title'].has_key(lang):
	wtitle=traslation['page_title'][lang]

limitsub=300 #límite de páginas a mostrar
limitmain=30
salidasmain=[]
for year, d in anyos.items():
	l=[]
	for page_title, edits in d.items():
		#if edits>1: #quitamos peso a la lista
		l.append([edits, page_title])
	l.sort()
	l.reverse()
	salidamain=u"== %s ==\n{{AP|Wikipedia:Artículos más editados/%s}}\n{| width=100%% style=\"background-color: transparent;\" " % (year, year)
	salidasub=u"{{../begin2|%s}}\n== %s ==\n{| width=100%% style=\"background-color: transparent;\" " % (year, year)
	cc=0
	for edits, article in l:
		if cc>=limitsub:
			break
		if cc<limitmain and cc % (limitmain/3) == 0:
			salidamain+=u"\n| valign=top width=33% | "
		if cc<limitsub and cc % (limitsub/3)==0:
			salidasub+=u"\n| valign=top width=33% | "
		if cc<limitmain:
			salidamain+=u"\n* [[%s]] (%s)" % (article, edits)
		if cc<limitsub:
			salidasub+=u"\n* [[%s]] (%s)" % (article, edits)
		cc+=1
	salidasub+=u"\n|}\n{{../end2}}"
	salidamain+=u"\n|}"
	salidasmain.append([year, salidamain])
	wikipedia.output(salidamain)
	wiii=wikipedia.Page(site, u"%s/%s" % (wtitle, year))
	msg=u""
	if bots.count("BOTijo")==0:
		msg+=u"(This bot only edits user subpages. If flag if needed for this, please, send a message to [[:es:User talk:Emijrp]].)"	
	wiii.put(salidasub, u'BOT - Updating ranking %s' % msg)
salidasmain.sort()
salidasmain.reverse()
print len(salidasmain)
salidasmain2=[]
for year, salida in salidasmain:
	salidasmain2.append(salida)
salidamain=u"{{/begin}}\n%s\n{{/end}}" % ("\n\n".join(salidasmain2))

wiii=wikipedia.Page(site, wtitle)
msg=u""
if bots.count("BOTijo")==0:
	msg+=u"(This bot only edits user subpages. If flag if needed for this, please, send a message to [[:es:User talk:Emijrp]].)"
wiii.put(salidamain, u'BOT - Updating ranking %s' % msg)

tarea000.insertBOTijoInfo(site)

