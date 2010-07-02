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

import _mysql
import re
import os
import sets
import sys
import time

import wikipedia

def percent(c, d=1000):
    if c % d == 0:
        wikipedia.output(u'Llevamos %d' % c)

def loadProjects(site):
    wikipedia.output(u'Loading projects names')
    
    projects=[]
    projectsall=[]
    wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/Wikiproyectos')
    if wii.exists() and not wii.isRedirectPage():
        for trozo in wii.get().splitlines():
            trozo=trozo.strip() #re.sub(ur'(?im)^ *([^\n\r]*?) *$', ur'\1', trozo)
            trozo=re.sub(ur'(?i) *(Wikiproyecto|Wikiproject) *: *', ur'', trozo)
            trozo=re.sub('_', ' ', trozo)
            trozo=trozo.strip()
            projectsall.append(trozo)
            if trozo[0]=='#':
                continue
            if projects.count(trozo)==0:
                wikipedia.output(u'PR:%s' % trozo)
                projects.append(trozo)
        projectsall.sort()
        salida='\n'.join(projectsall)
        wii.put(salida, u'BOT - Ordenado lista de wikiproyectos y quitando repeticiones si las hay')
    return projects

def loadCategories(site, project):
    categories=[]
    categoriesall=[]
    wikipedia.output(u'Loading categories for %s project' % project)
    wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Categorías' % project)
    if wii.exists() and not wii.isRedirectPage():
        trozos=wii.get().splitlines()
        categoriesall=[]
        for trozo in trozos:
            trozo=trozo.strip()
            trozo=re.sub(ur'(?i) *(Categoría|Category) *: *', ur'', trozo)
            trozo=re.sub('_', ' ', trozo)
            if len(trozo)<1 or trozo[0]=='#':
                continue
            if categoriesall.count(trozo)==0:
                categoriesall.append(trozo)
                categories.append(trozo)
        categoriesall.sort()
        salida='\n'.join(categoriesall)
        wii.put(salida, u'BOT - Ordenado lista de categorías y quitando repeticiones si las hay')
    return categories

def loadNewPages(site, limitenuevos):
    nuevos_dic={}
    nuevos_list=[]
    newpagesgen=site.newpages(number=limitenuevos)

    for newpage in newpagesgen:
        newpagetitle=newpage[0].title()
        newpagedate=newpage[1]
        newpageuser=re.sub(ur'( \(aún no redactado\)|(Contribuciones|Contributions)\/|\" class\=\"mw\-userlink)', ur'', newpage[4])
        if not nuevos_dic.has_key(newpagetitle):
            nuevos_dic[newpagetitle]={'date':newpagedate,'user':newpageuser}
            nuevos_list.append(newpagetitle) #para conservar orden cronologico usando el indice de la list[]
    
    return nuevos_dic, nuevos_list

def loadTemplates(conn):
    #cargamos page_id y page_title para plantillas
    templates={} #nos va a hacer falta luego para las imagenes inservibles
    conn.query("SELECT page_id, page_title from page where page_namespace=10;")
    c=0
    r=conn.use_result()
    row=r.fetch_row(maxrows=1, how=1)
    while row:
        if len(row)==1:
            page_id=int(row[0]['page_id'])
            page_title=re.sub("_", " ", unicode(row[0]['page_title'], 'utf-8'))
            c+=1
            percent(c)
            templates[page_id]=page_title
        row=r.fetch_row(maxrows=1, how=1)
    print 'Cargadas %d plantillas de eswiki' % (c)
    return templates

def loadBadImages(conn, templates):
    #generamos lista de imagenes inservibles
    badimages=sets.Set()
    conn.query("SELECT il_from, il_to from imagelinks;")
    c=0
    cc=0
    r=conn.use_result()
    row=r.fetch_row(maxrows=1, how=1)
    while row:
        if len(row)==1:
            c+=1
            percent(c, 100000)
            il_from=int(row[0]['il_from'])
            try:
                il_to=re.sub('_', ' ', unicode(row[0]['il_to'], "utf-8"))
            except:
                wikipedia.output(row[0]['il_to'])
            if templates.has_key(il_from):
                badimages.add(il_to)
                cc+=1
        row=r.fetch_row(maxrows=1, how=1)
    wikipedia.output(u"%d enlaces a imágenes, %d imágenes inservibles" % (c, cc))
    return badimages

def main():
    lang="es"
    if len(sys.argv)>1:
        lang=sys.argv[1]
    
    conn = _mysql.connect(host='sql-s3', db='%swiki_p' % lang, read_default_file='~/.my.cnf')
    essite=wikipedia.Site(lang, "wikipedia")
    projects=loadProjects(essite)
    limitenuevos=2000
    [nuevos_dic, nuevos_list]=loadNewPages(essite, limitenuevos)
    templates=loadTemplates(conn)
    badimages=loadBadImages(conn, templates)
    
    for project in projects:
        print "PR:%s" % project
        categories=loadCategories(essite, project)
        
        for category in categories:
            print "  CAT:%s" % category
        
        #Recorremos CategoryLinks buscando las categorías de este wikiproyecto y capturamos los cl_from
        conn.query("SELECT cl_from, cl_to from categorylinks;")
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        projectpages=[]
        while row:
            if len(row)==1:
                cl_from=row[0]['cl_from']
                cl_to=unicode(row[0]['cl_to'], 'utf-8')
                cl_to=re.sub("_", " ", cl_to)
                
                if cl_to in categories: # Revisamos todas las categorías de este wikiproyecto
                    projectpages.append(cl_from)
                
            row=r.fetch_row(maxrows=1, how=1)
        wikipedia.output(u"Ha este wikiproyecto pertenecen %d páginas" % len(projectpages))
        
        #Inicializamos diccionario para las páginas de este wikiproyecto
        conn.query("SELECT page_id, page_title, page_len, page_namespace from page where (page_namespace=0 or page_namespace=104) and page_is_redirect=0;")
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        c=0
        wikipedia.output(u"Cargando páginas del wikiproyecto %s" % (project))
        pages={}
        pagetitle2pageid={}
        while row:
            if len(row)==1:
                page_id=int(row[0]['page_id'])
                page_title=re.sub('_', ' ', unicode(row[0]['page_title'], 'utf-8'))
                page_len=int(row[0]['page_len'])
                page_nm=int(row[0]['page_namespace'])
                page_new=False
                if nuevos_dic.has_key(page_title):
                    page_new=True
                if page_id in projectpages:
                    c+=1
                    percent(c)
                    pagetitle2pageid[page_title]=page_id
                    pages[page_id]={'t':page_title, 'l':page_len, 'nm':page_nm, 'i':0, 'c':0, 'cat':0, 'iws':0, 'im':0, 'en':0, 'f':False, 'con':False, 'rel':False, 'wik':False, 'edit':False, 'ref':False, 'obras':False, 'neutral':False, 'trad':False, 'discutido':False, 'nuevo':page_new}
            row=r.fetch_row(maxrows=1, how=1)
        
        #Plantillas de mantenimiento
        miniesbozo_pattern=re.compile(ur'(?im)^mini ?esbozo')
        esbozo_pattern=re.compile(ur'(?im)^esbozo')
        desamb_pattern=re.compile(ur'(?im)^(Des|D[ei]sambig|Desambiguaci[oó]n)$')
        destacado_pattern=re.compile(ur'(?im)^Artículo destacado$')
        bueno_pattern=re.compile(ur'(?im)^Artículo bueno$')
        fusionar_pattern=re.compile(ur'(?im)^Fusionar$')
        contextualizar_pattern=re.compile(ur'(?im)^Contextualizar$')
        sinrelevancia_pattern=re.compile(ur'(?im)^Sin ?relevancia$')
        wikificar_pattern=re.compile(ur'(?im)^Wikificar$')
        copyedit_pattern=re.compile(ur'(?im)^Copyedit$')
        sinreferencias_pattern=re.compile(ur'(?im)^(Referencias|Artículo sin fuentes|Unreferenced)$')
        enobras_pattern=re.compile(ur'(?im)^(En ?obras|En ?desarrollo)$')
        noneutral_pattern=re.compile(ur'(?im)^(NN|No ?neutral|NPOV|No ?neutralidad)$')
        traduccion_pattern=re.compile(ur'(?im)^Traducción$')
        discutido_pattern=re.compile(ur'(?im)^Discutido$')
        
        conn.query("SELECT tl_from, tl_title from templatelinks;")
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        
        c=0
        while row:
            if len(row)==1:
                tl_from=int(row [0]['tl_from'])
                tl_title=re.sub('_', ' ', unicode(row [0]['tl_title'], "utf-8"))
                if pages.has_key(tl_from):
                    c+=1
                    percent(c)
                    if re.search(destacado_pattern, tl_title):
                        pages[tl_from]['c']=1
                    elif re.search(bueno_pattern, tl_title):
                        pages[tl_from]['c']=2
                    elif re.search(esbozo_pattern, tl_title):
                        pages[tl_from]['c']=3
                    elif re.search(miniesbozo_pattern, tl_title):
                        pages[tl_from]['c']=4
                    elif re.search(desamb_pattern, tl_title):
                        pages[tl_from]['c']=5
                    #sino es ninguna de las 5 cosas, se queda el 0 que significa desconocida
                    
                    if re.search(fusionar_pattern, tl_title):
                        pages[tl_from]['f']=True
                    if re.search(contextualizar_pattern, tl_title):
                        pages[tl_from]['con']=True
                    if re.search(sinrelevancia_pattern, tl_title):
                        pages[tl_from]['rel']=True
                    if re.search(wikificar_pattern, tl_title):
                        pages[tl_from]['wik']=True
                    if re.search(copyedit_pattern, tl_title):
                        pages[tl_from]['edit']=True
                    if re.search(sinreferencias_pattern, tl_title):
                        pages[tl_from]['ref']=True
                    if re.search(enobras_pattern, tl_title):
                        pages[tl_from]['obras']=True
                    if re.search(noneutral_pattern, tl_title):
                        pages[tl_from]['neutral']=True
                    if re.search(traduccion_pattern, tl_title):
                        pages[tl_from]['trad']=True
                    if re.search(discutido_pattern, tl_title):
                        pages[tl_from]['discutido']=True
            row=r.fetch_row(maxrows=1, how=1)
        print '%d plantillas de mantenimiento en las páginas de este wikiproyecto' % (c)
        
        #Conteo de imágenes (obviando las inservibles)
        
        #Contar interwikis
        
        #Contar enlaces entrantes
        
        #Resto
        
    conn.close()

if __name__ == "__main__":
    main()
