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

import datetime
import os, re, wikipedia, sys

begin=u"''Please, translate this into your language and delete the english text'': This table shows '''first {{{1}}} users with more edits''' in this Wikipedia. Bots are not included.\n\n''If you want to change page title, contact to [[:es:User talk:Emijrp]]. Thanks.''\n\n<center>\n{| class='wikitable sortable' style='text-align:center;'\n! #\n! User\n! Edits\n"
begin2=u"''Please, translate this into your language and delete the english text'': This table shows '''first {{{1}}} users with more edits''' in this Wikipedia. Bots are included.\n\n''If you want to change page title, contact to [[:es:User talk:Emijrp]]. Thanks.''\n\n<center>\n{| class='wikitable sortable' style='text-align:center;'\n! #\n! User\n! Edits\n"
end=u"|}\n</center>\n\n''Please, put here a category similar to <nowiki>[[Category:Wikipedia statistics]]</nowiki>.''\n\n[[cs:Wikipedie:Nejaktivnější wikipedisté]]\n[[de:Wikipedia:Beitragszahlen]]\n[[es:Wikipedia:Lista de wikipedistas por número de ediciones]]\n[[fr:Wikipédia:Liste des Wikipédiens par nombre d'éditions]]\n[[zh-classical:維基大典:編輯次數]]\n[[id:Wikipedia:Daftar pengguna menurut jumlah suntingan]]\n[[is:Wikipedia:Notendur eftir breytingafjölda]]\n[[he:ויקיפדיה:נתונים סטטיסטיים/משתמשים/1-100]]\n[[jv:Wikipedia:Daftar panganggo miturut cacahé suntingan]]\n[[ka:ვიკიპედია:ვიკიპედიელები აქტიურობის მიხედვით]]\n[[lt:Vikipedija:Naudotojai pagal keitimų skaičių]]\n[[hu:Wikipédia:Szerkesztők listája szerkesztésszám szerint]]\n[[ja:Wikipedia:編集回数の多いウィキペディアンの一覧]]\n[[pl:Wikipedia:Najaktywniejsi wikipedyści]]\n[[pt:Wikipedia:Lista de wikipedistas por número de edições]]\n[[sq:Wikipedia:Lista e Wikipedianëve sipas redaktimeve]]\n[[uk:Вікіпедія:Найактивніші]]\n[[bat-smg:Vikipedėjė:Nauduotuojē palē keitėmu skaitliu]]\n[[zh:Wikipedia:最多贡献的用户]]"
end2=end

tras1={
u"ar": u"قائمة الويكيبيديين حسب عدد التعديلات",
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
}
tras2={
u"ar": u"قائمة الويكيبيديين حسب عدد التعديلات (متضمنة البوتات)",
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
}

#do not want: nl, simple 
# fix: hr
projects={
'wikinews': ['es'],
#'wikipedia': ['es', 'eo', 'hu', 'ca', 'tr', 'ro', 'vo', 'fi', 'it', 'nl', 'ru', 'sv', 'no', 'da', 'ar', 'ko', 'sr', 'sl', 'vi', 'bg', 'et', 'ht', 'fa', 'hr', 'new', 'nn', 'te', 'gl', 'th', 'simple', 'he'],
'wikipedia': ['es', 'hr', 'ro', 'simple', 'th', 'tr', 'vi', 'da', 'eo', 'ar'],
}

#if len(sys.argv)>1:
#	lll=[sys.argv[1]]

#generating interwikis
iws1={}
iws2={}
for family, langs in projects.items():
	iws1[family]=[]
	iws2[family]=[]
	for lang in langs:
		site=wikipedia.Site(lang, family)
		data=site.getUrl("/w/index.php?title=Special:RecentChanges&limit=0")
		data=data.split('<select id="namespace" name="namespace" class="namespaceselector">')[1].split('</select>')[0]
		m=re.compile(ur'<option value="([1-9]\d*)">(.*?)</option>').finditer(data)
		wikipedianm=u''
		for i in m:
			number=i.group(1)
			name=i.group(2)
			if number=='4':
				wikipedianm+=name
		traslation1="List of Wikipedians by number of edits"
		if tras1.has_key(lang):
			traslation1=tras1[lang]
		iws1[family].append(u"[[%s:%s:%s]]" % (lang, wikipedianm, traslation1)
		traslation2="List of Wikipedians by number of edits (bots included)"
		if tras2.has_key(lang):
			traslation2=tras2[lang]
		iws2[family].append(u"[[%s:%s:%s]]" % (lang, wikipedianm, traslation2))
	iws1[family].sort()
	iws2[family].sort()

for family, langs in projects.items():
	for lang in langs:
		#la lista de bots debe ir dentro del bucle
		bots=[u'BOTpolicia', u'AVBOT', u'CommonsDelinker', u'Eskimbot', u'EmxBot', u'YurikBot', u'H-Bot', u'Paulatz bot', u'TekBot', u'Alfiobot', u'RoboRex', u'Agtbot', u'Felixbot', u'Pixibot', u'Sz-iwbot', u'Timbot (Gutza)', u'Ginosbot', u'GrinBot', u'.anacondabot', u'Omdirigeringsrättaren', u'Rubinbot', u'HasharBot', u'NetBot', u"D'ohBot", u'Byrialbot', u'Broadbot', u'Guanabot', u'Chris G Bot 2', u'CCyeZBot', u'Soulbot', u'MSBOT', u'GnawnBot', u'Chris G Bot 3', u'Huzzlet the bot', u'JCbot', u'DodekBot', u'John Bot II', u'CyeZBot', u'Beefbot', u'Louperibot', u'SOTNBot', u'DirlBot', u'Obersachsebot', u'WikiDreamer Bot', u'YonaBot', u'Chlewbot', u'PixelBot', u'ToePeu.bot', u'HujiBot', u'Le Pied-bot', u'Ugur Basak Bot', u'NigelJBot', u'CommonsTicker', u'Tangobot', u'SeanBot', u'Corrector de redirecciones', u'HermesBot', u'Darkicebot', u'RedBot', u'HerculeBot', u'PatruBOT']
		site=wikipedia.Site(lang, family)
		
		data=site.getUrl("/w/index.php?title=Special:Listusers&limit=5000&group=bot")
		data=data.split('<!-- start content -->')
		data=data[1].split('<!-- end content -->')[0]
		m=re.compile(ur" title=\".*?:(.*?)\">").finditer(data)
		for i in m:
			bots.append(i.group(1))
		
		admins=[]
		data=site.getUrl("/w/index.php?title=Special:Listusers&limit=5000&group=sysop")
		data=data.split('<!-- start content -->')
		data=data[1].split('<!-- end content -->')[0]
		m=re.compile(ur" title=\".*?:(.*?)\">").finditer(data)
		for i in m:
			admins.append(i.group(1))
		
		data=site.getUrl("/w/index.php?title=Special:RecentChanges&limit=0")
		data=data.split('<select id="namespace" name="namespace" class="namespaceselector">')[1].split('</select>')[0]
		m=re.compile(ur'<option value="([1-9]\d*)">(.*?)</option>').finditer(data)
		wikipedianm=u''
		for i in m:
			number=i.group(1)
			name=i.group(2)
			if number=='4':
				wikipedianm+=name
		
		family2='wiki'
		if family=='wikinews':
			family2='wikinews'
		
		os.system('mysql -h %s%s-p.db.toolserver.org -e "use %s%s_p;select user_name, user_editcount from user where user_editcount!=0 order by user_editcount desc limit 5000;" > /home/emijrp/temporal/tarea008.data' % (lang, family2, lang, family2))
		
		f=open('/home/emijrp/temporal/tarea008.data', 'r')
		sql=unicode(f.read(), 'utf-8')
		f.close()
		m=re.compile(ur"(.+)	(\d+)").finditer(sql)
		
		c=1
		cbots=1
		cplanti2=1
		cuantos=500
		s=u"{{/begin|%d}}\n" % cuantos
		sbots=u"{{/begin|%d}}\n" % cuantos
		planti2=u"{{#switch:{{{1|User}}}\n"
		planti=u"{| class='wikitable sortable' style='font-size: 90%;text-align: center;float: right;'\n! #\n! Usuario\n! Ediciones\n"
		for i in m:
			ed=str(i.group(2))
			nick=i.group(1)
			if c<=cuantos:
				if bots.count(nick)==0:
					if admins.count(nick):
						s+=u"|-\n| %s || [[User:%s|%s]] (Admin) || [[Special:Contributions/%s|%s]] \n" % (str(c),nick,nick,nick,ed)
					else:
						s+=u"|-\n| %s || [[User:%s|%s]] || [[Special:Contributions/%s|%s]] \n" % (str(c),nick,nick,nick,ed)
					if c<=10:
						planti+=u"|-\n| %s || [[User:%s|%s]] || [[Special:Contributions/%s|%s]] \n" % (str(c),nick,nick,nick,ed)
					c+=1
			if cbots<=cuantos:
				if bots.count(nick):
					sbots+=u"|-\n| %s || [[User:%s|%s]] (Bot) || [[Special:Contributions/%s|%s]] \n" % (str(cbots),nick,nick,nick,ed)
				else:
					sbots+=u"|-\n| %s || [[User:%s|%s]] || [[Special:Contributions/%s|%s]] \n" % (str(cbots),nick,nick,nick,ed)
				cbots+=1
			if cplanti2<=2500:
				planti2+=u"|%s=%s\n" % (nick,ed)
				cplanti2+=1
		
		s+=u"%s\n" % ("\n".join(iws1[family]))
		s=re.sub(ur"(?im)\[\[%s:.*?\]\]\n" % lang, ur"", s)
		s+=u"{{/end}}"
		sbots+=u"%s\n" % ("\n".join(iws2[family]))
		sbots=re.sub(ur"(?im)\[\[%s:.*?\]\]\n" % lang, ur"", sbots)
		sbots+=u"{{/end}}"
		planti2+=u"|USUARIO DESCONOCIDO\n}}<noinclude>{{uso de plantilla}}</noinclude>"
		planti+=u"|-\n| colspan=3 | Véase también [[Wikipedia:Ranking de ediciones]]<br/>Actualizado a las {{subst:CURRENTTIME}} (UTC) del  {{subst:CURRENTDAY}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}} por [[Usuario:BOTijo|BOTijo]] \n|}<noinclude>{{uso de plantilla}}</noinclude>"
		
		resume=u""
		if bots.count(u"BOTijo"):
			resume=u"BOT - Updating ranking"
		else:
			resume=u"BOT - Updating ranking (Testing bot, please don't panic, I'm going to request flag soon)"
		
		
		#first ranking
		if len(s)>1000: #evitando errores de db replication
			title=u''
			if tras1.has_key(lang):
				title=u"%s:%s" % (wikipedianm, tras1[lang])
			else:
				title=u"%s:List of Wikipedians by number of edits" % wikipedianm
			page=wikipedia.Page(site, title)
			if not page.isRedirectPage() and not page.isDisambig():
				page.put(s, resume)
		
		#begin & end
		page=wikipedia.Page(site, u"%s/begin" % title)
		if not page.exists():
			page.put(begin, resume)
		page=wikipedia.Page(site, u"%s/end" % title)
		if not page.exists():
			page.put(end, resume)
		
		#second ranking
		if len(sbots)>1000: #evitando errores de db replication
			title=u''
			if tras2.has_key(lang):
				title=u"%s:%s" % (wikipedianm, tras2[lang])
			else:
				title=u"%s:List of Wikipedians by number of edits (bots included)" % wikipedianm
			page=wikipedia.Page(site, title)
			if not page.isRedirectPage() and not page.isDisambig():
				page.put(sbots, resume)
		
		#begin & end
		page=wikipedia.Page(site, u"%s/begin" % title)
		if not page.exists():
			page.put(begin2, resume)
		page=wikipedia.Page(site, u"%s/end" % title)
		if not page.exists():
			page.put(end2, resume)
		
		#otras plantillas
		if lang=='es':
			page=wikipedia.Page(site, u"Template:RankingEdiciones")
			page.put(planti, resume)
			
			page=wikipedia.Page(site, u"Template:Ediciones")
			page.put(planti2, resume)
		
		#userpages
		if lang!='es':
			up=u"This user is a bot. It won't understand you. Comments to [[:es:User talk:Emijrp]]. Thanks.\n\nThis bot is executed from [[meta:Toolserver]], so, if it is necessary, block it by nick. Other users can use the same IP address."
			page=wikipedia.Page(site, u"User:BOTijo")
			if not page.exists():
				page.put(up, u"BOT")


