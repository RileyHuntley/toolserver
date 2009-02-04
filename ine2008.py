#!/usr/bin/python
# -*- coding: utf-8  -*-

#los datos que necesita vienen de  http://www.ine.es/pob_xls/pobmun08.xls separados por ;
import wikipedia, pagegenerators, re, sys, time

codigos={
'01':u'Álava',
'02':u'Albacete',
'03':u'Alicante',
'04':u'Almería',
'05':u'Ávila',
'06':u'Badajoz',
'07':u'Islas Baleares',
'08':u'Barcelona',
'09':u'Burgos',
'10':u'Cáceres',
'11':u'Cádiz',
'12':u'Castellón',
'13':u'Ciudad Real',
'14':u'Córdoba',
'15':u'La Coruña',
'16':u'Cuenca',
'17':u'Gerona',
'18':u'Granada',
'19':u'Guadalajara',
'20':u'Guipúzcoa',
'21':u'Huelva',
'22':u'Huesca',
'23':u'Jaén',
'24':u'León',
'25':u'Lérida',
'26':u'La Rioja',
'27':u'Lugo',
'28':u'Madrid',
'29':u'Málaga',
'30':u'Murcia',
'31':u'Navarra',
'32':u'Orense',
'33':u'Asturias',
'34':u'Palencia',
'35':u'Las Palmas',
'36':u'Pontevedra',
'37':u'Salamanca',
'38':u'Santa Cruz de Tenerife',
'39':u'Cantabria',
'40':u'Segovia',
'41':u'Sevilla',
'42':u'Soria',
'43':u'Tarragona',
'44':u'Teruel',
'45':u'Toledo',
'46':u'Valencia',
'47':u'Valladolid',
'48':u'Vizcaya',
'49':u'Zamora',
'50':u'Zaragoza',
}

def ine2008(page, nombre, cpro, pob08):
	if page.isRedirectPage():
		page=page.getRedirectTarget()
	if page.exists() and not page.isRedirectPage():
		wtext=newtext=page.get()
		wtitle=page.title()
		if re.search(ur'cod_provincia *= *%s' % cpro, wtext):
			newtext=re.sub(ur'(?m)^(?P<ineano> *\|? *ine_año *= *)\d{4}', ur'\g<ineano>2008', newtext)
			newtext=re.sub(ur'(?m)^(?P<pob> *\|? *población *= *)[\d\.\,]*', ur'\g<pob>%s' % pob08, newtext)
			
			if newtext!=wtext:
				wikipedia.output(u'---> %s <---' % wtitle)
				wikipedia.showDiff(wtext, newtext)
				page.put(newtext, u'BOT - Actualizando cifras de población según INE 2008')
				return True, page
	return False, page

eswiki=wikipedia.Site('es', 'wikipedia')

f=open('ine2008.txt', 'r')
g=open('ine2008noencontrados.txt', 'w')

for l in f:
	l=unicode(l, 'utf-8')
	
	t=l.split(';')
	cpro=t[0]
	provincia=t[1]
	cmun=t[2]
	nombre=t[3]
	nombre=nombre.split('/')[0] #evitamos Alicante/Alicant
	nombre=re.sub(ur'(.*?) \((.*?)\)', ur'\2 \1', nombre)
	
	pob08=re.sub('[\.\s]', '', t[4])
	
	page=wikipedia.Page(eswiki, nombre)
	actualizado=False
	if page.exists():
		[actualizado, page]=ine2008(page, nombre, cpro, pob08)
		red=wikipedia.Page(eswiki, '%s (%s)' % (nombre, codigos[cpro]))
		if not red.exists():
			red.put('#REDIRECT [[%s]]' % page.title(), 'BOT - #REDIRECT [[%s]]' % page.title())
	else:
		page=wikipedia.Page(eswiki, '%s (%s)' % (nombre, codigos[cpro]))
		if page.exists():
			[actualizado, page]=ine2008(page, nombre, cpro, pob08)
	
	if not actualizado:
		salida='%s, %s no se ha actualizado;\n' % (nombre, provincia)
		g.write(salida.encode('utf-8'))

f.close()
g.close()
