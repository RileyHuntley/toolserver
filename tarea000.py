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

def latestDump(family, lang, date):
	return

def botList(site):
	bots=[]
	data=site.getUrl("/w/index.php?title=Special:Listusers&limit=5000&group=bot")
	data=data.split('<!-- start content -->')
	data=data[1].split('<!-- end content -->')[0]
	m=re.compile(ur' title=".*?:(?P<botname>.*?)">').finditer(data)
	for i in m:
		bots.append(i.group("botname"))
	return bots

def insertBOTijoInfo(site):
	if botList(site).count(u"BOTijo")==0:
		bot=wikipedia.Page(site, u"User:BOTijo")
		if not bot.exists():
			bot.put(u"{{/info}}", u"BOT - Creating bot userpage")
		elif not re.search(ur"{{/info}}", bot.get()):
			bot.put(u"{{/info}}\n%s" % bot.get(), u"BOT - Adding info")
		botinfo=wikipedia.Page(site, u"User:BOTijo/info")
		info=u"""<center>
{| class="wikitable" width=600px
| This is a '''bot account''' operated by [[w:es:User:Emijrp|emijrp]] from [[w:es:Mainpage|Spanish Wikipedia]]. It updates some global rankings, like:
* [[User:Emijrp/List of Wikipedians by number of edits]]
* [[User:Emijrp/List of Wikipedians by page count]]
This bot edits at a '''very low rate''' (only a few edits per day), and '''only user subpages'''. If a flag is required for this, I will request it. Please, [[:es:User talk:Emijrp|notice me]], thanks : ). ([http://toolserver.org/~vvv/sulutil.php?user=BOTijo Flag was granted in largest Wikipedias]).
|-
| '''This [[w:en:Wikipedia:Bot policy|bot]] runs on the [[meta:Toolserver|Wikimedia Toolserver]].''' <br /><small>''Administrators: If this bot needs to be blocked due to a malfunction, please remember to disable autoblocks so that other Toolserver bots are not affected.''
|}
</center>"""
		if not botinfo.exists() or botinfo.get()!=info:
			botinfo.put(info, u"BOT - Bot info page")
		bottalk=bot.toggleTalkPage()
		if not bottalk.exists():
			bottalk.put(u"#REDIRECT [[User:BOTijo]]", u"BOT - Redirect")

