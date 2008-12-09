# -*- coding: utf-8 -*-

import wikipedia,re,sys,os,gzip,time, datetime

trad={
'es':u'Wikipedia:Protección de plantillas',
'en':u'User:Emijrp/Most linked templates status',
'de':u'User:Emijrp/Most linked templates status',
'fr':u'User:Emijrp/Most linked templates status',
}

for lang in ['en', 'es', 'fr', 'de']:
	site=wikipedia.Site(lang, 'wikipedia')

	#cargamos lista de plantillas mas usadas
	templates=[]
	data=site.getUrl("/w/index.php?title=Special:Mostlinkedtemplates&limit=500&offset=0")
	data=data.split('<!-- start content -->')
	data=data[1].split('<!-- end content -->')[0]
	#<li><a href="/wiki/Mod%C3%A8le:!" title="Modèle:!">Modèle:!</a> ‎(<a href="/w/index.php?title=Special:Pages_li%C3%A9es&amp;target=Mod%C3%A8le%3A%21" title="Special:Pages liées">602 833 liens</a>)</li>

	m=re.compile(ur"(?i)<li><a href=\"[^\"]*?\" title=\"[^\:]*?\:([^\"]*?)\">.*?</a>.*?<a href=.*?>(.*?) [a-z]").finditer(data)
	for i in m:
		title=i.group(1)
		title=re.sub(ur'\&\#039\;', ur"'", title)
		links=i.group(2)
		#wikipedia.output(u'%s - %s' % (title, links))
		templates.append([title, links])

	#cargamos diccionario de protecciones
	protectsedit={}
	protectsmove={}
	os.system(u'mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title, pr_type, pr_level from page, page_restrictions where page_id=pr_page and pr_level!=\'\' and page_namespace=10" > /home/emijrp/temporal/protecciondeplantillas' % (lang, lang))
	f=open('/home/emijrp/temporal/protecciondeplantillas', 'r')
	sql=unicode(f.read(), 'utf-8')
	f.close()
	n=re.compile(ur"(?im)^(.*?)	(.*?)	(.*?)$").finditer(sql)
	for j in n:
		title=j.group(1)
		title=re.sub(ur'_', ur' ', title)
		type=j.group(2)
		who=j.group(3)
		if type=='edit':
			protectsedit[title]=who
		elif type=='move':
			protectsmove[title]=who

	#print len(protectsedit.items())

	s=u"{{/begin}}"
	c=0
	for template, links in templates:
		c+=1
		s+=u"\n|-\n| %s || [[Template:%s]] || %s" % (str(c),template, links)
		if protectsedit.has_key(template):
			s+=u' || %s' % protectsedit[template]
		else:
			s+=u' || ·'
		
		if protectsmove.has_key(template):
			s+=u' || %s ' % protectsmove[template]
		else:
			s+=u' || · '

	s+=u"\n{{/end}}\n"

	#+iws
	for k, v in trad.items():
		if k!=lang:
			s+=u"\n[[%s:%s]]" % (k, v)

	#wikipedia.output(s)

	title=u'User:Emijrp/Most linked templates status'
	if trad.has_key(lang):
		title=trad[lang]

	wiii=wikipedia.Page(site, title)
	wiii.put(s, u'BOT - Updating list')

	#begin
	begin=u"<center>\n{| class='wikitable sortable' style='text-align:center;'\n! #\n! Template\n! Links\n! Edit\n! Move\n"
	wiii=wikipedia.Page(site, u"%s/begin" % title)
	if not wiii.exists():
		wiii.put(begin, u'BOT - Updating list')

	#end
	end=u"|}\n</center>"
	wiii=wikipedia.Page(site, u"%s/end" % title)
	if not wiii.exists():
		wiii.put(end, u'BOT - Updating list')

