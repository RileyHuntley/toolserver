# -*- coding: utf-8 -*-

import re, urllib, sys, time
import wikipedia, catlib, pagegenerators

ensite=wikipedia.Site('en', 'wikipedia')
st=u"A"
if (len(sys.argv)>=2):
	st=sys.argv[1]
gen=pagegenerators.AllpagesPageGenerator(start = st, namespace = 0, includeredirects = False, site = ensite)
pre=pagegenerators.PreloadingGenerator(gen, pageNumber=250, lookahead=250)

c=0
t1=time.time()
for page in pre:
	wtitle=page.title()
	if not page.exists() or page.isRedirectPage() or page.isDisambig():
		continue
	else:
		if re.search(ur"[^a-zA-Z ]", wtitle):
			continue
		elif len(wtitle.split(" "))>=3:
			trozos=wtitle.split(" ")
			min=may=False
			
			for i in trozos[1:]:
				imay=i.upper()
				imin=i.lower()
				if imay[0]==i[0]:#primer caracter comprobar
					may=True
				if imin[0]==i[0]:
					min=True
			
			if min and may:
				#crear redirect con todo en minusculas
				wiii=wikipedia.Page(ensite, wtitle.lower())
				if not wiii.exists():
					if c>=10:
						while time.time()-t1<60:
							time.sleep(0.1)
						t1=time.time()
						c=0
					c+=1
					wiii.put(u"#REDIRECT [[%s]] {{R from other capitalisation}}" % wtitle, u"BOT - Creating redirect to [[%s]]" % wtitle)
				else:
					wikipedia.output(u"Ya existe el redirect")
