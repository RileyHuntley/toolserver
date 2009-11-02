# -*- coding: utf-8 -*-

import wikipedia
import urllib, re

eswiki=wikipedia.Site('es', 'wikipedia')
users=['AVBOT', 'BOTijo', 'Emijrp', 'Emijrpbot', 'Poc-oban', 'Toolserver']
path="http://toolserver.org/~vvv/sulutil.php?user="
salida=u"{{#switch:{{{1|}}}"
total=oldtotal=0
for i in users:
	url=path+i
	f=urllib.urlopen(url, 'r')
	m=re.compile(ur"Total editcount: <b>(\d+)</b>").finditer(f.read())
	for j in m:
		salida+=u"\n|%s=%s" % (i, j.group(1))
		total+=int(j.group(1))
	f.close()
salida+=u"\n|Total=%d\n|%d}}" % (total, total)

editcount=wikipedia.Page(eswiki, u"User:Emijrp/Editcount")
#evitamos regresiones en el contador
editcountold=int(editcount.get().split("Total=")[1].split("\n")[0])

if total>oldtotal:
	wikipedia.Page(eswiki, u"User:Emijrp/Editcount/Old").put(editcount.get(), u"BOT - Datos de la versión anterior de [[User:Emijrp/Editcount]]")	
	editcount.put(salida, u"BOT - Actualizando ediciones globales de %s: %d" % (", ".join(users), total))
