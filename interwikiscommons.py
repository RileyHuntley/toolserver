# -*- coding: utf-8  -*-
 
import wikipedia, pagegenerators
import re, sys

st='A'
if len(sys.argv)>=2:
	st=sys.argv[1]

commons=wikipedia.Site('commons', 'commons')
wikipediaen=wikipedia.Site('en', 'wikipedia')
gen=pagegenerators.AllpagesPageGenerator(start=st, namespace=0, includeredirects=False, site=commons)
preloadingGen=pagegenerators.PreloadingGenerator(gen, pageNumber=100, lookahead=100)
 
for page in preloadingGen:
	if page.isRedirectPage() or page.isDisambig():
		pass
	else:
		ctext=page.get()
		ctitle=page.title()
		
		if re.search(ur'(?i)p4b', ctitle):
			continue
		
		print "-"*50
		wikipedia.output(u"Analizando: [[%s]]" % ctitle)
		m=re.compile(ur"(?i)\[\[(en):([^]]*?)\]\]").finditer(ctext)
		
		id=u""
		iw=u""
		for i in m:
			if not id and not iw:
				id=i.group(1)
				iw=i.group(2)
		
		if not id or not iw:
			continue
		
		p=wikipedia.Page(wikipedia.Site(id, "wikipedia"), iw)
		try:
			if p.exists() and not p.isRedirectPage() and not p.isDisambig():
				wiws=p.interwiki()
				wiws.append(p)
				wiws.sort()
				
				nuevo=wikipedia.removeLanguageLinks(ctext, p.site())
				nuevo+=u"\n"
				
				for i in wiws:
					nuevo+=u"\n[[%s:%s]]" % (i.site().lang, i.title())
				
				if nuevo!=ctext and len(nuevo)>len(ctext)+10:
					wikipedia.showDiff(ctext, nuevo)
					page.put(nuevo, u"BOT - Updating interwikis")
				else:
					wikipedia.output(u"Los interwikis ya estan actualizados")
		except:
			pass
