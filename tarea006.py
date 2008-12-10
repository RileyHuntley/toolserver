# -*- coding: utf-8 -*-

import datetime
import os, re, wikipedia

site=wikipedia.Site("es", "wikipedia")

#discusiones mas activas
diferencia=3 # 3 dias
date=datetime.datetime.now()-datetime.timedelta(days=diferencia)
timestamp="%s" % date.year
if date.month<10:
	timestamp+="0%s" % date.month
else:
	timestamp+="%s" % date.month
if date.day<10:
	timestamp+="0%s" % date.day
else:
	timestamp+="%s" % date.day
if date.hour<10:
	timestamp+="0%s" % date.hour
else:
	timestamp+="%s" % date.hour
if date.minute<10:
	timestamp+="0%s" % date.minute
else:
	timestamp+="%s" % date.minute
if date.second<10:
	timestamp+="0%s" % date.second
else:
	timestamp+="%s" % date.second

os.system('mysql -h sql-s3 -e "use eswiki_p;select count(*), rc_title from recentchanges where rc_timestamp>=%s and rc_namespace=1 group by rc_title order by count(*) desc limit 25;" > /home/emijrp/temporal/tarea006data' % timestamp)

f=open('/home/emijrp/temporal/tarea006data', 'r')
sql=unicode(f.read(), 'utf-8')
m=re.compile(ur"(\d+)	(.*)").finditer(sql)

page=wikipedia.Page(site, "Template:DiscusionesActivas")
s=u"<div class='plainlinks'>\n{| class='wikitable' style='clear: right;float: right;margin: 0 0 1em 1em;font-size: 90%;text-align: center;'\n! Discusiones más activas [[Image:FireIcon.svg|18px]]\n! Ediciones\n"
c=1
for i in m:
	ed=str(i.group(1))
	art_=i.group(2)
	art=re.sub("_", " ", art_)
	if not re.search(u"Candidatura a destacado", art):
		if c<=5:
			s+=u"|-\n| [[Discusión:%s|%s]] || [http://es.wikipedia.org/w/index.php?title=Discusión:%s&action=history %s] \n" % (art,art,art_,ed)
		c+=1
s+=u"|-\n| colspan='2' | Actualizado a las {{subst:CURRENTTIME}} (UTC) del {{subst:CURRENTDAY}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}} por [[Usuario:Toolserver|Toolserver]]\n"
s+=u"|}\n</div>"
wikipedia.output(s)
page.put(s, u"BOT - Actualizando plantilla")
f.close()
