# -*- coding: utf-8 -*-

import datetime
import os, re, wikipedia

tras1={u"es": u"Ranking de ediciones", u"fr": u"Utilisateurs par nombre d'éditions", u"pl": u"Użytkownicy według liczby edycji"}
tras2={u"es": u"Ranking de ediciones (incluye bots)", u"fr": u"Utilisateurs par nombre d'éditions (bots inclus)", u"pl": u"Użytkownicy według liczby edycji (w tym boty)"}

for lang in ['es']:
	site=wikipedia.Site(lang, 'wikipedia')
	
	bots=[u'BOTpolicia', u'AVBOT', u'CommonsDelinker', u'Eskimbot']
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
	
	
	os.system('mysql -h sql-s3 -e "use %swiki_p;select user_name, user_editcount from user order by user_editcount desc limit 5000;" > /home/emijrp/temporal/tarea008.data' % lang)
	
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
	
	if tras1.has_key(lang):
		page=wikipedia.Page(site, u"%s:%s" % (wikipedianm, tras1[lang]))
	else:
		page=wikipedia.Page(site, u"%s:Users by number of edits" % wikipedianm)
	page.put(s, "BOT - Updating ranking")
	
	if tras2.has_key(lang):
		page=wikipedia.Page(site, u"%s:%s" % (wikipedianm, tras2[lang]))
	else:
		page=wikipedia.Page(site, u"%s:Users by number of edits (bots included)" % wikipedianm)
	page.put(sbots, "BOT - Updating ranking")
	
	page=wikipedia.Page(site, u"Template:RankingEdiciones")
	page.put(planti, "BOT - Updating template")
	
	page=wikipedia.Page(site, u"Template:Ediciones")
	page.put(planti2, "BOT - Updating template")
