# -*- coding: utf-8  -*-
 
import wikipedia, pagegenerators
import re, sys, os
import tareas

def percent(c):
	if c % 10000 == 0:
		wikipedia.output(u'Llevamos %d' % c)

langorig='en'
st='A'
langdest='es'
if len(sys.argv)>=2:
	langdest=sys.argv[1]

redirects=tareas.getRedirectsAndTargets(langorig, targetStartsWith=st)
localpages=tareas.getPageTitle(langdest, redirects=True)

wikipediadestino=wikipedia.Site(langdest, 'wikipedia')
gen=pagegenerators.AllpagesPageGenerator(start=st, namespace=0, includeredirects=False, site=wikipediadestino)
preloadingGen=pagegenerators.PreloadingGenerator(gen, pageNumber=100, lookahead=100)
 
for page in preloadingGen:
	if page.isRedirectPage() or page.isDisambig():
		pass
	else:
		wtitle=page.title()
		
		if wtitle[0]!=st[0]:
			st=wtitle[0]
			redirects=tareas.getRedirectsAndTargets(langorig, targetStartsWith=st[0])
		
		iws=page.interwiki()
		for iw in iws:
			if iw.site().lang==langorig:
				wtext=page.get()
				m=re.compile(ur'\'{3,}(?P<bold>[^\']{3,})\'{3,}').finditer(wtext)
				for i in m:
					bold=i.group('bold')
					if bold!=wtitle and redirects.has_key(bold) and redirects[bold]==iw.title() and not localpages.has_key(bold):
						wikipedia.output(u'%s: #REDIRECT [[%s]]' % (bold, wtitle))
						#comprobar si existe antes de crear redireccion
						red=wikipedia.Page(wikipediadestino, bold)
						if not red.exists():
							red.put(u'#REDIRECT [[%s]]' % wtitle, u'BOT - #REDIRECT [[%s]]' % wtitle)
		
		
