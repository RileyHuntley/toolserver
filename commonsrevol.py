# -*- coding: utf-8 -*-

#crear categoria con el nombre de la galeria, llevar a ella las categorias, y poner la galería en primer lugar con | ]]
#{{en|...}}{{de|...}} meter salto de linea
#ocultar nl http://commons.wikimedia.org/w/index.php?title=Al-Aqsa_Mosque&oldid=20753394
#añadir iws cuando no tenga, contando que el articulo ingles del mismo titulo tenga mas de X imagenes de la galeria
#sugerir imagen con descrpicion inglesa a ser posible
#coipiar defaultsort de la inglesa si el titulo coincide con el de la galeria en commons, y meterlo en la cat del mismo nombre para q se ordene en people by alphabet,

import re, urllib, sys
import wikipedia, catlib, pagegenerators

def getAllInterwikis(wtext):
	iws={}
	m=re.compile(ur"(?i)\[\[ *([a-z]{2,3}|[a-z]{2,3}\-[a-z]{2,3}) *\: *([^\]\|]+?) *\]\]").finditer(wtext)
	for i in m:
		iws[i.group(1)]=i.group(2)
	return iws

def getEnglishInterwiki(wtext):
	m=re.compile(ur"(?i)\[\[ *en *\: *([^\]\|]+) *\]\]").finditer(wtext)
	for i in m:
		return i.group(1)

def getImageTitles(wtitle, site):
	images=[]
	
	raw=site.getUrl("/w/api.php?action=query&prop=images&titles=%s&imlimit=500&format=xml" % urllib.quote(re.sub(" ", "_", wtitle).encode('utf-8')))
	m=re.compile(ur"title=\"File\:(.+?)\" \/\>").finditer(raw)
	for i in m:
		images.append(i.group(1))
	
	return images

commonssite=wikipedia.Site('commons', 'commons')
ensite=wikipedia.Site('en', 'wikipedia')
st="A"
if (len(sys.argv)>=2):
	st=sys.argv[1]
gen=pagegenerators.AllpagesPageGenerator(start = st, namespace = 0, includeredirects = False, site = commonssite)
pre=pagegenerators.PreloadingGenerator(gen, pageNumber=50, lookahead=50)

for page in pre:
	wtitle=page.title()
	wtext=newtext=page.get()
	summary="BOT -"
	eniw=getEnglishInterwiki(newtext)
	
	if not getAllInterwikis(wtext):
		wikipedia.output("=== %s ===" % wtitle)
		wikipedia.output("La galería NO tiene interwikis")
		enpage=wikipedia.Page(ensite, wtitle)
		if enpage.exists() and not enpage.isRedirectPage() and not enpage.isDisambig():
			commonsimages=getImageTitles(wtitle, commonssite)
			enimages=getImageTitles(wtitle, ensite)
			for image in enimages:
				if commonsimages.count(image)!=0:
					eniws=enpage.interwiki()
					eniws.append(enpage)
					eniws.sort()
					iws_=""
					for iw in eniws:
						iws_+="[[%s:%s]]\n" % (iw.site().lang, iw.title())
					page.put(u"%s\n\n%s" % (wtext, iws_), u"BOT - Adding %d interwiki(s) from [[:en:%s]]" % (len(eniws), enpage.title()))
					break
			continue
	#wikipedia.output("La galería tiene interwikis")
	
	
	#preparamos datos usados frecuentemente
	commonsimages=getImageTitles(wtitle, commonssite)
	#fin datos
	
	#'''wtitle'''->'''[[:lang:title|title]]'''
	"""http://commons.wikimedia.org/w/index.php?title=User_talk:Emijrp&diff=cur#Paulus_Moreelse
	if len(wtitle)>3: #por seguridad
		iws=getAllInterwikis(newtext)
		iwslist=[]
		for lang, title in iws.items():
			try:
				iwslist.append(wikipedia.Page(wikipedia.Site(lang, 'wikipedia'), title))
			except:
				pass
		iws2={}
		iwsgen = iter(iwslist)
		iwspre = pagegenerators.PreloadingGenerator(iwsgen, pageNumber = 50)
		for iw in iwspre:
			if iw.exists() and not iw.isRedirectPage() and not iw.isDisambig(): #enlazaremos aquellos que existan
				iws2[iw.site().lang]=iw.title()
		difftext=newtext
		for lang, title in iws2.items(): #enlazaremos aquellos que existan
			r_intro=ur"(?im)^\{\{ *%s *\| *(?P<ini>[^\'\[\:\|]{0,10})(?P<comillas>\'{0,3})\[?\[?(?P<name>%s|%s)\]?\]?(?P=comillas)" % (lang, title, wtitle)
			if re.search(r_intro, newtext):
				newtext=re.sub(r_intro, ur"{{%s|\g<ini>'''[[:%s:%s|\g<name>]]'''" % (lang, lang, title), newtext, 1)
		if difftext!=newtext:
			summary+=" Linking descriptions;"
	"""
	
	#sugerir imagenes
	"""difftext=newtext
	imagesource={}
	imagesource_=[]
	if len(re.findall(ur"(?i)< *gallery *>", newtext))==1 and len(commonsimages)<=5: #agregar cuando solo haya <5 imagenes?
		#buscamos imagenes en las wikipedias
		sugerencias=[]
		for lang, title in iws.items():
			tmpimages=getImageTitles(title, wikipedia.Site(lang, 'wikipedia'))
			for image in tmpimages:
				if commonsimages.count(image)==0:
					tmpsplit=wtitle.split(" ")
					for sp in tmpsplit:
						if len(sp)>=4 and re.search(ur"(?i)%s" % sp, image) and re.search(ur"(?i)\.jpe?g", image):
							sugpage=wikipedia.Page(commonssite, u"File:%s" % image)
							if sugpage.exists() and sugerencias.count(image)==0:
								sugerencias.append(image)
								imagesource[image]=u"[[:%s:%s]]" % (lang, title)
							break
		
		for sugerencia in sugerencias:
			wikipedia.output(u"Sugerencia para agregar a galería -> [[File:%s]]" % (sugerencia))
			newtext=re.sub(ur"(?im)^< */ *gallery *>", ur"File:%s\n</gallery>" % sugerencia, newtext, 1)
			if imagesource_.count(imagesource[sugerencia])==0:
				imagesource_.append(imagesource[sugerencia])
	if difftext!=newtext:
		summary+=" Adding %d image(s) from %s;" % (len(sugerencias) ,", ".join(imagesource_))
	"""
	
	#ampliar descripciones
	difftext=newtext
	r_desc=ur"(?im)^\{\{ *en *\| *\'{0,3} *\[{0,2}(\:en\:)? *%s( *\| *%s)? *\]{0,2} *\'{0,3} *\}\}" % (eniw, eniw)
	if re.search(r_desc, newtext):
		eniwpage=wikipedia.Page(wikipedia.Site('en', 'wikipedia'), eniw)
		if eniwpage.exists() and not eniwpage.isRedirectPage() and not eniwpage.isDisambig():
			m=re.compile(ur"(?im)^(\'{3,5} *%s *\'{3,5}[^\r\n\.]+?\.)[\n\r]" % (eniw)).finditer(eniwpage.get())
			for i in m:
				desc=i.group(1)
				desc=re.sub(ur"\{\{ *[^\}]+? *\}\}", ur"", desc)
				desc=re.sub(ur"\( *[^\)]+? *\)", ur"", desc)
				desc=re.sub(ur"  +", ur" ", desc)
				desc=re.sub(ur"\'{3,5} *%s *\'{3,5}" % eniw, ur"'''[[:en:%s|%s]]'''" % (eniw, eniw), desc)
				wikipedia.output(u"Descripción recomendada: %s" % desc)
				newtext=re.sub(r_desc, ur"{{en|%s}}" % desc, newtext)
				break
	if difftext!=newtext:
		summary+=" Adding description from [[:en:%s]];" % eniw
	
	#redirects
	iws=getAllInterwikis(newtext)
	redirectscandidates=[]
	redirectscandidatestitles=[]
	redirectscandidatesdic={}
	for lang, title in iws.items():
		if not re.search(ur"(?i)[^a-záéíóúàèìòùñçäëïöü ]", title):
			if redirectscandidatestitles.count(title)==0:
				redirectscandidatestitles.append(title)
				redirectscandidates.append(wikipedia.Page(wikipedia.Site(lang, 'wikipedia'), title))
				redirectscandidatesdic[title]=lang
	
	#verificamos que existen tales iws
	redirectscandidates2=[]
	for redirectcandidate in redirectscandidates:
		if redirectcandidate.exists() and not redirectcandidate.isRedirectPage() and not redirectcandidate.isDisambig():
			redirectscandidates2.append(wikipedia.Page(commonssite, redirectcandidate.title()))
	#creamos las redirects
	redgen = iter(redirectscandidates2)
	redpre = pagegenerators.PreloadingGenerator(redgen, pageNumber = 50)
	for red in redpre:
		if not red.exists():
			redtext=u"#REDIRECT [[%s]]" % wtitle
			try:
				red.put(redtext, u"BOT - Creating (%s:) redirect to [[%s]]" % (redirectscandidatesdic[red.title()], wtitle))
			except:
				pass
	
	if wtext!=newtext:
		#[[Category:wtitle| ]]
		r_catsort=ur"\[\[ *Category *\: *%s *(\| *[\!\*] *)? *\]\]" % wtitle
		if re.search(r_catsort, newtext):
			newtext=re.sub(r_catsort, "[[Category:%s| ]]" % wtitle, newtext, 1)
		
		wikipedia.output("=== %s ===" % wtitle)
		wikipedia.showDiff(wtext, newtext)
		wikipedia.output(u"Summary: %s" % summary)
		wikipedia.output(u"%s" % "#"*66)
		
		page.put(newtext, summary)
	
	
