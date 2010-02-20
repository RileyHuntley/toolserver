# -*- coding: utf-8 -*-

import re
import wikipedia
import sys
import pagegenerators
import urllib
import os

"""errors: 
http://commons.wikimedia.org/w/index.php?title=File:Backi_petrovac_map.png&diff=35687668&oldid=31253617

"""

commonswiki=wikipedia.Site("commons", "commons")

st=u"A" #start page

if (len(sys.argv)>=2):
	st=sys.argv[1]

gen=pagegenerators.AllpagesPageGenerator(start = st, namespace = 6, includeredirects = False, site = commonswiki)
pre=pagegenerators.PreloadingGenerator(gen, pageNumber=250, lookahead=250)

for page in pre:
	#print page.title()
	if not page.exists():
		continue
	
	wtext=page.get()
	if not re.search(ur"(?i)\{\{ *information", wtext):
		continue
	
	reg=ur"(?im)(?P<ini>Description *= *)(?P<desc>[^\n\r\{\/\:]+?)(?P<fin>\r\n *\| *Source *=)" # never templates
	m=re.compile(reg).finditer(wtext)
	for i in m:
		desc=i.group("desc")
		if len(desc)<100 or len(desc)>4000: #el limite de google es 5000, probar límite inferior
			break
		desc_=desc
		desc_=re.sub(ur"\[\[(?P<link>[^\]\|]+?)\]\]", ur"\g<link>", desc_)
		desc_=re.sub(ur"\[\[(?P<link>[^\]\|]+?)\|(?P<label>[^\]\|]+?)\]\]", ur"\g<label>", desc_)
		desc_=re.sub(ur" ", ur"%20", desc_)
		
		url="http://ajax.googleapis.com/ajax/services/language/detect?v=1.0&q="
		url+=desc_.encode("utf-8")
		wikipedia.output(u"=== %s ===" % page.title())
		os.system("curl -e http://es.wikipedia.org/wiki/User:Emijrp '%s' > a.txt 2> /dev/null" % url)
		
		f=open("a.txt", "r")
		raw=f.read()
		#print raw
		f.close()
		
		n=re.compile(ur'"language":"(?P<lang>[a-z]+)","isReliable":(?P<rel>true|false),"confidence":(?P<con>[0-9\.]+)\}').finditer(raw)
		for j in n:
			lang=j.group("lang")
			con=float(j.group("con"))
			rel=j.group("rel")
			if rel=="true" and con>0.8:
				wikipedia.output(u"Description: %s" % desc)
				wikipedia.output(u"Language: %s" % lang)
				
				newtext=re.sub(reg, ur"\g<ini>{{%s|\g<desc>}}\g<fin>" % lang, wtext)
				print '-'*50
				print desc_
				print '-'*50
				print "Language:", lang, "	isReliable", rel, "	Confidence", con
				print '-'*50
				wikipedia.showDiff(wtext, newtext)
				print '-'*50
				page.put(newtext, u"BOT - Adding {{%s}} to description: %s" % (lang, desc))
			break
		break
	

