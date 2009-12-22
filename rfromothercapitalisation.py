# -*- coding: utf-8  -*-

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

import wikipedia, pagegenerators
import re, random, time, sys, datetime
import cosmetic_changes

days=[u'A', u'B', u'C', u'D', u'E', u'F', u'G', u'H', u'I', u'J', u'K', u'L', u'M', u'N', u'Ñ', u'O', u'P', u'Q', u'R', u'S', u'T', u'U', u'V', u'W', u'X', u'Y', u'Z', u'Á', u'É', u'Í', u'Ó']
wiki=wikipedia.Site("en", "wikipedia")
day=datetime.datetime.now().day
day=day % len(days)
if len(sys.argv)==2:
	start=sys.argv[1]
	gen=pagegenerators.AllpagesPageGenerator(start, namespace = 0, includeredirects = True, site = wiki)
else:
	start=days[day]
	gen=pagegenerators.AllpagesPageGenerator(start, namespace = 0, includeredirects = True, site = wiki)
preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber = 200)

for page in preloadingGen:
	if page.exists() and page.isRedirectPage():
		wikipedia.output(u"Analizando: [[%s]]" % page.title())
		wtext=page.get(get_redirect=True)
		wtitle=page.title()
		#punto de ruptura
		if start[0]!=wtitle[0]:
			break
		target=page.getRedirectTarget().title()
		if wtitle.lower()==target.lower() and (len(wtext)==len(target)+13 or len(wtext)==len(target)+14):
			salida=u'#REDIRECT [[%s]] {{R from other capitalisation}}' % target
			if wtext!=salida:
				try:
					page.put(salida, u'BOT - Sorting redirects')
				except:
					pass
