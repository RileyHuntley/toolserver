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

import datetime, time
import os, re, wikipedia, sys
import tarea000
import MySQLdb

delay=5
minimumedits=100 #edits to appear in the ranking
minimumusers=10 #para evitar listas de 2 personas
table_header=u"{| class='wikitable sortable' style='text-align:center;'\n! #\n! User\n! Edits\n"
table_footer=u"|}"
begin=u"''Please, translate this into your language and delete the english text'': This table shows '''first {{{1}}} users with more edits''' in this Wikipedia. Bots are not included.\n\n''If you want to change page title, contact to [[:es:User talk:Emijrp]]. Thanks.''\n\n<center>\n%s" % table_header
begin2=u"''Please, translate this into your language and delete the english text'': This table shows '''first {{{1}}} users with more edits''' in this Wikipedia. Bots are included.\n\n''If you want to change page title, contact to [[:es:User talk:Emijrp]]. Thanks.''\n\n<center>\n%s" % table_header
end=u"%s\n</center>\n\n''Please, put here a category similar to <nowiki>[[Category:Wikipedia statistics]]</nowiki>.''" % table_footer

"""\n\n[[cs:Wikipedie:Nejaktivnější wikipedisté]]\n[[de:Wikipedia:Beitragszahlen]]\n[[es:Wikipedia:Lista de wikipedistas por número de ediciones]]\n[[fr:Wikipédia:Liste des Wikipédiens par nombre d'éditions]]\n[[zh-classical:維基大典:編輯次數]]\n[[id:Wikipedia:Daftar pengguna menurut jumlah suntingan]]\n[[is:Wikipedia:Notendur eftir breytingafjölda]]\n[[he:ויקיפדיה:נתונים סטטיסטיים/משתמשים/1-100]]\n[[jv:Wikipedia:Daftar panganggo miturut cacahé suntingan]]\n[[ka:ვიკიპედია:ვიკიპედიელები აქტიურობის მიხედვით]]\n[[lt:Vikipedija:Naudotojai pagal keitimų skaičių]]\n[[hu:Wikipédia:Szerkesztők listája szerkesztésszám szerint]]\n[[ja:Wikipedia:編集回数の多いウィキペディアンの一覧]]\n[[pl:Wikipedia:Najaktywniejsi wikipedyści]]\n[[pt:Wikipedia:Lista de wikipedistas por número de edições]]\n[[sq:Wikipedia:Lista e Wikipedianëve sipas redaktimeve]]\n[[uk:Вікіпедія:Найактивніші]]\n[[bat-smg:Vikipedėjė:Nauduotuojē palē keitėmu skaitliu]]\n[[zh:Wikipedia:最多贡献的用户]]"
"""

end2=end

noflagrequired=[
	['ca', 'wikipedia'],
]

tras1={
'wikipedia': {
	u"default": u"User:Emijrp/List of Wikipedians by number of edits",
	u"ar": u"قائمة الويكيبيديين حسب عدد التعديلات",
	u"arz": u"List of Wikipedians by number of edits",
	u"ca": u"Llista de viquipedistes per nombre d'edicions",
	u"da": u"Wikipedianere efter antal redigeringer",
	u"eo": u"Listo de uzantoj laŭ redaktonombro",
	u"es": u"Ranking de ediciones", 
	u"fa": u"فهرست کاربران ویکی‌پدیا بر اساس تعداد ویرایش‌ها",
	u"fi": u"Luettelo Wikipedian käyttäjistä muokkausmäärän mukaan",
	u"fr": u"Utilisateurs par nombre d'éditions", 
	u"gl": u"Estatísticas/Lista de usuarios por número de edicións",
	u"hr": u"Popis Wikipedista po broju uređivanja",
	u"ht": u"Lis Wikipedyen pa nonm edisyon yo fè",
	u"hu": u"Wikipédisták listája szerkesztésszám szerint",
	u"ko": u"편집횟수 순 사용자 목록",
	u"pl": u"Użytkownicy według liczby edycji",
	u"ro": u"Lista wikipediştilor după numărul de editări",
	u"simple": u"List of Wikipedians by number of changes",
	u"sl": u"Seznam Wikipedistov po številu urejanj",
	u"sv": u"Lista över Wikipedia-användare sorterad efter antalet redigeringar",
	u"th": u"รายชื่อชาววิกิพีเดียที่แก้ไขมากที่สุด 500 อันดับ",
	u"tr": u"Değişiklik sayılarına göre Vikipedistler listesi",
	u"vi": u"Danh sách thành viên Wikipedia theo số lần sửa trang",
	},
'wiktionary': {
	u"es": u"Ranking de ediciones", 	
	u"simple": u"List of Wiktionarians by number of changes",
	},
'wikinews': {
	u"es": u"Ranking de ediciones", 
	},
}

tras2={
'wikipedia': {
	u"default": u"User:Emijrp/List of Wikipedians by number of edits (bots included)",
	u"ar": u"قائمة الويكيبيديين حسب عدد التعديلات (متضمنة البوتات)",
	u"arz": u"List of Wikipedians by number of edits (bots included)",
	u"ca": u"Llista de viquipedistes per nombre d'edicions (bots inclosos)",
	u"da": u"Wikipedianere efter antal redigeringer (bots inkluderet)",
	u"eo": u"Listo de uzantoj laŭ redaktonombro (inkluzivante robotojn)",
	u"es": u"Ranking de ediciones (incluye bots)", 
	u"fr": u"Utilisateurs par nombre d'éditions (bots inclus)", 
	u"gl": u"Estatísticas/Lista de usuarios por número de edicións (bots incluídos)",
	u"hr": u"Popis Wikipedista po broju uređivanja (botovi uključeni)",
	u"hu": u"Wikipédisták listája szerkesztésszám szerint (botokkal)",
	u"ko": u"편집횟수 순 사용자 목록 (봇 포함)",
	u"pl": u"Użytkownicy według liczby edycji (w tym boty)",
	u"ro": u"Lista wikipediştilor după numărul de editări (inclusiv roboţi)",
	u"simple": u"List of Wikipedians by number of changes (bots included)",
	u"sl": u"Seznam Wikipedistov po številu urejanj (z boti)",
	u"sv": u"Lista över Wikipedia-användare sorterad efter antalet redigeringar (inklusive robotar)",
	u"th": u"รายชื่อชาววิกิพีเดียที่แก้ไขมากที่สุด 500 อันดับ (รวมบอต)",
	u"tr": u"Değişiklik sayılarına göre Vikipedistler listesi (botlar dahil)",
	u"vi": u"Danh sách thành viên Wikipedia theo số lần sửa trang (tính cả bot)",
	},
'wiktionary': {
	u"es": u"Ranking de ediciones (incluye bots)", 
	},
'wikinews': {
	u"es": u"Ranking de ediciones (incluye bots)", 
	},
}

#do not want: nl, simple 
# fix: hr
tt100={'rankingusers':True, 'rankingbots':True, 'limit':100}
tt500={'rankingusers':True, 'rankingbots':True, 'limit':500}
projects={
	'wikinews': {
		'es': tt100,
		},
	'wikipedia': {
		'ar': tt500,
		'arz': tt100,
		'ca': tt500,
		'da': tt500,
		'eo': tt500,
		'es': tt500,
		'gl': tt100,
		'hr': tt500,
		'ht': tt100,
		'ro': tt500,
		'simple': tt500,
		'sl': tt100,
		'th': tt500,
		'tr': tt500,
		'vi': tt500,
		},
	'wiktionary': {
		'es': tt100,
		'simple': {'rankingusers':True, 'rankingbots':False, 'limit':100},
		},
}

"""
	'wikinews': {
		'es': tt100,
		},
	'wikipedia': {
		'ar': tt500,
		'ca': tt500,
		'da': tt500,
		'eo': tt500,
		'es': tt500,
		'gl': tt100,
		'hr': tt500,
		'ht': tt100,
		'ro': tt500,
		'simple': tt500,
		'sl': tt100,
		'th': tt500,
		'tr': tt500,
		'vi': tt500,
		},
	'wiktionary': {
		'es': tt100,
		'simple': {'rankingusers':True, 'rankingbots':False, 'limit':100},
		},

"""

"""'wikipedia': {
		'es': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'eo': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'hu': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'ca': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'tr': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'ro': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'vo': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'fi': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'it': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'nl': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'ru': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'sv': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'no': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'da': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'ar': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'ko': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'sr': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'sl': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'vi': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'bg': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'et': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'ht': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'fa': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'hr': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'new': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'nn': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'te': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'gl': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'th': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'simple': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		'he': {'rankingusers':True, 'rankingbots':True, 'limit':500},
		},"""

#metemos el resto de idiomas
for lang in tarea000.getLangsByFamily('wikipedia'):
	if lang=='en-simple':
		lang='simple'
	if not projects['wikipedia'].has_key(lang):
		projects['wikipedia'][lang]=tt100

#generating interwikis
iws1={}
iws2={}
for family, langs in projects.items():
	iws1[family]=[]
	iws2[family]=[]
	for lang, v in langs.items():
		if tarea000.isExcluded('tarea008', family, lang):
			continue
		wikipedianm=tarea000.getNamespaceName(lang, family, 4)
		if projects[family][lang]['rankingusers']:
			traslation1=""
			if tras1[family].has_key(lang):
				traslation1=u"%s:%s" % (wikipedianm, tras1[family][lang])
			else:
				traslation1=tras1[family]['default']
			iws1[family].append(u"[[%s:%s]]" % (lang, traslation1))
		if projects[family][lang]['rankingbots']:
			traslation2=""
			if tras2[family].has_key(lang):
				traslation2=u"%s:%s" % (wikipedianm, tras2[family][lang])
			else:
				traslation2=tras2[family]['default']
			iws2[family].append(u"[[%s:%s]]" % (lang, traslation2))
	iws1[family].sort()
	iws2[family].sort()

for family, langs in projects.items():
	for lang, v in langs:
		print family, lang
		if tarea000.isExcluded('tarea008', family, lang):
			continue
		
		title=u''
		#la lista de bots debe ir dentro del bucle, ya que se llena con más bots de cada caso
		bots=[u'BOTpolicia', u'AVBOT', u'CommonsDelinker', u'Eskimbot', u'EmxBot', u'YurikBot', u'H-Bot', u'Paulatz bot', u'TekBot', u'Alfiobot', u'RoboRex', u'Agtbot', u'Felixbot', u'Pixibot', u'Sz-iwbot', u'Timbot (Gutza)', u'Ginosbot', u'GrinBot', u'.anacondabot', u'Omdirigeringsrättaren', u'Rubinbot', u'HasharBot', u'NetBot', u"D'ohBot", u'Byrialbot', u'Broadbot', u'Guanabot', u'Chris G Bot 2', u'CCyeZBot', u'Soulbot', u'MSBOT', u'GnawnBot', u'Chris G Bot 3', u'Huzzlet the bot', u'JCbot', u'DodekBot', u'John Bot II', u'CyeZBot', u'Beefbot', u'Louperibot', u'SOTNBot', u'DirlBot', u'Obersachsebot', u'WikiDreamer Bot', u'YonaBot', u'Chlewbot', u'PixelBot', u'ToePeu.bot', u'HujiBot', u'Le Pied-bot', u'Ugur Basak Bot', u'NigelJBot', u'CommonsTicker', u'Tangobot', u'SeanBot', u'Corrector de redirecciones', u'HermesBot', u'Darkicebot', u'RedBot', u'HerculeBot', u'PatruBOT', u'RobotGMwikt', u'MonoBot', u'WikimediaNotifier', u'SBot39', u'DSisyphBot', u'GriffinBot1', u'WeggeBot', u'EhJBot3', u'Gerakibot', u'Picochip08', u'MondalorBot', u'Redirect fixer', u'Skagedalobot']
		
		try:
			site=wikipedia.Site(lang, family)
		except:
			print "Error", lang, family
			continue
		
		bots+=tarea000.botList(site)
		admins=tarea000.adminList(site)
		wikipedianm=tarea000.getNamespaceName(lang, family, 4)
		dbname=tarea000.getDbname(lang, family)
		time.sleep(0.5)
		server=tarea000.getServer(lang, family)
		time.sleep(0.5)
		conn = MySQLdb.connect(host='sql-s%s' % server, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
		cursor = conn.cursor()
		cursor.execute("select user_name, user_editcount from user where user_editcount!=0 order by user_editcount desc limit 5000;")
		result=cursor.fetchall()
		cursor.close()
		conn.close()
		time.sleep(0.5)
		
		s=u""
		sbots=u""
		c=1
		cbots=1
		cplanti2=1
		cuantos=projects[family][lang]['limit']
		planti2=u"{{#switch:{{{1|User}}}\n"
		planti=u"{| class='wikitable sortable' style='font-size: 90%;text-align: center;float: right;'\n! #\n! Usuario\n! Ediciones\n"
		bot_r=re.compile(ur"(?m)(^([Bb]ot|BOT) | ([Bb]ot|BOT)$|[a-z0-9\. ](Bot|BOT)$|^BOT[a-z0-9\. ])")
		for row in result:
			nick=unicode(row[0], 'utf-8')
			ed=int(row[1])
			if ed<minimumedits and c>minimumusers: #al menos minimumusers, aunque no tengan ni el minimumedits necesario
				continue
			if c<=cuantos:
				if bots.count(nick)==0 and not re.search(bot_r, nick):
					if admins.count(nick):
						s+=u"|-\n| %d || [[User:%s|%s]] (Admin) || [[Special:Contributions/%s|%s]] \n" % (c,nick,nick,nick,ed)
					else:
						s+=u"|-\n| %d || [[User:%s|%s]] || [[Special:Contributions/%s|%s]] \n" % (c,nick,nick,nick,ed)
					if c<=10:
						planti+=u"|-\n| %d || [[User:%s|%s]] || [[Special:Contributions/%s|%s]] \n" % (c,nick,nick,nick,ed)
					c+=1
			if cbots<=cuantos:
				if bots.count(nick)>0 or re.search(bot_r, nick):
					sbots+=u"|-\n| %d || [[User:%s|%s]] (Bot) || [[Special:Contributions/%s|%s]] \n" % (cbots,nick,nick,nick,ed)
				else:
					sbots+=u"|-\n| %d || [[User:%s|%s]] || [[Special:Contributions/%s|%s]] \n" % (cbots,nick,nick,nick,ed)
				cbots+=1
			if cplanti2<=2500:
				planti2+=u"|%s=%s\n" % (nick,ed)
				cplanti2+=1
		
		planti2+=u"|USUARIO DESCONOCIDO\n}}<noinclude>{{uso de plantilla}}</noinclude>"
		planti+=u"|-\n| colspan=3 | Véase también [[Wikipedia:Ranking de ediciones]]<br/>Actualizado a las {{subst:CURRENTTIME}} (UTC) del  {{subst:CURRENTDAY}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}} por [[Usuario:BOTijo|BOTijo]] \n|}<noinclude>{{uso de plantilla}}</noinclude>"
		
		resume=u""
		if bots.count(u"BOTijo") or noflagrequired.count([lang, family]):
			resume=u"BOT - Updating ranking"
		else:
			resume=u"BOT - Updating ranking (This bot [[User:BOTijo|only makes a few edits in user subpages]]. Please, don't block. Contact to [[w:es:User talk:Emijrp]])"
		
		
		#first ranking
		if projects[family][lang]['rankingusers']:
			title=u''
			if tras1[family].has_key(lang) and tras1[family][lang]:
				title=u"%s:%s" % (wikipedianm, tras1[family][lang])
				page=wikipedia.Page(site, u"%s/begin" % title)
				if projects[family][lang]['rankingusers'] and not page.exists():
					page.put(begin, resume)
					time.sleep(delay)
				page=wikipedia.Page(site, u"%s/end" % title)
				if projects[family][lang]['rankingusers'] and not page.exists():
					page.put(end, resume)
					time.sleep(delay)
				s=u"{{/begin|%d}}\n%s{{/end}}\n%s" % (cuantos, s, "\n".join(iws1[family]))
			else: #by default
				title=tras1[family]['default']
				s=u"For a list including bots, see [[%s]].\n\nFor a global list, see [[meta:User:Emijrp/List of Wikimedians by number of edits]].\n%s%s%s\n%s" % (tras2[family]['default'], table_header, s, table_footer, "\n".join(iws1[family]))
			#eliminamos autointerwiki
			s=re.sub(ur"(?im)\[\[%s:.*?\]\]\n" % lang, ur"", s)
			page=wikipedia.Page(site, title)
			if projects[family][lang]['rankingusers'] and ((not page.exists()) or (not page.isRedirectPage() and not page.isDisambig() and page.get()!=s)):
				page.put(s, resume)
				time.sleep(delay)
		
		#second ranking
		if projects[family][lang]['rankingbots]:
			title=u''
			if tras2[family].has_key(lang) and tras2[family][lang]:
				title=u"%s:%s" % (wikipedianm, tras2[family][lang])
				page=wikipedia.Page(site, u"%s/begin" % title)
				if projects[family][lang]['rankingbots'] and not page.exists():
					page.put(begin2, resume)
					time.sleep(delay)
				page=wikipedia.Page(site, u"%s/end" % title)
				if projects[family][lang]['rankingbots'] and not page.exists():
					page.put(end2, resume)
					time.sleep(delay)
				sbots=u"{{/begin|%d}}\n%s{{/end}}\n%s" % (cuantos, sbots, "\n".join(iws2[family]))
			else: #by defect
				title=tras2[family]['default']
				sbots=u"For a list excluding bots, see [[%s]].\n\nFor a global list, see [[meta:User:Emijrp/List of Wikimedians by number of edits]].\n%s%s%s\n%s" % (tras1[family]['default'], table_header, sbots, table_footer, "\n".join(iws2[family]))
			#eliminamos autointerwiki
			sbots=re.sub(ur"(?im)\[\[%s:.*?\]\]\n" % lang, ur"", sbots)
			page=wikipedia.Page(site, title)
			if projects[family][lang]['rankingbots'] and ((not page.exists()) or (not page.isRedirectPage() and not page.isDisambig() and page.get()!=sbots)):
				page.put(sbots, resume)
				time.sleep(delay)
		
		#otras plantillas
		if lang=='es':
			page=wikipedia.Page(site, u"Template:RankingEdiciones")
			page.put(planti, resume)
			
			page=wikipedia.Page(site, u"Template:Ediciones")
			page.put(planti2, resume)

