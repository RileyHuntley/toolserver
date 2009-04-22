#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
 
import wikipedia, re, sys

esmeses=ur"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre"
enmeses=ur"January|February|March|April|May|June|July|August|September|October|November|December"

def unificar(wtext, lang, type):
	if lang=='es':
		wtext=re.sub(ur"(?im)^\* *\[\[ *(?P<diames>\d{1,2} de (%s)) *\]\] *[\-\:\–] *(?P<linea>.*?)$" % esmeses, ur"* [[\g<diames>]]: \g<linea>", wtext)
		wtext=re.sub(ur"(?i)\( *[md] *\. *\[?\[?(?P<anyo>\d{4})\]?\]? *\) *\.?", ur"(f. [[\g<anyo>]])", wtext)
		wtext=re.sub(ur"(?i)\( *[b] *\. *\[?\[?(?P<anyo>\d{4})\]?\]? *\) *\.?", ur"(n. [[\g<anyo>]])", wtext)
		if type=='daymonth':
			wtext=re.sub(ur"(?i)\( *(?P<letter>[fn]) *\. *\[?\[?(?P<anyo>\d{4})\]?\]? *\) *\.?", ur"(\g<letter>. \g<anyo>)", wtext)
	elif lang=='en':
		wtext=re.sub(ur"(?im)^\* *\[\[ *(?P<diames>(%s) \d{1,2}) *\]\] *[\-\:\–] *(?P<linea>.*?)$" % enmeses, ur"* [[\g<diames>]] - \g<linea>", wtext)
	return wtext

def extraerBiografias(wtext, regexp, lang, type):
	dic={}
	t=re.sub(ur"===", ur"", wtext).split("==")
	bio=""
	c=0
	for i in t:
		if re.search(regexp, i):
			bio=t[c+1]
		c+=1
	wikipedia.output(bio)
	m=""
	if type=='year':
		if lang=='es':
			m=re.compile(ur"(?im)^\* *\[\[ *(?P<diames>\d{1,2} de (%s)) *\]\] *[\-\:\–] *(?P<linea>\[\[(?P<nombre>[^\]\|]*?)\]\].*?)$" % esmeses).finditer(bio)
		if lang=='en':
			m=re.compile(ur"(?im)^\* *\[\[ *(?P<diames>(%s) \d{1,2}) *\]\] *[\-\:\–] *(?P<linea>\[\[(?P<nombre>[^\]\|]*?)\]\].*?)$" % enmeses).finditer(bio)
	elif type=='daymonth':
		m=re.compile(ur"(?im)^\* *\[\[ *(?P<anyo>\d{3,4}) *\]\] *[\-\:\–] *(?P<linea>\[\[(?P<nombre>[^\]\|]*?)\]\].*?)$").finditer(bio)
	
	for i in m:
		if type=='anyo':
			dic[i.group("nombre")]={'linea':i.group("linea"),'anyo':i.group("anyo")}
		elif type=='daymonth':
			dic[i.group("nombre")]={'linea':i.group("linea"),}
	
	return dic

def extraerNacimientos(text, lang, type):
	if lang=='es':
		return extraerBiografias(text, ur"(?i)nacimientos", lang, type)
	elif lang=='en':
		return extraerBiografias(text, ur"(?i)births", lang, type)

def extraerFallecimientos(text, lang, type):
	if lang=='es':
		return extraerBiografias(text, ur"(?i)fallecimientos", lang, type)
	elif lang=='en':
		return extraerBiografias(text, ur"(?i)deaths", lang, type)

#anyo=sys.argv[1]
eswiki = wikipedia.Site('es', 'wikipedia')

def mantenimiento(pagetitle, type):
	espage=wikipedia.Page(eswiki, pagetitle)
	eswtext=unificar(espage.get(), 'es', type)

	esNacDic=extraerNacimientos(eswtext, 'es', type)
	esFalDic=extraerFallecimientos(eswtext, 'es', type)

	dics={'n':esNacDic, 'f':esFalDic}
	option1={'n':'Nacidos', 'f':'Fallecidos'}
	option2={'f':'Nacidos', 'n':'Fallecidos'}
	option3={'n':'f', 'f':'n'}
	for type, dic in dics.items():
		print "Analizando... %s" % option1[type]
		for nombre, nombredic in dic.items():
			bio=wikipedia.Page(eswiki, nombre)
			if not bio.exists() or bio.isDisambig():
				continue
			if bio.isRedirectPage():
				bio=bio.getRedirectTarget()
			if not bio.exists() or bio.isDisambig():
				continue
			
			biocats=bio.categories()
			c=2
			anyoget=""
			for biocat in biocats:
				if type=='anyo':
					if re.search(ur"(?i)%s en %s" % (option1[type], pagetitle), biocat.title()):
						c-=1
				if type=='daymonth':
					if re.search(ur"(?i)%s en %s" % (option1[type], nombredic['anyo']), biocat.title()):
						c-=1
				if re.search(ur"(?i)%s en \d\d\d\d" % option2[type], biocat.title()):
					c-=1
					anyoget=biocat.title()
					anyoget=anyoget[len(anyoget)-4:len(anyoget)]
			
			if c: #no hay info en categorias, {{BD}} ?
				m=re.compile(ur"(?i)\{\{ *BD *\|(?P<birth>\d+)\|(?P<death>\d+)[\|\}]").finditer(bio.get())
				for i in m:
					if type=='n':
						anyoget=i.group("death")
					if type=='f':
						anyoget=i.group("birth")
					
			
			if not re.search(ur"\d{%s}" % len(anyoget), nombredic['linea']):
				wikipedia.output(nombre+" "+anyoget)
				linea=nombredic['linea']
				linea_=re.sub(ur"(?i)([^a-z\d])", ur"\\\1", linea) #protegemos caracteres extraños
				linea=re.sub(ur"(?im) *[\.\;\,\-\:]+ *$", ur"", linea) #quitamos punto final
				if type=='year':
					eswtext=re.sub(linea_, ur"%s (%s. [[%s]])" % (linea, option3[type], anyoget), eswtext)
				elif type=='daymonth':
					eswtext=re.sub(linea_, ur"%s (%s. %s)" % (linea, option3[type], anyoget), eswtext)

	if espage.get()!=eswtext:
		wikipedia.showDiff(espage.get(), eswtext)
		espage.put(eswtext, u"BOT - Unificando y/o añadiendo algunos años usando las biografías")

"""
for day in ['1', '2', '3',]:
	for month in [u'enero', u'febrero']:
		mantenimiento(u'%s de %s' % (day, month), 'daymonth')
"""

for anyo in range(1500, 1975):
	mantenimiento(str(anyo), 'year')



