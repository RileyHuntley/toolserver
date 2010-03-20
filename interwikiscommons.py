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
import re, sys, urllib

def getAllInterwikis(wtext):
	iws={}
	m=re.compile(ur"(?i)\[\[ *([a-z]{2,3}|[a-z]{2,3}\-[a-z]{2,3}) *\: *([^\]\|]+?) *\]\]").finditer(wtext)
	for i in m:
		iws[i.group(1)]=i.group(2)
	return iws

def getEnglishInterwiki(wtext):
	iws=getAllInterwikis(wtext)
	if iws.has_key("en"):
		return iws["en"]
	else:
		return ""

def getImageTitles(wtitle, site):
	images=[]
	
	raw=site.getUrl("/w/api.php?action=query&prop=images&titles=%s&imlimit=500&format=xml" % urllib.quote(re.sub(" ", "_", wtitle).encode('utf-8')))
	m=re.compile(ur"title=\"File\:(?P<filename>.+?)\" \/\>").finditer(raw)
	for i in m:
		images.append(i.group("filename"))
	
	return images

st='A'
if len(sys.argv)>=2:
	st=sys.argv[1]

commons=wikipedia.Site('commons', 'commons')
commonssite=wikipedia.Site('commons', 'commons')
ensite=wikipedia.Site('en', 'wikipedia')
wikipediaen=wikipedia.Site('en', 'wikipedia')
gen=pagegenerators.AllpagesPageGenerator(start=st, namespace=0, includeredirects=False, site=commons)
preloadingGen=pagegenerators.PreloadingGenerator(gen, pageNumber=100, lookahead=100)
 
for page in preloadingGen:
	if page.isRedirectPage() or page.isDisambig():
		continue
	else:
		if not getAllInterwikis(page.get()):
			wtitle=page.title()
			wtext=newtext=page.get()
			summary="BOT -"
			eniw=getEnglishInterwiki(newtext)
			wikipedia.output("=== %s ===" % wtitle)
			wikipedia.output("La galería NO tiene interwikis")
			enpage=wikipedia.Page(ensite, wtitle)
			if enpage.exists() and not enpage.isRedirectPage() and not enpage.isDisambig():
				commonsimages=getImageTitles(wtitle, commonssite)
				enimages=getImageTitles(wtitle, ensite)
				for image in enimages:
					if commonsimages.count(image)!=0: #con que una imagen coincida, ya vale
						eniws=enpage.interwiki()
						eniws.append(enpage)
						eniws.sort()
						iws_=""
						for iw in eniws:
							iws_+="[[%s:%s]]\n" % (iw.site().lang, iw.title())
						page.put(u"%s\n\n%s" % (wtext, iws_), u"BOT - Adding %d interwiki(s) from [[:en:%s]]" % (len(eniws), enpage.title()))
						break
				continue
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
