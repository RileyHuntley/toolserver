# -*- coding: utf-8 -*-

from __future__ import generators
import sys, re
import wikipedia, pagegenerators,catlib, config
import urllib, time

#u'Acontecimientos futuros', u'Actualidad', u'Wikipedia:Artículos con enlaces externos rotos', u'Wikipedia:Artículos demasiado complejos', u'Wikipedia:Artículos en desarrollo', u'Wikipedia:Artículos que necesitan referencias', u'Wikipedia:Artículos con secciones para expandir', u'Wikipedia:Borrar (definitivo)', u'Wikipedia:Borrar (en consulta)', u'Wikipedia:Categorías para borrar', u'Wikipedia:Plagios obvios', u'Wikipedia:Trasladar a Anexos', u'Wikipedia:Trasladar a Wikcionario', u'Wikipedia:Trasladar a Wikilibros', u'Wikipedia:Trasladar a Wikinoticias', u'Wikipedia:Trasladar a Wikiquote', u'Wikipedia:Trasladar a Wikisource', u'Wikipedia:Traducción automática', u'Wikipedia:Copyedit', u'Wikipedia:Wikificar', u'Wikipedia:Veracidad discutida', u'Wikipedia:Fusionar', u'Wikipedia:Fusiones discutidas', u'Wikipedia:Sin relevancia aparente'

resultado=[]
for i in [u'Acontecimientos futuros', u'Actualidad', u'Wikipedia:Artículos con enlaces externos rotos', u'Wikipedia:Artículos demasiado complejos', u'Wikipedia:Artículos en desarrollo', u'Wikipedia:Artículos que necesitan referencias', u'Wikipedia:Artículos con secciones para expandir', u'Wikipedia:Borrar (definitivo)', u'Wikipedia:Borrar (en consulta)', u'Wikipedia:Plagios obvios', u'Wikipedia:Trasladar a Wikcionario', u'Wikipedia:Trasladar a Wikilibros', u'Wikipedia:Trasladar a Wikinoticias', u'Wikipedia:Trasladar a Wikiquote', u'Wikipedia:Trasladar a Wikisource', u'Wikipedia:Traducción automática', u'Wikipedia:Copyedit', u'Wikipedia:Wikificar', u'Wikipedia:Veracidad discutida', u'Wikipedia:Fusionar', u'Wikipedia:Fusiones discutidas', u'Wikipedia:Sin relevancia aparente']:
	cat=catlib.Category(wikipedia.Site("es", "wikipedia"), u"Category:%s" % i)
	l=[]
	cont=0
	
	try:
		if i!=u'Wikipedia:Categorías para borrar' and i!=u'Wikipedia:Borrar (definitivo)':
			l=cat.articles()
		else:
			iiii=0
			#l=cat.subcategories()
	except:
		wikipedia.output(u"%s" % str(cont))
		resultado.append(cont)
		continue
	
	for j in l:
		cont+=1
	wikipedia.output(u"%s" % str(cont))
	resultado.append(cont)

salida=u"{{subst:Plantilla:TablaMantenimiento/subst"
for i in resultado:
	salida+=u"|%s" % str(i)
salida+=u"}}<noinclude>{{documentación de plantilla}}</noinclude>"

wiii = wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Plantilla:TablaMantenimiento")
wiii.put(u"%s" % salida, u"BOT - Actualizando plantilla")

