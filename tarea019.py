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
import os, re, wikipedia


site=wikipedia.Site('es', 'wikipedia')

os.system('mysql -h sql-s3 -e "use eswiki_p;select page_title, page_touched from page where page_namespace=0 and page_is_redirect=0 order by page_touched asc limit 1000;" > /home/emijrp/temporal/tarea019.data')

f=open('/home/emijrp/temporal/tarea019.data', 'r')
sql=unicode(f.read(), 'utf-8')
f.close()
m=re.compile(ur"(.+)	(\d+)").finditer(sql)

c=1
cuantos=500
viejisima=u''
s=u"{{/begin|%d}}\n" % cuantos
for i in m:
	fecha=str(i.group(2))
	fecha=u'%s-%s-%s %s:%s:%s' % (fecha[0:4], fecha[4:6], fecha[6:8], fecha[8:10], fecha[10:12], fecha[12:14])
	titulo_=i.group(1)
	titulo=re.sub('_', ' ', titulo_)
	if c==1:
		viejisima+=titulo
	if c<=cuantos:
		s+=u"|-\n| %d || [[%s]] || <span class='plainlinks'>[http://es.wikipedia.org/w/index.php?title=%s&action=history %s]</span> \n" % (c, titulo, titulo_, fecha)
		c+=1
	

s+=u"{{/end}}"
page=wikipedia.Page(site, u"Wikipedia:Páginas viejas")
page.put(s, u"BOT - Actualizando páginas viejas. La más vieja es [[%s]]" % viejisima)
