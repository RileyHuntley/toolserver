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
import sys
import time

import wikipedia

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

def main():
    lang="es"
    if len(sys.argv)>1:
        lang=sys.argv[1]
    
    conn = _mysql.connect(host='sql-s3', db='%swiki_p' % lang, read_default_file='~/.my.cnf')
    essite=wikipedia.Site(lang, "wikipedia")
    projects=loadProjects(essite)
    limitenuevos=2000
    [nuevos_dic, nuevos_list]=loadNewPages(essite, limitenuevos)
    
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
                    page[page_id]={'t':page_title, 'l':page_len, 'nm':page_nm, 'i':0, 'c':0, 'cat':0, 'iws':0, 'im':0, 'en':0, 'f':False, 'con':False, 'rel':False, 'wik':False, 'edit':False, 'ref':False, 'obras':False, 'neutral':False, 'trad':False, 'discutido':False, 'nuevo':page_new}
            row=r.fetch_row(maxrows=1, how=1)
        
        time.sleep(10)
    conn.close()

if __name__ == "__main__":
    main()
