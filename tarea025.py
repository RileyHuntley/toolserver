#!/usr/bin/env python2.5
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
