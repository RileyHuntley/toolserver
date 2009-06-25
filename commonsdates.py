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
fin=ur"[ \.]*(?P<fin> *[\n\r\|])" #eliminamos . finales que no permiten hacer la conversión de fechas
month2number_es={
u"enero":u"01", 
u"ene":u"01", 
u"febrero":u"02", 
u"feb":u"02", 
u"marzo":u"03", 
u"mar":u"03", 
u"abril":u"04", 
u"abr":u"04", 
u"mayo":u"05", 
u"may":u"05", 
u"junio":u"06", 
u"jun":u"06", 
u"julio":u"07", 
u"jul":u"07", 
u"agosto":u"08", 
u"ago":u"08", 
u"agos":u"08", 
u"septiembre":u"09", 
u"sep":u"09", 
u"sept":u"09", 
u"octubre":u"10", 
u"oct":u"10", 
u"noviembre":u"11", 
u"nov":u"11", 
u"diciembre":u"12",
u"dic":u"12",
}
monthsnames_es=[]
for k, v in month2number_es.items():
	monthsnames_es.append(k)
regexp_es=ur"%s(?P<change>\[?\[?(?P<day>[1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>%s)\]?\]?(?P<separator2>%s)\[?\[?(?P<year>200\d)\]?\]?)%s" % (inicio, "|".join(separador_es), "|".join(monthsnames_es), "|".join(separador_es), fin)
sub_es=ur"\g<inicio>%s-%s-%s\g<fin>"

#dd/mm/aaaa para dd>12
separador_ddmmaaa=[ur" *del? *", ur" *[\-\/\,\.] *"]  #cuidado no meter ()
regexp_ddmmaaa=ur"%s(?P<change>(?P<day>1[3-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>[1-9]|0[1-9]|1[0-2])(?P<separator2>%s)(?P<year>200\d))%s" % (inicio, "|".join(separador_ddmmaaa), "|".join(separador_ddmmaaa), fin)
sub_ddmmaaa=ur"\g<inicio>%s-%s-%s\g<fin>"

#mm/dd/aaaa para dd>12
#aaaa/mm/dd para dd>12
#aaaa/dd/mm para dd>12

#June 2007
#15.8.07 complicado http://commons.wikimedia.org/wiki/File:Schlossportal_Ringelheim.jpg
#13-jun-2009 http://commons.wikimedia.org/wiki/File:Ascenso1-minotauro.JPG
#November 02, 2006 at 22:50 http://commons.wikimedia.org/wiki/File:Christina_Aguilera_(2006).jpg
#[[20 July]] [[2008]] http://commons.wikimedia.org/wiki/File:Kit_left_arm_black_flick.png

c=0
t1=time.time()
for page in pre:
	if not page.exists() or page.isRedirectPage() or page.isDisambig():
		continue
	
	wtitle=page.title()
	wtext=newtext=page.get()
	change=u""
	changed=""
	
	if len(re.findall(regexp_es, newtext))==1:
		m=re.compile(regexp_es).finditer(newtext)
		
		year=month=day=u""
		for i in m:
			change=i.group("change")
			[year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
			if len(day)==1:
				day="0"+day
			break
		
		newtext=re.sub(regexp_es, sub_es % (year, month2number_es[month.lower()], day), newtext, 1)
		m=re.compile(ur"Date *\= *(?P<changed>\d{4}\-\d{2}\-\d{2})").finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	elif len(re.findall(regexp_ddmmaaa, newtext))==1:
		m=re.compile(regexp_ddmmaaa).finditer(newtext)
		
		year=month=day=u""
		for i in m:
			change=i.group("change")
			[year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
			if len(month)==1:
				month="0"+month
			if len(day)==1: #nunca deberia entrar aqui
				day="0"+day
			break
		
		newtext=re.sub(regexp_ddmmaaa, sub_ddmmaaa % (year, month, day), newtext, 1)
		m=re.compile(ur"Date *\= *(?P<changed>\d{4}\-\d{2}\-\d{2})").finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	
	if newtext!=wtext:
		wikipedia.showDiff(wtext, newtext)
		if c>=10:
			while time.time()-t1<60:
				time.sleep(0.1)
			t1=time.time()
			c=0
		c+=1
		page.put(newtext, u"BOT - Normalize date format to allow localization: %s → %s" % (change, changed))
		