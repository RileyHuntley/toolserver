# -*- coding: utf-8 -*-

import wikipedia
import urllib, re

users=['AVBOT', 'BOTijo', 'Emijrp', 'Emijrpbot', 'Poc-oban', 'Toolserver']
path="http://toolserver.org/~vvv/sulutil.php?user="
salida=u"{{#switch:{{{1|}}}"
total=0
for i in users:
	url=path+i
	f=urllib.urlopen(url, 'r')
	m=re.compile(ur"Total editcount: <b>(\d+)</b>").finditer(f.read())
	for j in m:
		salida+=u"\n|%s=%s" % (i, j.group(1))
		total+=int(j.group(1))
	f.close()
salida+=u"\n|Total=%d\n|%d}}" % (total, total)

if total>0:
	editcount=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u"User:Emijrp/Editcount")
	editcount.put(salida, u"BOT - Actualizando ediciones globales de %s: %d" % (", ".join(users), total))
