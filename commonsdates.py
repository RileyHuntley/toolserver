# -*- coding: utf-8 -*-

#ideas:
#15junio2009, cuidado con las regexp tipo ddmmaaaa
#coger meses de todos los idiomas con el select html de las contribs, mirar que distintos meses en distintos idiomas no tengan en mismo nombre (colisión), hacer una versión simple que admita 12juin2009 y 12 juin 2009 y va que chuta
#hora delante de la fecha, invetir, 17:22 26 июня 2009
#para las fechas que coincida dd y mm, no pasa nada, el resto verficiar con exif?

import re, urllib, sys, time
import wikipedia, catlib, pagegenerators

commonssite=wikipedia.Site('commons', 'commons')
st=u"Es"
if (len(sys.argv)>=2):
	st=sys.argv[1]
gen=pagegenerators.AllpagesPageGenerator(start = st, namespace = 6, includeredirects = False, site = commonssite)
pre=pagegenerators.PreloadingGenerator(gen, pageNumber=250, lookahead=250)

inicio=ur"(?im)^(?P<inicio> *\| *Date *\= *)"
fin=ur"[ \.]*(?P<fin> *[\n\r\|])" #eliminamos . finales que no permiten hacer la conversión de fechas

#español
separador_es=[ur" *del? *", ur" *[\-\/\,\. ] *"] #cuidado no meter ()
month2number_es={
u"enero":u"01", u"ene":u"01", 
u"febrero":u"02", u"feb":u"02", 
u"marzo":u"03", u"mar":u"03", 
u"abril":u"04", u"abr":u"04", 
u"mayo":u"05", u"may":u"05", 
u"junio":u"06", u"jun":u"06", 
u"julio":u"07", u"jul":u"07", 
u"agosto":u"08", u"ago":u"08", u"agos":u"08", 
u"setiembre":u"09", u"septiembre":u"09", u"sep":u"09", u"sept":u"09", 
u"octubre":u"10", u"oct":u"10", 
u"noviembre":u"11", u"nov":u"11", 
u"diciembre":u"12", u"dic":u"12",
}
monthsnames_es=month2number_es.keys()
regexp_es=ur"%s(?P<change>\[?\[?(?P<day>[1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>%s)\]?\]?(?P<separator2>%s)\[?\[?(?P<year>200\d)\]?\]?)%s" % (inicio, "|".join(separador_es), "|".join(monthsnames_es), "|".join(separador_es), fin)
sub_es=ur"\g<inicio>%s-%s-%s\g<fin>"

#inglés    dd month aaaa
separador_en=[ur" *[\-\/\,\. ] *", ] #cuidado no meter ()
month2number_en={
u"january":u"01", u"jan":u"01", 
u"february":u"02", u"feb":u"02", 
u"march":u"03", u"mar":u"03", 
u"april":u"04", u"apr":u"04", 
u"may":u"05", 
u"june":u"06", u"jun":u"06", 
u"july":u"07", u"jul":u"07", 
u"august":u"08", u"aug":u"08", 
u"september":u"09", u"sep":u"09", u"sept":u"09", 
u"october":u"10", u"oct":u"10", 
u"november":u"11", u"nov":u"11", 
u"december":u"12", u"dec":u"12",
}
monthsnames_en=month2number_en.keys()
regexp_en=ur"%s(?P<change>\[?\[?(?P<day>[1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>%s)\]?\]?(?P<separator2>%s)\[?\[?(?P<year>200\d)\]?\]?)%s" % (inicio, "|".join(separador_en), "|".join(monthsnames_en), "|".join(separador_en), fin)
sub_en=ur"\g<inicio>%s-%s-%s\g<fin>"

#francés    dd month aaaa
separador_fr=[ur" *[\-\/\,\. ] *", ] #cuidado no meter ()
month2number_fr={
u"janvier":u"01",
u"février":u"02",
u"mars":u"03",
u"avril":u"04",
u"mai":u"05", 
u"juin":u"06",
u"juillet":u"07",
u"août":u"08",
u"septembre":u"09",
u"octobre":u"10",
u"novembre":u"11",
u"décembre":u"12",
}
monthsnames_fr=month2number_fr.keys()
regexp_fr=ur"%s(?P<change>\[?\[?(?P<day>[1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>%s)\]?\]?(?P<separator2>%s)\[?\[?(?P<year>200\d)\]?\]?)%s" % (inicio, "|".join(separador_fr), "|".join(monthsnames_fr), "|".join(separador_fr), fin)
sub_fr=ur"\g<inicio>%s-%s-%s\g<fin>"


#dd/mm/aaaa para dd>12
separador_ddmmaaa=[ur" *del? *", ur" *[\-\/\,\. ] *"]  #cuidado no meter ()
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
	
	if len(re.findall(regexp_es, newtext))==1: #español
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
		
		try:
			page.put(newtext, u"BOT - Normalize date format to allow localization: %s → %s" % (change, changed))
			c+=1
		except:
			pass

"""elif len(re.findall(regexp_en, newtext))==1: #ingles
		m=re.compile(regexp_en).finditer(newtext)
		
		year=month=day=u""
		for i in m:
			change=i.group("change")
			[year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
			if len(day)==1:
				day="0"+day
			break
		
		newtext=re.sub(regexp_en, sub_en % (year, month2number_en[month.lower()], day), newtext, 1)
		m=re.compile(ur"Date *\= *(?P<changed>\d{4}\-\d{2}\-\d{2})").finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	elif len(re.findall(regexp_fr, newtext))==1: #frances
		m=re.compile(regexp_fr).finditer(newtext)
		
		year=month=day=u""
		for i in m:
			change=i.group("change")
			[year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
			if len(day)==1:
				day="0"+day
			break
		
		newtext=re.sub(regexp_fr, sub_fr % (year, month2number_fr[month.lower()], day), newtext, 1)
		m=re.compile(ur"Date *\= *(?P<changed>\d{4}\-\d{2}\-\d{2})").finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break"""
