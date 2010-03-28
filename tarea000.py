#!/usr/bin/env python2.5
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

import wikipedia, re
import time
import MySQLdb

def latestDump(family, lang, date):
	return

def botList(site):
	bots=[]
	data=site.getUrl("/w/index.php?title=Special:Listusers&limit=5000&group=bot")
	data=data.split('<!-- start content -->')
	data=data[1].split('<!-- end content -->')[0]
	m=re.compile(ur' title="[^\:]+?:(?P<botname>.*?)">\g<botname>').finditer(data)
	for i in m:
		bots.append(i.group("botname"))
	
	#get global bots too
	data=wikipedia.Site('meta', 'meta').getUrl("/w/index.php?title=Special:GlobalUsers&limit=5000&group=Global_bot")
	data=data.split('<!-- start content -->')
	data=data[1].split('<!-- end content -->')[0]
	m=re.compile(ur'<li>(?P<botname>.*?) ‎(\(<a href|\(unattached)').finditer(data)
	for i in m:
		bots.append(i.group("botname"))
	
	print bots
	time.sleep(10)
	return bots

def insertBOTijoInfo(site):
	delay=10
	if botList(site).count(u"BOTijo")==0: #no tiene flag
		bot=wikipedia.Page(site, u"User:BOTijo")
		if not bot.exists():
			bot.put(u"{{/info}}", u"BOT - Creating bot userpage")
			time.sleep(delay)
		elif not re.search(ur"{{/info}}", bot.get()):
			bot.put(u"{{/info}}\n%s" % bot.get(), u"BOT - Adding info")
			time.sleep(delay)
		botinfo=wikipedia.Page(site, u"User:BOTijo/info")
		info=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u"User:Emijrp/BOTijoInfo.css").get()
		if not botinfo.exists() or botinfo.get()!=info:
			botinfo.put(info, u"BOT - Bot info page")
			time.sleep(delay)
		bottalk=bot.toggleTalkPage()
		if not bottalk.exists():
			bottalk.put(u"#REDIRECT [[User:BOTijo]]", u"BOT - Redirect")
			time.sleep(delay)
	else: #tiene flag
		bot=wikipedia.Page(site, u"User:BOTijo")
		if not bot.exists():
			bot.put(u"This is a bot account operated by [[w:es:User:Emijrp|emijrp]] from [[w:es:Mainpage|Spanish Wikipedia]].\n\n'''This [[w:en:Wikipedia:Bot policy|bot]] runs on the [[meta:Toolserver|Wikimedia Toolserver]].''' <br /><small>''Administrators: If this bot needs to be blocked due to a malfunction, please remember to disable autoblocks so that other Toolserver bots are not affected.''", u"BOT - Creating bot userpage")
			time.sleep(delay)
		else:
			bot.put(re.sub(ur"(?i)\{\{\s*/info\s*\}\}", ur"", bot.get()), u"BOT - Flag granted")
			time.sleep(delay)
		bottalk=bot.toggleTalkPage()
		if not bottalk.exists():
			bottalk.put(u"#REDIRECT [[User:BOTijo]]", u"BOT - Redirect")
			time.sleep(delay)

def getLangsByFamily(family):
	conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
	cursor = conn.cursor()
	cursor.execute("SELECT lang from wiki where family='%s' and is_closed=0;" % family)
	result=cursor.fetchall()
	langs=[]
	for row in result:
		if len(row)==1:
			langs.append(row[0])		

	cursor.close()
	conn.close()
	return langs

def getNamespaceName(lang, family, nsnumber):
	conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
	cursor = conn.cursor()
	cursor.execute("SELECT ns_name from namespace where domain='%s.%s.org' and ns_id=%s;" % (lang, family, nsnumber))
	result=cursor.fetchall()
	nsname=""
	for row in result:
		if len(row)==1:
			nsname=unicode(row[0], "utf-8")

	cursor.close()
	conn.close()
	return nsname

