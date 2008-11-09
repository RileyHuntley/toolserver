# -*- coding: utf-8 -*-

import wikipedia,re,sys,os,gzip,time, datetime

site=wikipedia.Site('es', 'wikipedia')

#cargamos lista de plantillas mas usadas
templates=[]
data=site.getUrl("/w/index.php?title=Special:Mostlinkedtemplates&limit=500&offset=0")
data=data.split('<!-- start content -->')
data=data[1].split('<!-- end content -->')[0]
m=re.compile(ur" title=\"Plantilla\:(.*?)\">.*?(\d+\.?\d+) enlaces").finditer(data)
for i in m:
	title=i.group(1)
	links=i.group(2)
	templates.append([title, links])

#cargamos diccionario de protecciones
protectsedit={}
protectsmove={}
os.system(u'mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select page_title, pr_type, pr_level from page, page_restrictions where page_id=pr_page and pr_level!=\'\' and page_namespace=10" > /home/emijrp/temporal/protecciondeplantillas')
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
	s+=u"\n|-\n| %s || [[Plantilla:%s]] || %s" % (str(c),template, links)
	if protectsedit.has_key(template):
		s+=u' || %s' % protectsedit[template]
	else:
		s+=u' || ·'
	
	if protectsmove.has_key(template):
		s+=u' || %s ' % protectsmove[template]
	else:
		s+=u' || · '

s+=u"\n{{/end}}\n"

#wikipedia.output(s)

wiii=wikipedia.Page(site, u'Wikipedia:Protección de plantillas')
wiii.put(s, u'BOT - Actualizando lista de protección de plantillas')
