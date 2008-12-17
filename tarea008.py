# -*- coding: utf-8 -*-

import datetime
import os, re, wikipedia

begin=u"''Please, translate this into your language and delete the english text'': This table shows '''first {{{1}}} users with more edits''' in this Wikipedia. Bots are not included.\n\n''If you want to change page title, contact to [[:es:User talk:Emijrp]]. Thanks.''\n\n<center>\n{| class='wikitable sortable' style='text-align:center;'\n! #\n! User\n! Edits\n"
begin2=u"''Please, translate this into your language and delete the english text'': This table shows '''first {{{1}}} users with more edits''' in this Wikipedia. Bots are included.\n\n''If you want to change page title, contact to [[:es:User talk:Emijrp]]. Thanks.''\n\n<center>\n{| class='wikitable sortable' style='text-align:center;'\n! #\n! User\n! Edits\n"
end=u"|}\n</center>\n\n''Please, put here a category similar to <nowiki>[[Category:Wikipedia statistics]]</nowiki>.''\n\n[[cs:Wikipedie:Nejaktivnější wikipedisté]]\n[[de:Wikipedia:Beitragszahlen]]\n[[es:Wikipedia:Lista de wikipedistas por número de ediciones]]\n[[fr:Wikipédia:Liste des Wikipédiens par nombre d'éditions]]\n[[zh-classical:維基大典:編輯次數]]\n[[id:Wikipedia:Daftar pengguna menurut jumlah suntingan]]\n[[is:Wikipedia:Notendur eftir breytingafjölda]]\n[[he:ויקיפדיה:נתונים סטטיסטיים/משתמשים/1-100]]\n[[jv:Wikipedia:Daftar panganggo miturut cacahé suntingan]]\n[[ka:ვიკიპედია:ვიკიპედიელები აქტიურობის მიხედვით]]\n[[lt:Vikipedija:Naudotojai pagal keitimų skaičių]]\n[[hu:Wikipédia:Szerkesztők listája szerkesztésszám szerint]]\n[[ja:Wikipedia:編集回数の多いウィキペディアンの一覧]]\n[[pl:Wikipedia:Najaktywniejsi wikipedyści]]\n[[pt:Wikipedia:Lista de wikipedistas por número de edições]]\n[[sq:Wikipedia:Lista e Wikipedianëve sipas redaktimeve]]\n[[uk:Вікіпедія:Найактивніші]]\n[[bat-smg:Vikipedėjė:Nauduotuojē palē keitėmu skaitliu]]\n[[zh:Wikipedia:最多贡献的用户]]"
end2=end

tras1={
u"ca": u"Llista de viquipedistes per nombre d'edicions",
u"eo": u"Listo de uzantoj laŭ redaktonombro",
u"es": u"Ranking de ediciones", 
u"fi": u"Luettelo wikipedian käyttäjistä muokkausmäärän mukaan",
u"fr": u"Utilisateurs par nombre d'éditions", 
u"gl": u"Estatísticas/Lista de usuarios por número de edicións",
u"hr": u"Popis Wikipedista po broju uređivanja",
u"hu": u"Wikipédisták listája szerkesztésszám szerint",
u"ko": u"편집횟수 순 사용자 목록",
u"pl": u"Użytkownicy według liczby edycji",
u"ro": u"Lista wikipediştilor după numărul de editări",
u"sl": u"Seznam Wikipedistov po številu urejanj",
u"sv": u"Lista över Wikipedia-användare sorterad efter antalet redigeringar",
u"vi": u"Danh sách thành viên Wikipedia theo số lần sửa trang",
}
tras2={
u"eo": u"Listo de uzantoj laŭ redaktonombro (inkluzivante robotojn)",
u"es": u"Ranking de ediciones (incluye bots)", 
u"fr": u"Utilisateurs par nombre d'éditions (bots inclus)", 
u"gl": u"Estatísticas/Lista de usuarios por número de edicións (bots incluídos)",
u"hr": u"Popis Wikipedista po broju uređivanja (botovi uključeni)",
u"hu": u"Wikipédisták listája szerkesztésszám szerint (botokkal)",
u"ko": u"편집횟수 순 사용자 목록 (봇 포함)",
u"pl": u"Użytkownicy według liczby edycji (w tym boty)",
u"ro": u"Lista wikipediştilor după numărul de editări (inclusiv boţi)",
u"sl": u"Seznam Wikipedistov po številu urejanj (z boti)",
u"sv": u"Lista över Wikipedia-användare sorterad efter antalet redigeringar (inklusive robotar)",
u"vi": u"Danh sách thành viên Wikipedia theo số lần sửa trang (tính cả bot)",
}

lll=['es', 'eo', 'hu', 'ca', 'tr', 'ro', 'vo', 'fi', 'it', 'nl', 'ru', 'sv', 'no', 'da', 'ar', 'ko', 'sr', 'sl', 'vi', 'bg', 'et', 'ht', 'fa', 'hr', 'new', 'nn', 'te', 'gl', 'th', 'simple', 'he']
lll=['es', 'eo', 'hu', 'ca', 'tr', 'ro', 'vo', 'nl', 'sv', 'no', 'da', 'ar', 'ko', 'sr', 'sl', 'vi', 'et', 'ht', 'fa', 'hr', 'new', 'nn', 'te', 'gl', 'th', 'simple', 'he']
for lang in lll:
	site=wikipedia.Site(lang, 'wikipedia')
	
	bots=[u'BOTpolicia', u'AVBOT', u'CommonsDelinker', u'Eskimbot', u'YurikBot', u'H-Bot', u'Paulatz bot', u'TekBot', u'Alfiobot', u'RoboRex', u'Agtbot', u'Felixbot', u'Pixibot', u'Sz-iwbot', u'Timbot (Gutza)', u'Ginosbot', u'GrinBot', u'.anacondabot', u'Omdirigeringsrättaren']
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
	
	
	os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select user_name, user_editcount from user where user_editcount!=0 order by user_editcount desc limit 5000;" > /home/emijrp/temporal/tarea008.data' % (lang, lang))
	
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
	
	s+=u"{{/end}}"
	sbots+=u"{{/end}}"
	planti2+=u"|USUARIO DESCONOCIDO\n}}<noinclude>{{uso de plantilla}}</noinclude>"
	planti+=u"|-\n| colspan=3 | Véase también [[Wikipedia:Ranking de ediciones]]<br/>Actualizado a las {{subst:CURRENTTIME}} (UTC) del  {{subst:CURRENTDAY}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}} por [[Usuario:Toolserver|Toolserver]] \n|}<noinclude>{{uso de plantilla}}</noinclude>"
	
	resume=u"BOT - Updating ranking (TESTING BOT, PLEASE DON'T PANIC, I'M GOING TO REQUEST FLAG SOON)"
	title=u''
	#first ranking
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
	
	if lang=='es':
		page=wikipedia.Page(site, u"Template:RankingEdiciones")
		page.put(planti, resume)
		
		page=wikipedia.Page(site, u"Template:Ediciones")
		page.put(planti2, resume)

	if lang!='es':
		up=u"This user is a bot. It won't understand you. Comments to [[:es:User talk:Emijrp]]. Thanks.\n\nThis bot is executed from [[meta:Toolserver]], so, if it is necessary, block it by nick. Other users can use the same IP address."
		page=wikipedia.Page(site, u"User:BOTijo")
		if not page.exists():
			page.put(up, u"BOT")


