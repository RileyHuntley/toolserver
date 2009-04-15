#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
 
import wikipedia, re
 
site = wikipedia.Site('es', 'wikipedia')
wiii = wikipedia.Page(site, u'Usuario:AVBOT/Errores/Automático')
wtext=wiii.get()

salida=u""
for l in wtext.splitlines():
	if re.search(ur'(?im)^\# \[\[([^\]]+?)\]\], ', l):
		wtitle=l.split("]],")[0].split("[[")[1]
		temp=wikipedia.Page(site, wtitle)
		if temp.exists():
			salida+=l+'\n'
			wikipedia.output(wtitle+' existe')
		else:
			wikipedia.output(wtitle+' NO existe')
	else:
		salida+=l+'\n'

if wtext!=salida:
	wiii.put(salida, u'BOT - Limpiando páginas que se han borrado')

wikipedia.stopme()
