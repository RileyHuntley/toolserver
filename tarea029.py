#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
 
import wikipedia, re, os, datetime

hoy=datetime.date.today()
ayer=hoy-datetime.timedelta(1)
anyoayer=ayer.strftime("%Y")
mesayer=ayer.strftime("%m")
diaayer=ayer.strftime("%d")
timestamphoy=hoy.strftime("%Y%m%d")
timestampayer=ayer.strftime("%Y%m%d")
os.system('''mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select concat('# \[\[',rc_title,'\]\] (\{\{diff\|',rc_this_oldid,'\|diff\}\})') from recentchanges where rc_namespace=0 and rc_user_text!='AVBOT' and rc_user_text!='Torrente' and rc_user_text!='Botarel' and rc_timestamp>=%s000000 and rc_timestamp<=%s235959 and rc_comment regexp '[Rr]evertid[ao]s?|[Dd]eshecha' order by rc_timestamp asc" > tarea029.txt''' % (timestampayer, timestampayer))
 
f=open('tarea029.txt', 'r')
log=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'Usuario:AVBOT/Reversiones humanas/%s/%s/%s' % (anyoayer, mesayer, diaayer))
log.put("{{Usuario:AVBOT/Reversiones humanas/begin}}\n%s\n{{Usuario:AVBOT/Reversiones humanas/end}}" % '\n'.join(re.sub('_', ' ', unicode(f.read(), 'utf-8')).splitlines()[1:]), u'BOT - Creando log')
f.close()
