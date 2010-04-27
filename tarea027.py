#!/usr/bin/env python2.5
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

import wikipedia, re, catlib
 
essite = wikipedia.Site('es', 'wikipedia')
selfcat = wikipedia.Page(essite, u'Wikipedia:Informes automáticos/Categorías autocontenidas')
spam = u"Usando: [[Wikipedia:Informes automáticos/Categorías autocontenidas]]"

m=re.compile(ur"(?i)\[\[:(C[^\]].*?)\]\]").finditer(selfcat.get())
for i in m:
    cattitle=i.group(1)
    catpage=catlib.Category(essite, cattitle)
    
    if catpage.exists() and not catpage.isRedirectPage() and not catpage.isDisambig():
        cattitleWithout=catpage.titleWithoutNamespace()
        cattext=catpage.get()
        wikipedia.output(catpage.title())
        
        #marcamos para destruir las que no tienen artículos ni subcategorías
        if len(cattext)>=len(cattitle)+4 and len(cattext)<=len(cattitle)+10 and len(catpage.articlesList())==0 and len(catpage.subcategoriesList())==1:
            catpage.put(u'{{RobotDestruir||Categoría cíclica y sin artículos}}\n%s' % cattext, u'BOT - Marcando para destruir. Categoría cíclica y sin artículos. %s' % spam)
            continue
        
        #eliminamos el ciclo en aquellas que tienen articulos/subcategorías y una categoría válida
        if len(catpage.articlesList())!=0 or len(catpage.subcategoriesList())>1:
            c=0
            owncats=catpage.categories()
            for owncat in owncats:
                if owncat.exists():
                    c+=1
            
            if c>1:
                cattext=wikipedia.replaceExcept(cattext, ur'(?i)\[\[ *Categor(y|ía) *\: *%s[^\]]*?\]\]\n?' % cattitleWithout, ur'', exceptions=['nowiki']) #eliminamos el ciclo
                if cattext!=catpage.get():
                    catpage.put(cattext, u'BOT - Eliminando ciclo. %s' % spam)
                    continue


