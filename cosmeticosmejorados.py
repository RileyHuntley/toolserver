#!/usr/bin/python
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

import wikipedia, pagegenerators, re, sys, time

def eliminaTripleSaltos(newtext):
	lineas=newtext.splitlines()
	c=t=0
	newtext=''
	for linea in lineas:
		t+=1
		if linea:
			newtext+=linea
			if t<len(lineas):
				newtext+='\n'
			c=0
		else:
			c+=1
			if c<=1:
				newtext+='\n'
	return newtext

def separaSecciones(newtext):
	
	
	return newtext

def eliminaEspaciosInnecesarios(newtext):
	newtext=re.sub(ur'(?i)\[\[ *(?!Categor(y|ía) *\:)(?P<art>[^\|\]]*?) *\| *(?P<label>[^\|\]]*?) *\]\]', ur'[[\g<art>|\g<label>]]', newtext) #no espacios en [[   gggg  | hhh ]], evita los [[Categoría:iajasd| ]]
	newtext=re.sub(ur'(?i)\[\[ *(?P<art>[^\|\]]*?) *\| *\g<art> *\]\]', ur'[[\g<art>]]', newtext) #no repeticiones  [[blabla|blabla]]s
	newtext=re.sub(ur'(?i)\[\[ *(?P<art>[^\|\]]*?) *\]\]', ur'[[\g<art>]]', newtext) #no espacios en enlaces [[   simples ]]
	newtext=re.sub(ur'(?im)^(?P<seccion>=+[^=]*?=+) *$', ur'\g<seccion>', newtext) #no espacios en == ssss ===     .
	newtext=re.sub(ur'(?im)^(?P<lista>[\#\*]+) *', ur'\g<lista> ', newtext) #separacion entre # y el item
	
	return newtext

def insertaEspacios(newtext):
	newtext=re.sub(ur'(?P<pre> [a-z]{2,})\. *(?P<post>[A-Z][a-z]+ )', ur'\g<pre>. \g<post>', newtext) #despues de punto, espacio
	newtext=re.sub(ur'(?im)^(?P<lista>[\#\*]+)(?P<item>[^ \*\#])', ur'\g<lista> \g<item>', newtext) #separacion entre # y el item
	
	return newtext

def justificarParametros(newtext, templatesWithParams):
	
	#print templatesWithParams
	
	for template in templatesWithParams:
		templateName=template[0]
		templateParams={}
		maxlen=0
		for param in template[1]:
			param=re.sub(ur'[\r\n]', ur'', param)
			trozos=param.split('=')
			param=trozos[0]
			value=''
			if len(trozos)>1:
				value='='.join(trozos[1:])
			param=param.strip()
			value=value.strip()
			if param:
				templateParams[param]=value
			if maxlen<len(param):
				maxlen=len(param)
		#print templateParams.items()
		newtext=re.sub(ur'(?im)\{\{ *(?P<templatename>%s) *\|? *\r' % templateName, ur'{{\g<templatename>\r', newtext) #
		for param, value in templateParams.items(): #justificación de parámetros
			newtext=re.sub(ur'(?m)^ *\|? *(?P<param>%s) *\= *(?P<value>.*?) *\|? *\r' % param, ur'| \g<param>%s = \g<value>\r' % (' '*(maxlen-len(param))), newtext)
	
	return newtext

def cambiosTesteados(newtext, cambiostesteados):
	for k, v in cambiostesteados.items():
		newtext=re.sub(k, v, newtext)
	return newtext

cambiostesteados={

#secciones segun manual de estilo
ur'(?im)=(\s*)(v[íi]nculos?\s*e[xs]ternos?|l[íi]gas?\s*e[xs]tern[oa]s?|l[íi]nks?\s*e[xs]tern[oa]s?|enla[cs]es\s*e[xs]ternos|external\s*links?)(\s*)=': ur'=\1Enlaces externos\3=', #unificar EE
ur'(?im)=(\s*)([vb]er\s*tam[bv]i[ée]n|[vb][ée]a[cs]e\s*t[aá]mbi[ée]n|vea\s*tambi[eé]n|\{\{ver\}\})(\s*)=': ur'=\1Véase también\3=', #unificar VT
ur'(?im)=(\s*)(references)(\s*)=': ur'=\1Referencias\3=', #unificar sección referencias
ur'(?im)=(\s*)\'{3}([^\'\=]*?)\'{3}(\s*)=': ur'=\1\2\3=', #quitar negritas de secciones (debe ir despues de unificar los nombres de secciones)
#evitar toda la sección en mayúscula?

#categorias
ur'(?im)^ *\[\[ *Categor(y|ía) *\: *': ur'[[Categoría:', #unificar namespace 14
ur'(?im)\]\] *\[\[ *Categor(y|ía) *\: *': ur']]\n[[Categoría:', #separar categorías en lineas distintas
ur'(?i)\[\[ *Categor(y|ía) *\: *(?P<cat>[^\|\]]*?)\| *\! *\]\]': ur'[[Categoría:\g<cat>| ]]', #orden en categorías
#primera letra de la categoría en mayúscula

#archivo:
ur'(?i)\[\[ *(?P<dospuntos>\:?) *(File|Imagen?) *\: *': ur'[[\g<dospuntos>Archivo:', #thumbs o enlaces directos
ur'(?im)^(File|Imagen?) *\: *': ur'Archivo:', #en galerías

#meter punto final en los pie de fotos (cuidado, puede haber saltos de linea en los pies)

#[[html://
ur'(?i)\[\[ *(?P<url>(ftp|http)s?\:\/\/[^\]]*?) *\]\]': ur'[\g<url>]',

#caracteres
ur'<sup>1</sup>': ur'¹',
ur'<sup>2</sup>': ur'²',
ur'<sup>3</sup>': ur'³',

#Página Web Oficial, Web Oficial

#webs
ur'(?i)\[\[myspace\]\]': ur'[[MySpace]]',
ur'(?i)\[\[youtube\]\]': ur'[[YouTube]]',

#en inglés, en francés, en ucraniano
ur'(?im)\[ *(?P<url>(ftp|http)s?\:\/\/[^\]]*?) *\(? *(en)? *(?P<idioma>inglés|francés|italiano|portugués|ruso|ucraniano) *\)? *\]$': ur'[\g<url>] (en \g<idioma>)',

#cosas que sobran
ur'(?im)^ *\| *\}\}': ur'}}',

#html
ur'(?i)< *br */ *>': ur'<br />',

}

st='A'
if len(sys.argv)>=2:
	st=sys.argv[1]

gen=pagegenerators.AllpagesPageGenerator(start=st, namespace=0, includeredirects=False, site=wikipedia.Site('es', 'wikipedia'))
preloadingGen=pagegenerators.PreloadingGenerator(gen, pageNumber=33, lookahead=33)

for page in preloadingGen:
	if page.isRedirectPage() or page.isDisambig():
		pass
	else:
		wtitle=page.title()
		wtext=newtext=page.get()
		
		newtext=justificarParametros(newtext, page.templatesWithParams())
		"""
		#newtext=organizarParametrosArchivo()
		#newtext=organizarEnlacesExternos()
		#newtext=primeraOcurrenciaTítulo()
		"""
		if wtext!=newtext:
			newtext=eliminaTripleSaltos(newtext)
			newtext=separaSecciones(newtext)
			newtext=cambiosTesteados(newtext, cambiostesteados)
			newtext=eliminaEspaciosInnecesarios(newtext)
			newtext=insertaEspacios(newtext)
			
			wikipedia.output(u'%s###### %s ######' % ('\n'*5, wtitle))
			wikipedia.showDiff(wtext, newtext)
			page.put(newtext, u'BOT - Justificando parámetros')
			time.sleep(10)
	
