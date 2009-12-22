# -*- coding: utf-8 -*-

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

#ideas:
#15junio2009, cuidado con las regexp tipo ddmmaaaa
#coger meses de todos los idiomas con el select html de las contribs, mirar que distintos meses en distintos idiomas no tengan en mismo nombre (colisión), hacer una versión simple que admita 12juin2009 y 12 juin 2009 y va que chuta
#hora delante de la fecha, invetir, 17:22 26 июня 2009
#para las fechas que coincida dd y mm, no pasa nada, el resto verficiar con exif?

import re, urllib, sys, time
import wikipedia, catlib, pagegenerators

ratelimit=15
commonssite=wikipedia.Site('commons', 'commons')
st=u"Es"
if (len(sys.argv)>=2):
	st=sys.argv[1]
gen=pagegenerators.AllpagesPageGenerator(start = st, namespace = 6, includeredirects = False, site = commonssite)
pre=pagegenerators.PreloadingGenerator(gen, pageNumber=250, lookahead=250)

inicio=ur"(?im)^(?P<inicio> *\| *Date *\= *)"
fin=ur"[ \.]*(?P<fin> *[\n\r\|])" #eliminamos . finales que no permiten hacer la conversión de fechas

#español   dd month aaaa
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
regexp_es=ur"%s(?P<change>\[?\[?(?P<day>[1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>%s)\]?\]?(?P<separator2>%s)\[?\[?(?P<year>\d{4})\]?\]?)%s" % (inicio, "|".join(separador_es), "|".join(monthsnames_es), "|".join(separador_es), fin)
sub_es=ur"\g<inicio>%s-%s-%s\g<fin>"

#inglés    dd month aaaa
separador_en=[ur" *[\-\/\,\. ] *", ur" *nd *[\.\,]? *", ur" *rd *[\.\,]? *", ur" *st *[\.\,]? *", ur" *th *[\.\,]? *"] #cuidado no meter ()
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
regexp_en=ur"%s(?P<change>\[?\[?(?P<day>[1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>%s)\]?\]?(?P<separator2>%s)\[?\[?(?P<year>\d{4})\]?\]?)%s" % (inicio, "|".join(separador_en), "|".join(monthsnames_en), "|".join(separador_en), fin)
regexp_en_monthddaaaa=ur"%s(?P<change>\[?\[?(?P<month>%s)(?P<separator1>%s)(?P<day>[1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])\]?\]?(?P<separator2>%s)\[?\[?(?P<year>\d{4})\]?\]?)%s" % (inicio, "|".join(monthsnames_en), "|".join(separador_en), "|".join(separador_en), fin)
regexp_en_monthaaaa=ur"%s(?P<change>\[?\[?(?P<month>%s)\]?\]?(?P<separator2>%s)\[?\[?(?P<year>\d{4})\]?\]?)%s" % (inicio, "|".join(monthsnames_en), "|".join(separador_en), fin)
sub_en=ur"\g<inicio>%s-%s-%s\g<fin>"
sub_en_monthaaaa=ur"\g<inicio>%s-%s\g<fin>"

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
regexp_fr=ur"%s(?P<change>\[?\[?(?P<day>[1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>%s)\]?\]?(?P<separator2>%s)\[?\[?(?P<year>\d{4})\]?\]?)%s" % (inicio, "|".join(separador_fr), "|".join(monthsnames_fr), "|".join(separador_fr), fin)
sub_fr=ur"\g<inicio>%s-%s-%s\g<fin>"

#dd/mm/aaaa para dd>12
separador_ddmmaaaa=[ur" *del? *", ur" *[\-\/\,\. ] *"]  #cuidado no meter ()
regexp_ddmmaaaa=ur"%s(?P<change>(?P<day>1[3-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>[1-9]|0[1-9]|1[0-2])(?P<separator2>%s)(?P<year>\d{4}))%s" % (inicio, "|".join(separador_ddmmaaaa), "|".join(separador_ddmmaaaa), fin)
sub_ddmmaaaa=ur"\g<inicio>%s-%s-%s\g<fin>"

#mm/dd/aaaa para dd>12
separador_mmddaaaa=[ur" *del? *", ur" *[\-\/\,\. ] *"]  #cuidado no meter ()
regexp_mmddaaaa=ur"%s(?P<change>(?P<month>[1-9]|0[1-9]|1[0-2])(?P<separator1>%s)(?P<day>1[3-9]|2[0-9]|3[0-1])(?P<separator2>%s)(?P<year>\d{4}))%s" % (inicio, "|".join(separador_mmddaaaa), "|".join(separador_mmddaaaa), fin)
sub_mmddaaaa=ur"\g<inicio>%s-%s-%s\g<fin>"


#aaaa/mm/dd para dd>12
#no tiene mucho sentido http://commons.wikimedia.org/w/index.php?title=File:0-Bullet-anatomy.svg&diff=prev&oldid=23123025
"""
separador_aaaammdd=[ur" *del? *", ur" *[\-\/\,\. ] *"]  #cuidado no meter ()
regexp_aaaammdd=ur"%s(?P<change>(?P<year>\d{4})(?P<separator1>%s)(?P<month>[1-9]|0[1-9]|1[0-2])(?P<separator2>%s)(?P<day>1[3-9]|2[0-9]|3[0-1]))%s" % (inicio, "|".join(separador_aaaammdd), "|".join(separador_aaaammdd), fin)
sub_aaaammdd=ur"\g<inicio>%s-%s-%s\g<fin>"
"""

#aaaa/dd/mm para dd>12
separador_aaaaddmm=[ur" *del? *", ur" *[\-\/\,\. ] *"]  #cuidado no meter ()
regexp_aaaaddmm=ur"%s(?P<change>(?P<year>\d{4})(?P<separator1>%s)(?P<day>1[3-9]|2[0-9]|3[0-1])(?P<separator2>%s)(?P<month>[1-9]|0[1-9]|1[0-2]))%s" % (inicio, "|".join(separador_aaaaddmm), "|".join(separador_aaaaddmm), fin)
sub_aaaaddmm=ur"\g<inicio>%s-%s-%s\g<fin>"

#15.8.07 complicado http://commons.wikimedia.org/wiki/File:Schlossportal_Ringelheim.jpg
#November 02, 2006 at 22:50 http://commons.wikimedia.org/wiki/File:Christina_Aguilera_(2006).jpg
#[[20 July]] [[2008]] http://commons.wikimedia.org/wiki/File:Kit_left_arm_black_flick.png


#{{Own}}
inicio_own=ur"(?im)^(?P<inicio> *\| *Source *\= *)"
fin_own=ur"[ \.]*(?P<fin> *[\n\r\|])" #eliminamos . finales que no permiten hacer la conversión
#CUIDADO con own photograph! http://commons.wikimedia.org/w/index.php?title=File:Teatro_Coccia_chandelier.jpg&diff=next&oldid=19903214
#ideas: own photo, own photograph
own_synonym=[ur"own[ \-]*work", ur"self[ \-]*made", ur"eie[ \-]*werk", ur"Treballo de qui la cargó", ur"Trabayu propiu", ur"Уласны твор", ur"Собствена творба", ur"Vlastito djelo", ur"Treball propi", ur"Vlastní dílo", ur"Eget arbejde", ur"Eigene Arbeit", ur"Propra verko", ur"Trabajo propio", ur"self[ \-]*made *\/ *foto propia", ur"Üleslaadija oma töö", ur"Oma teos", ur"Travail personnel", ur"Traballo propio", ur"Vlastito djelo postavljača", ur"A feltöltő saját munkája", ur"Karya sendiri", ur"Opera propria", ur"Opus proprium", ur"Mano darbas", ur"Egen Wark", ur"Eigen waark", ur"Eigen werk", ur"Eget arbeide", ur"Trabalh personal", ur"Ejen Woakj", ur"Praca własna", ur"Trabalho próprio", ur"Operă proprie", ur"Vlastné dielo", ur"Lastno delo", ur"Eget arbete", ur"Sariling gawa"] #no meter  ()
regexp_own=ur"%s(?P<change>\[?\[?(%s)\]?\]?)%s" % (inicio_own, "|".join(own_synonym), fin_own)
sub_own=ur"\g<inicio>{{Own}}\g<fin>"

#== Licensing ==
inicio_lic=ur"" #noseusade momento
fin_lic=ur"(?P<fin> *[\n\r])"
lic_synonym=[ur"Licensing", ur"License", ur"\[\[Commons\:Copyright tags\|Licensing\]\]", ur"Licencia", ur"Lizenz", ur"Licence", ur"Licencja", ur"Licença", ur"ライセンス", ur"Лицензирование", ur"Licencado", ur"ترخيص", ur"\[\[Commons\:Copyright tags\|ترخيص\]\]", ur"Licenţiere", ur"Licenza", ur"Licenza d\'uso", ur"Licentie", ur"Llicència", ur"Licenc", ur"Lisenssi", ur"\[\[COM\:TOM\|Lisenssi\]\]"]  #no meter  ()
regexp_lic=ur"(?im)^%s(?P<h1>\=\=) *(?P<change>\[?\[?(%s)\]?\]? *\:?) *(?P<h2>\=\=)%s" % (inicio_lic, "|".join(lic_synonym), fin_lic)
sub_lic=ur"\g<h1> {{int:license}} \g<h2>\g<fin>"

#== Summary ==
inicio_sum=ur"" #noseusade momento
fin_sum=ur"(?P<fin> *[\n\r])"
sum_synonym=[ur"Summary", ur"Sumario", ur"Beschreibung", ur"Description", ur"Opis", ur"Descrição do ficheiro", ur"Beskrivning", ur"Dettagli", ur"ファイルの概要", ur"Beschrijving", ur"Краткое описание", ur"ملخص", ur"Resum", ur"Popis", ur"Resumo", ur"Beskrivelse", ur"Összegzés", ur"Beskrivelse", ur"Yhteenveto", ur"Descriere fişier", ur"Σύνοψη"]
regexp_sum=ur"(?im)^%s(?P<h1>\=\=) *(?P<change>\[?\[?(%s)\]?\]? *\:?) *(?P<h2>\=\=)%s" % (inicio_sum, "|".join(sum_synonym), fin_sum)
sub_sum=ur"\g<h1> {{int:filedesc}} \g<h2>\g<fin>"

c=0
t1=time.time()
regexp_changed=ur"(?m)^ *\| *Date *\= *(?P<changed>\d{4}\-\d{2}\-\d{2})"
regexp_changed_aaaamm=ur"(?m)^ *\| *Date *\= *(?P<changed>\d{4}\-\d{2})"
regexp_changed_own=ur"(?m)^ *\| *Source *\= *(?P<changed>\{\{Own\}\})"
regexp_changed_lic=ur"(?m)^\=+ *(?P<changed>\{\{int:license\}\}) *\=+"
regexp_changed_sum=ur"(?m)^\=+ *(?P<changed>\{\{int:filedesc\}\}) *\=+"
for page in pre:
	if not page.exists() or page.isRedirectPage() or page.isDisambig():
		continue
	
	wtitle=page.title()
	wtext=newtext=page.get()
	
	if re.search(ur"(?i)(\{\{ *User\:Tivedshambo\/Information|\<nowiki\>)", wtext): #http://commons.wikimedia.org/wiki/User_talk:Emijrp
		#nowiki para evitar historiales 
		continue
	
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
		m=re.compile(regexp_changed).finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	elif len(re.findall(regexp_en, newtext))==1: #ingles
		m=re.compile(regexp_en).finditer(newtext)
		
		year=month=day=u""
		for i in m:
			change=i.group("change")
			[year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
			if len(day)==1:
				day="0"+day
			break
		
		newtext=re.sub(regexp_en, sub_en % (year, month2number_en[month.lower()], day), newtext, 1)
		m=re.compile(regexp_changed).finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	elif len(re.findall(regexp_en_monthddaaaa, newtext))==1: #ingles regexp_en_monthddaaaa
		m=re.compile(regexp_en_monthddaaaa).finditer(newtext)
		
		year=month=day=u""
		for i in m:
			change=i.group("change")
			[year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
			if len(day)==1:
				day="0"+day
			break
		
		newtext=re.sub(regexp_en_monthddaaaa, sub_en % (year, month2number_en[month.lower()], day), newtext, 1)
		m=re.compile(regexp_changed).finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	elif len(re.findall(regexp_en_monthaaaa, newtext))==1: #ingles regexp_en_monthaaaa
		m=re.compile(regexp_en_monthaaaa).finditer(newtext)
		
		year=month=u""
		for i in m:
			change=i.group("change")
			[year, month]=[i.group("year"), i.group("month")]
			break
		
		newtext=re.sub(regexp_en_monthaaaa, sub_en_monthaaaa % (year, month2number_en[month.lower()]), newtext, 1)
		m=re.compile(regexp_changed_aaaamm).finditer(newtext)
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
			break
	elif len(re.findall(regexp_ddmmaaaa, newtext))==1:
		m=re.compile(regexp_ddmmaaaa).finditer(newtext)
		
		year=month=day=u""
		for i in m:
			change=i.group("change")
			[year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
			if len(month)==1:
				month="0"+month
			if len(day)==1: #nunca deberia entrar aqui
				day="0"+day
			break
		
		newtext=re.sub(regexp_ddmmaaaa, sub_ddmmaaaa % (year, month, day), newtext, 1)
		m=re.compile(regexp_changed).finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	elif len(re.findall(regexp_mmddaaaa, newtext))==1:
		m=re.compile(regexp_mmddaaaa).finditer(newtext)
		
		year=month=day=u""
		for i in m:
			change=i.group("change")
			[year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
			if len(month)==1:
				month="0"+month
			if len(day)==1: #nunca deberia entrar aqui
				day="0"+day
			break
		
		newtext=re.sub(regexp_mmddaaaa, sub_mmddaaaa % (year, month, day), newtext, 1)
		m=re.compile(regexp_changed).finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	elif len(re.findall(regexp_aaaaddmm, newtext))==1:
		m=re.compile(regexp_aaaaddmm).finditer(newtext)
		
		year=month=day=u""
		for i in m:
			change=i.group("change")
			[year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
			if len(month)==1:
				month="0"+month
			if len(day)==1: #nunca deberia entrar aqui
				day="0"+day
			break
		
		newtext=re.sub(regexp_aaaaddmm, sub_aaaaddmm % (year, month, day), newtext, 1)
		m=re.compile(regexp_changed).finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break
	
	#{{Own}}
	change_own=u""
	changed_own=u""
	if True or newtext!=wtext:
		if len(re.findall(regexp_own, newtext))==1:
			m=re.compile(regexp_own).finditer(newtext)
			
			for i in m:
				change_own=i.group("change")
				break
			
			newtext=re.sub(regexp_own, sub_own, newtext, 1)
			m=re.compile(regexp_changed_own).finditer(newtext)
			for i in m:
				changed_own=i.group("changed")
				break
	
	#== {{int:license}} ==
	change_lic=u""
	changed_lic=u""
	"""if True or newtext!=wtext:
		if len(re.findall(regexp_lic, newtext))==1:
			m=re.compile(regexp_lic).finditer(newtext)
			
			for i in m:
				change_lic=i.group("change")
				break
			
			newtext=re.sub(regexp_lic, sub_lic, newtext, 1)
			m=re.compile(regexp_changed_lic).finditer(newtext)
			for i in m:
				changed_lic=i.group("changed")
				break
	"""
	#== {{int:filedesc}} ==
	change_sum=u""
	changed_sum=u""
	"""if True or newtext!=wtext:
		if len(re.findall(regexp_sum, newtext))==1:
			m=re.compile(regexp_sum).finditer(newtext)
			
			for i in m:
				change_sum=i.group("change")
				break
			
			newtext=re.sub(regexp_sum, sub_sum, newtext, 1)
			m=re.compile(regexp_changed_sum).finditer(newtext)
			for i in m:
				changed_sum=i.group("changed")
				break
	"""
	if newtext!=wtext:
		wikipedia.showDiff(wtext, newtext)
		if c>=ratelimit:
			while time.time()-t1<60:
				time.sleep(0.1)
			t1=time.time()
			c=0
		
		try:
			summary=u"BOT - Changes to allow localization:"
			if changed:
				summary+=u" %s → %s;" % (change, changed)
			if changed_own:
				summary+=u" %s → %s;" % (change_own, changed_own)
			if changed_lic:
				summary+=u" %s → %s;" % (change_lic, changed_lic)
			if changed_sum:
				summary+=u" %s → %s;" % (change_sum, changed_sum)
			
			page.put(newtext, summary)
			c+=1
		except:
			pass

"""elif len(re.findall(regexp_aaaammdd, newtext))==1:
		m=re.compile(regexp_aaaammdd).finditer(newtext)
		
		year=month=day=u""
		for i in m:
			change=i.group("change")
			[year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
			if len(month)==1:
				month="0"+month
			if len(day)==1: #nunca deberia entrar aqui
				day="0"+day
			break
		
		newtext=re.sub(regexp_aaaammdd, sub_aaaammdd % (year, month, day), newtext, 1)
		m=re.compile(regexp_changed).finditer(newtext)
		for i in m:
			changed=i.group("changed")
			break"""
