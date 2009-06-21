# -*- coding: utf-8 -*-

import re, urllib, sys
import wikipedia, catlib, pagegenerators

commonssite=wikipedia.Site('commons', 'commons')
st=u"Es"
if (len(sys.argv)>=2):
	st=sys.argv[1]
gen=pagegenerators.AllpagesPageGenerator(start = st, namespace = 6, includeredirects = False, site = commonssite)
pre=pagegenerators.PreloadingGenerator(gen, pageNumber=250, lookahead=250)

inicio=ur"(?im)^(?P<inicio> *\| *Date *\= *)"
separador_es=[ur" *del? *", ur" *[\-\/\,\.] *"] #cuidado no meter ()
fin=ur"(?P<fin>[ \.]*[\n\r\|])"
monthsnames_es=[u"enero", u"febrero", u"marzo", u"abril", u"mayo", u"junio", u"julio", u"agosto", u"septiembre", u"octubre", u"noviembre", u"diciembre"]
month2number_es={
u"enero":u"01", 
u"febrero":u"02", 
u"marzo":u"03", 
u"abril":u"04", 
u"mayo":u"05", 
u"junio":u"06", 
u"julio":u"07", 
u"agosto":u"08", 
u"septiembre":u"09", 
u"octubre":u"10", 
u"noviembre":u"11", 
u"diciembre":u"12",
}
regexp_es=ur"%s(?P<change>\[?\[?(?P<day>[1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>%s)\]?\]?(?P<separator2>%s)\[?\[?(?P<year>200\d)\]?\]?)%s" % (inicio, "|".join(separador_es), "|".join(monthsnames_es), "|".join(separador_es), fin)
sub_es=ur"\g<inicio>%s-%s-%s\g<fin>"

#dd/mm/aaaa para dd>12
separador_common=[ur" *del? *", ur" *[\-\/\,\.] *"]  #cuidado no meter ()
regexp_common=ur"%s(?P<change>(?P<day>1[3-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>[1-9]|0[1-9]|1[0-2])(?P<separator2>%s)(?P<year>200\d))%s" % (inicio, "|".join(separador_common), "|".join(separador_common), fin)
sub_common=ur"\g<inicio>%s-%s-%s\g<fin>"

#mm/dd/aaaa para dd>12
#aaaa/mm/dd para dd>12
#aaaa/dd/mm para dd>12

#June 2007
#15.8.07 complicado http://commons.wikimedia.org/wiki/File:Schlossportal_Ringelheim.jpg

for page in pre:
	if not page.exists() or page.isRedirectPage() or page.isDisambig():
		continue
	
	wtitle=page.title()
	wtext=newtext=page.get()
	change=u""
	changed=""
	
	if len(re.findall(regexp_es, newtext))==1:
		m=re.compile(regexp_es).finditer(newtext)
		
		year=u""
		month=u""
		day=u""
		for i in m:
			change=i.group("change")
			year=i.group("year")
			month=i.group("month")
			day=i.group("day")
			if len(day)==1:
				day="0"+day
			break
		
		newtext=re.sub(regexp_es, sub_es % (year, month2number_es[month.lower()], day), newtext, 1)
		m=re.compile(ur"Date *\= *(?P<changed>\d{4}\-\d{2}\-\d{2})").finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	elif len(re.findall(regexp_common, newtext))==1:
		m=re.compile(regexp_common).finditer(newtext)
		
		year=u""
		month=u""
		day=u""
		for i in m:
			change=i.group("change")
			year=i.group("year")
			month=i.group("month")
			if len(month)==1:
				month="0"+month
			day=i.group("day")
			if len(day)==1:
				day="0"+day
			break
		
		newtext=re.sub(regexp_common, sub_common % (year, month, day), newtext, 1)
		m=re.compile(ur"Date *\= *(?P<changed>\d{4}\-\d{2}\-\d{2})").finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	
	if newtext!=wtext:
		wikipedia.showDiff(wtext, newtext)
		page.put(newtext, u"BOT - Normalize date format to allow localization: %s → %s" % (change, changed))
		