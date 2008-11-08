#!/usr/bin/python
# -*- coding: utf-8  -*-

import wikipedia, pagegenerators, re, time, catlib, sys

site = wikipedia.Site('es', 'wikipedia')
cat = catlib.Category(site, u'Categoría:Wikipedia:Esbozo geografía de Francia')
gen=pagegenerators.CategorizedPageGenerator(cat, start=sys.argv[1])
preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber=50)

template={}
template[u'Ficha de localidad de Francia']={
u'nomcommune':u'nomcommune',
u'imagen_bandera':u'',
u'imagen_escudo':u'',
u'imagen':u'',
u'région':u'région',
u'département':u'département',
u'arrondissement':u'arrondissement',
u'canton':u'canton',
u'insee':u'insee',
u'cp':u'cp',
u'maire':u'maire',
u'mandat':u'mandat',
u'nomhab':u'',
u'intercomm':u'intercomm',
u'longitude':u'longitude',
u'latitude':u'latitude',
u'alt moy':u'alt moy',
u'alt mini':u'alt mini',
u'alt maxi':u'alt maxi',
u'hectares':u'hectares',
u'km²':u'km²',
u'sans':u'sans',
u'date-sans':u'date-sans',
u'dens':u'dens', #no existe en la plantilla, pero me quito de problemas
}
t=u'Ficha de localidad de Francia'

for page in preloadingGen:
	wikipedia.output(page.title())
	wtext=page.get()
	newtext=wtext
	
	iws=page.interwiki()
	iwtitle=u''
	for iw in iws:
		if iw.site().lang=='fr':
			if iw.exists() and not iw.isRedirectPage() and not iw.isDisambig():
				iwtitle=iw.title()
				iwtext=iw.get()
				
				params={}
				#for param in [u'alt moy', u'alt mini', u'alt maxi']:
				for param in [u'longitude', u'latitude']:
					#m=re.findall(ur'(?im)^\|? *%s *\= *(\d+)( *m)? *\|?$' % param, iwtext)
					m=re.findall(ur'(?im)^\|? *%s *\= *(\-?\d\.?\d+) *\|?$' % param, iwtext)
					
					if m:
						print m
						params[param]=m[0][0]
				
				if params[u'latitude']<51.09 and params[u'latitude']>41.32:
					if params[u'longitude']>-5.0 and params[u'longitude']<9.56:
						for param, value in params.items():
							newtext=re.sub(ur'(?im)^ *(\|? *%s *\= *)(\|? *\r)' % param, ur'\1 %s\2' % value, newtext)
	
	resumen=u'BOT -'
	if wtext!=newtext:
		resumen+=u' Añadiendo parámetros desde [[:fr:%s]];' % iwtitle
	
	# hemos cambiado algo?
	if wtext!=newtext:
		
		
		maxlen=0
		for param, trad in template[t].items():
			if maxlen<len(param):
				maxlen=len(param)
		
		for param, trad in template[t].items():
			newtext=re.sub(ur'(?im)^ *\|? *%s *\= *([^\n\r]*?) *\|?(\r)' % (param), ur'| %s%s = \1\2' % (param, ' '*(maxlen-len(param))), newtext)
		
		
		wikipedia.showDiff(wtext, newtext)
		#page.put(newtext, u'%s Justificando parámetros;' % resumen)
		