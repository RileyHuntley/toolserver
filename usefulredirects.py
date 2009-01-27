# -*- coding: utf-8  -*-
 
import wikipedia, pagegenerators
import re, sys, os
import tareas

def percent(c):
	if c % 10000 == 0:
		wikipedia.output(u'Llevamos %d' % c)

st='A'
if len(sys.argv)>=2:
	st=sys.argv[1]

redirects=tareas.getRedirectsAndTargets('en', targetStartsWith=st)
localpages=tareas.getPageTitle('es', redirects=True)

wikipediaes=wikipedia.Site('es', 'wikipedia')
gen=pagegenerators.AllpagesPageGenerator(start=st, namespace=0, includeredirects=False, site=wikipediaes)
preloadingGen=pagegenerators.PreloadingGenerator(gen, pageNumber=100, lookahead=100)
 
for page in preloadingGen:
	if page.isRedirectPage() or page.isDisambig():
		pass
	else:
		wtitle=page.title()
		
		if wtitle[0]!=st[0]:
			st=wtitle[0]
			redirects=tareas.getRedirectsAndTargets('en', targetStartsWith=st[0])
		
		iws=page.interwiki()
		for iw in iws:
			if iw.site().lang=='en':
				wtext=page.get()
				m=re.compile(ur'\'{3,}(?P<bold>[^\']{3,})\'{3,}').finditer(wtext)
				for i in m:
					bold=i.group('bold')
					if bold!=wtitle and redirects.has_key(bold) and redirects[bold]==iw.title() and not localpages.has_key(bold):
						wikipedia.output(u'%s: #REDIRECT [[%s]]' % (bold, wtitle))
						#comprobar si existe antes de crear redireccion
						red=wikipedia.Page(wikipediaes, bold)
						if not red.exists():
							red.put(u'#REDIRECT [[%s]]' % wtitle, u'BOT - Creando redirección hacia [[%s]]' % wtitle)
		
		
