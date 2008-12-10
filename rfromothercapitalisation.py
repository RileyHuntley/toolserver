# -*- coding: utf-8  -*-

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
