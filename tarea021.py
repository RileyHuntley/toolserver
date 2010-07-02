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

from __future__ import generators

import sets
import wikipedia
import re
import sys
import os
import gzip
import time
import sqlite3
import MySQLdb
import _mysql

# todo:
# evitar hacer fetchall (xfetch?) enteros

def ResultIter(cursor, arraysize=1000):
    'An iterator that uses fetchmany to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result

def percent(c):
    if c % 1000 == 0:
        wikipedia.output(u'Llevamos %d' % c)

def getPageTitle(conn, cursor, pageid):
    cursor.execute("select title from page where id=?", (pageid,))
    conn.commit()
    for row in ResultIter(cursor):
        return row
    return None

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

def loadCategories(site, projects):
    categories={}
    categoriesall=[]
    for pr in projects:
        wikipedia.output(u'Loading categories for %s project' % pr)
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Categorías' % pr)
        if wii.exists() and not wii.isRedirectPage():
            categories[pr]={}
            trozos=wii.get().splitlines()
            categoriesall=[]
            for trozo in trozos:
                trozo=trozo.strip() #re.sub(ur'(?im)^ *([^\n\r]*?) *$', ur'\1', trozo)
                trozo=re.sub(ur'(?i) *(Categoría|Category) *: *', ur'', trozo)
                trozo=re.sub('_', ' ', trozo)
                if len(trozo)<1 or trozo[0]=='#':
                    continue
                if categoriesall.count(trozo)==0:
                    #wikipedia.output(u'  Categoría:%s' % trozo)
                    categoriesall.append(trozo)
                    categories[pr][trozo]=[]
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

sqlite3file='/home/emijrp/temporal/tarea021.db'
os.system('rm %s' % sqlite3file)

def main():
    lang="es"
    if len(sys.argv)>1:
        lang=sys.argv[1]

    clasificacion={0:u'·',1:u'Destacado',2:u'Bueno',3:u'Esbozo',4:u'Miniesbozo',5:u'Desambiguación'}
    #calidad={0:u'·',1:u'Bueno ([[Imagen:Artículo bueno.svg|14px|Artículo bueno]])',2:u'Destacado ([[Imagen:Cscr-featured.svg|14px|Artículo destacado]])'}
    importancia={0:u'·',1:u'Clase-A',2:u'Clase-B',3:u'Clase-C',4:u'Clase-D'}
    namespaces={104:u'Anexo'}
    namespaces_={104:u'Anexo:'}
    limitenuevos=2000
    categories={}
    projects=[]
    projectsall=[]
    avisotoolserver=u'<noinclude>{{aviso|Esta plantilla es actualizada automáticamente. No hagas cambios aquí. Si hay errores avisa a {{u|emijrp}}.}}</noinclude>\n'
    nohay=u':No hay contenido con estas características.'
    
    essite=wikipedia.Site('es', 'wikipedia')
    #Loading projects names
    projects=loadProjects(essite)
    
    #hacer que carguen las categorias desde una pagina, que quite category: etc, y compruebe que existen
    categories=loadCategories(essite, projects)
    
    #page=sets.Set()
    page={}
    pagetitle2pageid={}

    #bajamos los ultimos articulos nuevos y los metemos en un diccionario
    [nuevos_dic, nuevos_list]=loadNewPages(essite, limitenuevos)
    
    #page_id, page_title, page_length
    sqliteconn = sqlite3.connect(sqlite3file)
    sqlitecursor = sqliteconn.cursor()
    sqlitecursor.execute("""create table page 
    (id integer, title text, length integer, namespace integer, images integer, class integer, 
     categories integer, interwikis integer, importance integer, en integer, f bool, con bool, 
     rel bool, wik bool, edit bool, ref bool, obras bool, neutral bool, 
     trad bool, discutido bool, nuevo bool)""")
    sqliteconn.commit()
    
    conn = _mysql.connect(host='sql-s3', db='%swiki_p' % lang, read_default_file='~/.my.cnf')
    conn.query("SELECT page_id, page_title, page_len, page_namespace from page where (page_namespace=0 or page_namespace=104) and page_is_redirect=0;")
    r=conn.use_result()
    row=r.fetch_row(maxrows=1, how=1)
    c=0
    print 'Loading pages from %swiki' % (lang)
    while row:
        if len(row)==1:
            row=row[0]
            page_id=int(row['page_id'])
            page_title=re.sub('_', ' ', row['page_title'])
            page_len=int(row['page_len'])
            page_nm=int(row['page_namespace'])
            page_new=False
            if nuevos_dic.has_key(page_title):
                page_new=True
            c+=1
            percent(c)
            #page.add(page_id)
            pagetitle2pageid[page_title]=page_id
            #page[page_id]=0
            page[page_id]={'t':page_title, 'l':page_len, 'nm':page_nm, 'i':0, 'c':0, 'cat':0, 'iws':0, 'im':0, 'en':0, 'f':False, 'con':False, 'rel':False, 'wik':False, 'edit':False, 'ref':False, 'obras':False, 'neutral':False, 'trad':False, 'discutido':False, 'nuevo':page_new}
            #insert
            #print page_title
            #tupla=(page_id, page_title, page_len, page_nm, 0, 0, 0, 0, 0, 0, False, False, False, False, False, False, False, False, False, False, page_new)
            #sqlitecursor.execute("insert into page values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tupla)
            #if c % 1000 == 0:
            #    sqliteconn.commit()
            #print "insert into page (`id`, `t`, `l`, `nm`, `i`, `c`, `cat`, `iws`, `im`, `en`, `f`, `con`, `rel`, `wik`, `edit`, `ref`, `obras`, `neutral`, `trad`, `discutido`, `nuevo`) values (%s, '%s', %s, %s, 0, 0, 0, 0, 0, 0, False, False, False, False, False, False, False, False, False, False, False)" % (page_id, MySQLdb.escape_string(page_title), page_len, page_nm)
            #cursor2.execute("SELECT count(*) from page where 1")
            #result2=cursor2.fetchall()
            #print result2[0]
        row=r.fetch_row(maxrows=1, how=1)
    sqliteconn.commit()
    #se ha olvidado alguna el commit? (sqllite puede fallar segun lei por ahi)
    for row2 in sqlitecursor.execute("select count(*) from page"):
        if c!=row2[0]:
            print "Error"
            sys.exit()
    print 'Loaded %d pages from %swiki' % (c, lang)
    
    for i in range(1000):
        print getPageTitle(sqliteconn, sqlitecursor, i)
    
    #cargamos page_id y page_title para plantillas
    templates={} #nos va a hacer falta luego para las imagenes inservibles
    cursor.execute("SELECT page_id, page_title from page where page_namespace=10;")
    c=0
    for row in ResultIter(cursor):
        if len(row)==2:
            page_id=int(row[0])
            page_title=re.sub('_', ' ', row[1])
            c+=1
            percent(c)
            templates[page_id]=page_title
    print 'Cargadas %d templates en %swiki' % (c, lang)

    #esto debe ser lo primero, elegir las paginas para los proyectos, y su numero de categorias
    #bajamos tabla de categorylinks
    exclusioncat_pattern=re.compile(ur'(?i)Wikipedia:')
    # es mas eficiente un join?
    cursor.execute("SELECT cl_from, cl_to from categorylinks;")
    c=0
    for row in ResultIter(cursor):
        if len(row)==2:
            cl_from=int(row[0])
            cl_to=re.sub('_', ' ', row[1])
            #sumamos 1 cat
            if cl_from in page and not re.search(exclusioncat_pattern, cl_to):
                #print '->%s<-' % cl_from
                #print page[cl_from]
                #page[cl_from]+=1
                for k, v in categories.items():
                    if categories[k].has_key(cl_to) and categories[k][cl_to].count(cl_from)==0:
                        categories[k][cl_to].append(cl_from)
                        c+=1
                        percent(c)
                sqlitecursor.execute("update page set categories=categories+1 where id=?", (cl_from,)) #no importa que se haya creado un artículo nuevo en los últimos segundos, no veríamos error en mysql
                if c % 100 == 0:
                    sqliteconn.commit()
    sqliteconn.commit()
    print 'Categorizados %d veces' % (c)
    
    #quitar
    sqlitecursor.execute("select * from page where categories!=0")
    c=0
    for row2 in sqlitecursor:
        print row2
        c+=1
        if c>10:
            break
    sys.exit()
    #fin quitar
    
    #comprobamos clasificacion
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
    cursor.execute("SELECT tl_from, tl_title from templatelinks;")
    c=0
    for row in ResultIter(cursor):
        if len(row)==2:
            c+=1
            percent(c)
            tl_from=int(row [0])
            tl_title=re.sub('_', ' ', row [1])
            if page.has_key(tl_from):
                if re.search(destacado_pattern, tl_title):
                    #page[tl_from]['c']=1
                    cursor2.execute("update page set c=1 where id=%s" % tl_from)
                elif re.search(bueno_pattern, tl_title):
                    #page[tl_from]['c']=2
                    cursor2.execute("update page set c=2 where id=%s" % tl_from)
                elif re.search(esbozo_pattern, tl_title):
                    #page[tl_from]['c']=3
                    cursor2.execute("update page set c=3 where id=%s" % tl_from)
                elif re.search(miniesbozo_pattern, tl_title):
                    #page[tl_from]['c']=4
                    cursor2.execute("update page set c=4 where id=%s" % tl_from)
                elif re.search(desamb_pattern, tl_title):
                    #page[tl_from]['c']=5
                    cursor2.execute("update page set c=5 where id=%s" % tl_from)
                #sino es ninguna de las 5 cosas, se queda el 0 que significa desconocida
                
                if re.search(fusionar_pattern, tl_title):
                    #page[tl_from]['f']=True
                    cursor2.execute("update page set f=True where id=%s" % tl_from)
                if re.search(contextualizar_pattern, tl_title):
                    #page[tl_from]['con']=True
                    cursor2.execute("update page set con=True where id=%s" % tl_from)
                if re.search(sinrelevancia_pattern, tl_title):
                    #page[tl_from]['rel']=True
                    cursor2.execute("update page set rel=True where id=%s" % tl_from)
                if re.search(wikificar_pattern, tl_title):
                    #page[tl_from]['wik']=True
                    cursor2.execute("update page set wik=True where id=%s" % tl_from)
                if re.search(copyedit_pattern, tl_title):
                    #page[tl_from]['edit']=True
                    cursor2.execute("update page set edit=True where id=%s" % tl_from)
                if re.search(sinreferencias_pattern, tl_title):
                    #page[tl_from]['ref']=True
                    cursor2.execute("update page set ref=True where id=%s" % tl_from)
                if re.search(enobras_pattern, tl_title):
                    #page[tl_from]['obras']=True
                    cursor2.execute("update page set obras=True where id=%s" % tl_from)
                if re.search(noneutral_pattern, tl_title):
                    #page[tl_from]['neutral']=True
                    cursor2.execute("update page set neutral=True where id=%s" % tl_from)
                if re.search(traduccion_pattern, tl_title):
                    #page[tl_from]['trad']=True
                    cursor2.execute("update page set trad=True where id=%s" % tl_from)
                if re.search(discutido_pattern, tl_title):
                    #page[tl_from]['discutido']=True
                    cursor2.execute("update page set discutido=True where id=%s" % tl_from)
    print '%d templatelinks' % (c)

    #generamos lista de imagenes inservibles
    imagenesnegras={}
    cursor.execute("SELECT il_from, il_to from imagelinks;")
    result=cursor.fetchall()
    c=0
    c2=0
    for row in result:
        if len(row)==2:
            c+=1
            percent(c)
            il_from=int(row[0])
            il_to=re.sub('_', ' ', row[1])
            if templates.has_key(il_from):
                imagenesnegras[il_to]=False #ahorrar
                c2+=1
    print '%d imagelinks, %d imagenes negras' % (c, c2)

    #VOY POR AQUI tarea021b.py
    #ahora contamos imagenes, sin contar inservibles, usamos el mismo fichero q antes
    cursor.execute("SELECT il_from, il_to from imagelinks where il_from in (select page_id from page where (page_namespace=0 or page_namespace=104) and page_is_redirect=0);")
    result=cursor.fetchall()
    c=0
    for row in result:
        if len(row)==2:
            il_from=int(row[0])
            il_to=re.sub('_', ' ', row[1])
            if not imagenesnegras.has_key(il_to):
                #page[il_from]['i']+=1
                cursor2.execute("update page set i=i+1 where id=%s" % il_from)
                c+=1
                percent(c)
    print '%d imagenes usadas' % (c)

    #contamos interwikis
    cursor.execute("SELECT ll_from, ll_lang from langlinks where ll_from in (select page_id from page where (page_namespace=0 or page_namespace=104) and page_is_redirect=0);")
    result=cursor.fetchall()
    c=0
    for row in result:
        if len(row)==2:
            c+=1
            percent(c)
            ll_from=int(row[0])
            ll_lang=re.sub('_', ' ', row[1])
            #if page.has_key(ll_from):
            #    page[ll_from]['iws']+=1
            cursor2.execute("update page set iws=iws+1 where id=%s" % ll_from)
    print '%d langlinks' % (c)
    f.close()

    #contamos enlaces entrantes
    #bajamos el dump, es mas eficiente
    try:
        f=gzip.open('/mnt/user-store/%swiki-latest-pagelinks.sql.gz' % lang, 'r')
    except:
        os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-pagelinks.sql.gz -O /mnt/user-store/%swiki-latest-pagelinks.sql.gz' % (lang, lang, lang)) #entorno a 150MB
        f=gzip.open('/mnt/user-store/%swiki-latest-pagelinks.sql.gz' % lang, 'r')
    c=0
    pagelinks_pattern=re.compile(ur'(?i)\((\d+)\,(0|104)\,\'([^\']*?)\'\)') #104 anexo:
    for line in f:
        line=line[:len(line)-1] #evitamos \n
        line=re.sub('_', ' ', line)
        m=re.findall(pagelinks_pattern, line)
        for i in m:
            c+=1
            percent(c)
            pl_from=int(i[0])
            pl_nm=int(i[1])
            pl_title=u''
            try:
                pl_title=unicode(i[2], 'utf-8')
            except:
                continue
            #if page.has_key(pl_from) and pagetitle2pageid.has_key(pl_title): #si el enlace proviene del nm=0 y va hacia un nm=0
            #    page_id=pagetitle2pageid[pl_title]
            #    if page.has_key(page_id):
            #        page[page_id]['en']+=1 #+1 entrante, im es importancia
            cursor2.execute("update page set en=en+1 where id=%s" % pl_from)
    print '%d pagelinks' % (c)
    f.close()


    #empezamos el analisis propiamente dicho
    limpag=500
    limcabecera=50
    limkblist=5
    cabeceratabla=u'\n|-\n! # !! Artículo !! Disc !! Tamaño !! Clasificación !! Importancia !! Ent !! Cat !! Img !! Iw !! Otros '
    for pr, cats in categories.items():
        wikipedia.output(u'%s' % pr)
        inicio=u'{{Wikipedia:Contenido por wikiproyecto/Inicio|%s}}\n\n== Índice ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Índice}}\n\n== Artículos ==\n\'\'Actualizado por última vez a las {{subst:CURRENTTIME}} ([[UTC]]) del {{subst:CURRENTDAY}} de {{subst:CURRENTMONTHNAME}} de {{subst:CURRENTYEAR}}.\'\'\n<center>\n<span style="clear:left;float:left;">{{#ifexpr:{{SUBPAGENAME}}>1|← [[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}-1}}|Anterior]]|← Esta es la primera}}</span><span style="clear:right;float:right;">{{#ifexist:Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|[[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|Siguiente]] →|Esta es la última →}}</span><span id="arriba">↓ [[#abajo|Ir al final]] ↓</span>\n{| class="wikitable sortable" style="text-align: center;"%s' % (pr, pr, pr, pr, pr, cabeceratabla)
        fin=u'\n|}\n<span style="clear:left;float:left;">{{#ifexpr:{{SUBPAGENAME}}>1|← [[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}-1}}|Anterior]]|← Esta es la primera}}</span><span style="clear:right;float:right;">{{#ifexist:Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|[[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|Siguiente]] →|Esta es la última →}}</span><span id="abajo">↑ [[#arriba|Ir al principio]] ↑</span>\n</center>\n\n{{Wikipedia:Contenido por wikiproyecto/Fin|%s}}' % (pr, pr, pr, pr)
        salida=inicio
        c=0
        nodupes=[] #evitamos duplicados
        resumen={'desconocida':0,'bueno':0,'destacado':0,'esbozo':0,'miniesbozo':0,'desambig':0,'>10':0,'>5':0,'>2':0,'>1':0,'<1':0,'<2':0}
        artstitles=[]
        artstitles2=[]
        for cat, arts in cats.items():
            wikipedia.output(u'  Categoría:%s' % cat)
            for artid in arts:
                if page.has_key(artid) and nodupes.count(artid)==0:
                    nodupes.append(artid)
                    artstitles.append([page[artid]['t'], artid])
                    artstitles2.append([page[artid]['en'], page[artid]['t'], artid])
        
        #ordenamos alfabeticamente
        artstitles.sort()
        #ordenamos por entrantes
        artstitles2.sort()
        artstitles2.reverse()
        
        lenartstitles=len(artstitles)
        qclasea=lenartstitles/100*2
        listqclasea=[]
        qclaseb=lenartstitles/100*5-qclasea
        listqclaseb=[]
        qclasec=lenartstitles/100*20-qclaseb
        qclased=lenartstitles-qclasec
        
        #calculamos importancias
        i=0
        for artentrantes, arttitle, artid in artstitles2:
            if i<qclasea:
                page[artid]['im']=1
                if listqclasea.count(arttitle)==0:
                    listqclasea.append([artentrantes, arttitle])
            elif i<qclasea+qclaseb:
                page[artid]['im']=2
                if listqclaseb.count(arttitle)==0:
                    listqclaseb.append([artentrantes, arttitle])
            elif i<qclasea+qclaseb+qclasec:
                page[artid]['im']=3
            else:
                page[artid]['im']=4
            i+=1
        
        #blanqueamos para ahorrar memoria
        artstitles2=[]
        
        #ordenamos listas de importancia
        listqclasea.sort()
        listqclasea.reverse()
        listqclaseb.sort()
        listqclaseb.reverse()
        
        #generamos salida de listas de importancia
        listqclaseaplana='\n'.join(['# [[%s]] (%d enlaces entrantes)' % (arttitle, artentrantes) for artentrantes, arttitle in listqclasea])
        listqclasebplana='\n'.join(['# [[%s]] (%d enlaces entrantes)' % (arttitle, artentrantes) for artentrantes, arttitle in listqclaseb])
        
        #recorremos los articulos del wikiproyecto
        qfusionar=0
        qcontextualizar=0
        qsinrelevancia=0
        qwikificar=0
        qcopyedit=0
        qsinreferencias=0
        qenobras=0
        qnoneutral=0
        qentraduccion=0
        qveracidaddiscutida=0
        relatedchanges=u''
        for arttitle, pageid in artstitles:
            #resumen tamanios
            if page[pageid]['l']>=10*1024:
                resumen['>10']+=1
            if page[pageid]['l']>=5*1024:
                resumen['>5']+=1
            if page[pageid]['l']>=2*1024:
                resumen['>2']+=1
            if page[pageid]['l']>=1*1024:
                resumen['>1']+=1
            if page[pageid]['l']<1*1024:
                resumen['<1']+=1
            if page[pageid]['l']<2*1024:
                resumen['<2']+=1
            
            #resumen calidad
            if page[pageid]['c']==1:
                resumen['destacado']+=1
            elif page[pageid]['c']==2:
                resumen['bueno']+=1
            elif page[pageid]['c']==3:
                resumen['esbozo']+=1
            elif page[pageid]['c']==4:
                resumen['miniesbozo']+=1
            elif page[pageid]['c']==5:
                resumen['desambig']+=1
            else:
                resumen['desconocida']+=1
            
            c+=1
            otros=u''
            if page[pageid]['f']:
                qfusionar+=1
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Fusionar|fusionar]]' % pr
            if page[pageid]['con']:
                qcontextualizar+=1
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Contextualizar|contextualizar]]' % pr
            if page[pageid]['rel']:
                qsinrelevancia+=1
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Sin relevancia|sin relevancia]]' % pr
            if page[pageid]['wik']:
                qwikificar+=1
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Wikificar|wikificar]]' % pr
            if page[pageid]['edit']:
                qcopyedit+=1
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Copyedit|copyedit]]' % pr
            if page[pageid]['ref']:
                qsinreferencias+=1
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Sin referencias|sin referencias]]' % pr
            if page[pageid]['obras']:
                qenobras+=1
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#En obras|en obras]]' % pr
            if page[pageid]['neutral']:
                qnoneutral+=1
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#No neutral|no neutral]]' % pr
            if page[pageid]['trad']:
                qentraduccion+=1
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#En traducción|en traducción]]' % pr
            if page[pageid]['discutido']:
                qveracidaddiscutida+=1
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Veracidad discutida|discutido]]' % pr
            if page[pageid]['nuevo']:
                if otros:
                    otros+=u', '
                otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Nuevos|nuevo]]' % pr
            
            clasificacionplana=u''
            if page[pageid]['c']==1: #1 destacado
                clasificacionplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Artículos destacados|Destacado]]' % pr
            elif page[pageid]['c']==2: #2 es bueno, 
                clasificacionplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Artículos buenos|Bueno]]' % pr
            else: #resto: esbozo, miniesbozo, desambig, ·
                clasificacionplana=clasificacion[page[pageid]['c']]
            
            importanciaplana=u''
            if page[pageid]['im']==1:
                importanciaplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Clase-A|Clase-A]]' % pr
            elif page[pageid]['im']==2:
                importanciaplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Clase-B|Clase-B]]' % pr
            else:
                importanciaplana=importancia[page[pageid]['im']]
            
            artnm=u''
            artnm_=u''
            if page[pageid]['nm']!=0:
                artnm=namespaces[page[pageid]['nm']]
                artnm+=u' ' # http://es.wikipedia.org/w/index.php?title=Wikipedia:Contenido_por_wikiproyecto/Aviaci%C3%B3n/4&curid=1996845&diff=21475084&oldid=21403165
                artnm_=namespaces_[page[pageid]['nm']]
            
            salida+=u'\n|-\n| %d || [[%s%s]] || [[%sDiscusión:%s|Disc]] || %d || %s || %s || %d || %d || %d || %d || %s ' % (c, artnm_, arttitle, artnm, arttitle, page[pageid]['l'], clasificacionplana, importanciaplana, page[pageid]['en'], page[pageid]['cat'], page[pageid]['i'], page[pageid]['iws'], otros)
            relatedchanges+=u'# [[%s%s]]\n' % (artnm_, arttitle) #pagina 0
            #if c % limcabecera == 0:
            #    salida+=cabeceratabla
            if c % limpag == 0:
                salida+=fin
                #guardamos
                wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/%d' % (pr, c/limpag)) #numeracion
                wii.put(salida, u'BOT - Actualizando lista para [[Wikiproyecto:%s]]' % pr)
                salida=inicio
        if salida!=inicio:
            salida+=fin
            #guardamos
            wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/%d' % (pr, c/limpag+1)) #numeracion
            wii.put(salida, u'BOT - Actualizando lista para [[Wikiproyecto:%s]]' % pr)
        
        #pagina 0 para hacer relatedchanges
        if len(relatedchanges)<=1024*500: #limite de KBs
            wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/0' % (pr))
            wii.put(relatedchanges, u'BOT - Actualizando lista para [[Wikiproyecto:%s]]' % pr)
        #fin pagina 0
        
        salida=u''
        for i in range(1, c/limpag+2):
            if salida:
                salida+=u' – [[Wikipedia:Contenido por wikiproyecto/%s/%d|Página %d]]' % (pr, i, i)
            else:
                salida+=u'[[Wikipedia:Contenido por wikiproyecto/%s|Resumen]]: [[Wikipedia:Contenido por wikiproyecto/%s/%d|Página %d]]' % (pr, pr, i, i)
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Índice' % pr) #index
        wii.put(salida, u'BOT - Actualizando índice')
        
        
        #resumen global
        
        #tabla de clasificacion
        tablaclasificacion=avisotoolserver
        tablaclasificacion+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
        tablaclasificacion+=u'! colspan=4 | Clasificación !! rowspan=2 | Total '
        tablaclasificacion+=u'\n|-\n! [[Wikipedia:Artículos destacados|Destacado]] [[Imagen:Cscr-featured.svg|14px|Artículo destacado]] !! [[Wikipedia:Artículos buenos|Bueno]] [[Imagen:Artículo bueno.svg|14px|Artículo bueno]] !! [[Wikipedia:Página de desambiguación|Desambiguación]] !! Desconocido'
        tablaclasificacion+=u'\n|-\n| [[Wikipedia:Contenido por wikiproyecto/%s#Artículos destacados|%d]] || [[Wikipedia:Contenido por wikiproyecto/%s#Artículos buenos|%d]] || %d || %d || %d ' % (pr, resumen['destacado'], pr, resumen['bueno'], resumen['desambig'], resumen['desconocida'], lenartstitles)
        tablaclasificacion+=u'\n|-\n| %.1f%% || %.1f%% || %.1f%% || %.1f%% || 100%%' % ((resumen['destacado']/(lenartstitles/100.0)), (resumen['bueno']/(lenartstitles/100.0)), (resumen['desambig']/(lenartstitles/100.0)), (resumen['desconocida']/(lenartstitles/100.0)))
        tablaclasificacion+=u'\n|}</onlyinclude>\n'
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Clasificación' % pr) #resumen
        wii.put(tablaclasificacion, u'BOT - Actualizando tabla de clasificación para [[Wikiproyecto:%s]]' % pr)
        
        #tabla de tamanios
        tablatamanos=avisotoolserver
        tablatamanos+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
        tablatamanos+=u'! colspan=6 | Tamaño !! rowspan=2 | Total '
        tablatamanos+=u'\n|-\n! > 10 KB !! > 5 KB !! > 2 KB !! > 1 KB !! < 1 KB !! < 2 KB '
        tablatamanos+=u'\n|-\n| %d || %d || %d || %d || %d || %d || %d ' % (resumen['>10'], resumen['>5'], resumen['>2'], resumen['>1'], resumen['<1'], resumen['<2'], lenartstitles)
        tablatamanos+=u'\n|-\n| %.1f%% || %.1f%% || %.1f%% || %.1f%% || %.1f%% || %.1f%% || 100%%' % ((resumen['>10']/(lenartstitles/100.0)), (resumen['>5']/(lenartstitles/100.0)), (resumen['>2']/(lenartstitles/100.0)), (resumen['>1']/(lenartstitles/100.0)), (resumen['<1']/(lenartstitles/100.0)), (resumen['<2']/(lenartstitles/100.0)))
        tablatamanos+=u'\n|}</onlyinclude>\n'
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Tamaños' % pr) #resumen
        wii.put(tablatamanos, u'BOT - Actualizando tabla de tamaños para [[Wikiproyecto:%s]]' % pr)
        
        #tabla de clases (importancia)
        tablaimportancia=avisotoolserver
        tablaimportancia+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
        tablaimportancia+=u'! colspan=4 | Importancia !! rowspan=2 | Total '
        tablaimportancia+=u'\n|-\n! Clase-A ↑↑ !! Clase-B ↑ !! Clase-C ↓ !! Clase-D ↓↓'
        tablaimportancia+=u'\n|-\n| [[Wikipedia:Contenido por wikiproyecto/%s#Clase-A|%d]] || [[Wikipedia:Contenido por wikiproyecto/%s#Clase-B|%d]] || %d || %d || %d ' % (pr, qclasea, pr, qclaseb, qclasec, qclased, lenartstitles)
        tablaimportancia+=u'\n|-\n| 1–2%s || 3–5%s || 6–10%s || 11–100%s || 100%s ' % (u'%', u'%', u'%', u'%', u'%')
        tablaimportancia+=u'\n|}</onlyinclude>\n'
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Importancia' % pr) #resumen
        wii.put(tablaimportancia, u'BOT - Actualizando tabla de importancia para [[Wikiproyecto:%s]]' % pr)
        
        #tabla de mantenimiento
        qmantenimiento=qfusionar+qcontextualizar+qsinrelevancia+qwikificar+qcopyedit+qsinreferencias+qenobras+qnoneutral+qentraduccion+qveracidaddiscutida
        tablamantenimiento=avisotoolserver
        tablamantenimiento+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
        tablamantenimiento+=u'! colspan=3 | Mantenimiento '
        tablamantenimiento+=u'\n|-\n! Fusionar \n| [[Wikipedia:Contenido por wikiproyecto/%s#Fusionar|%d]] \n| %.1f%% ' % (pr, qfusionar, (qfusionar/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Contextualizar \n| [[Wikipedia:Contenido por wikiproyecto/%s#Contextualizar|%d]] \n| %.1f%% ' % (pr, qcontextualizar, (qcontextualizar/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Sin relevancia \n| [[Wikipedia:Contenido por wikiproyecto/%s#Sin relevancia|%d]] \n| %.1f%% ' % (pr, qsinrelevancia, (qsinrelevancia/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Wikificar \n| [[Wikipedia:Contenido por wikiproyecto/%s#Wikificar|%d]] \n| %.1f%% ' % (pr, qwikificar, (qwikificar/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Copyedit \n| [[Wikipedia:Contenido por wikiproyecto/%s#Copyedit|%d]] \n| %.1f%% ' % (pr, qcopyedit, (qcopyedit/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Sin referencias \n| [[Wikipedia:Contenido por wikiproyecto/%s#Sin referencias|%d]] \n| %.1f%% ' % (pr, qsinreferencias, (qsinreferencias/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! En obras \n| [[Wikipedia:Contenido por wikiproyecto/%s#En obras|%d]] \n| %.1f%% ' % (pr, qenobras, (qenobras/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! No neutral \n| [[Wikipedia:Contenido por wikiproyecto/%s#No neutral|%d]] \n| %.1f%% ' % (pr, qnoneutral, (qnoneutral/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! En traducción \n| [[Wikipedia:Contenido por wikiproyecto/%s#En traducción|%d]] \n| %.1f%% ' % (pr, qentraduccion, (qentraduccion/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n! Veracidad discutida \n| [[Wikipedia:Contenido por wikiproyecto/%s#Veracidad discutida|%d]] \n| %.1f%% ' % (pr, qveracidaddiscutida, (qveracidaddiscutida/(qmantenimiento/100.0)))
        tablamantenimiento+=u'\n|-\n| Total \n| %d \n| 100%% ' % (qmantenimiento)
        tablamantenimiento+=u'\n|}</onlyinclude>\n'
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Mantenimiento' % pr) #resumen
        wii.put(tablamantenimiento, u'BOT - Actualizando tabla de mantenimiento para [[Wikiproyecto:%s]]' % pr)
        
        #tabla con categorias y numero de articulos que contienen, en desuso
        categoriasanalizadas=u'{| class="wikitable sortable" style="text-align: center;"\n! #\n! Categoría\n! Artículos'
        categoriasordenadas=[]
        for cat, arts in categories[pr].items():
            categoriasordenadas.append([cat, arts])
        categoriasordenadas.sort()
        cont=1
        for cat, arts in categoriasordenadas:
            categoriasanalizadas+=u'\n|-\n| %d || [[:Categoría:%s|%s]] || %d ' %  (cont, cat, cat, len(arts))
            cont+=1
        categoriasanalizadas+=u'\n|}'

        #pagina de resumen con hijas
        resumen=u'\'\'Actualizado por última vez a las {{subst:CURRENTTIME}} ([[UTC]]) del {{subst:CURRENTDAY}} de {{subst:CURRENTMONTHNAME}} de {{subst:CURRENTYEAR}}.\'\'\n'
        resumen+=u'{| style="background-color: transparent"\n| valign=top |\n'
        resumen+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Clasificación}}\n' % pr
        resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Clasificación]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
        resumen+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Tamaños}}\n' % pr
        resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Tamaños]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
        resumen+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Importancia}}\n' % pr
        resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Importancia]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
        resumen+=u'\nEn total han sido analizadas [[Wikipedia:Contenido por wikiproyecto/%s/Categorías|%d categorías]].\n' % (pr, len(categoriasordenadas))
        resumen+=u'| valign=top |\n{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Mantenimiento}}\n' % pr
        resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Mantenimiento]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
        resumen+=u'|}'
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen' % pr) #resumen
        wii.put(resumen, u'BOT - Actualizando resumen para [[Wikiproyecto:%s]]' % pr)
        
        #seccion importancia, mantenimiento
        clasea=avisotoolserver+listqclaseaplana
        claseb=avisotoolserver+listqclasebplana
        
        buenos=avisotoolserver
        destacados=avisotoolserver
        fusionar=avisotoolserver
        contextualizar=avisotoolserver
        sinrelevancia=avisotoolserver
        wikificar=avisotoolserver
        copyedit=avisotoolserver
        sinreferencias=avisotoolserver
        enobras=avisotoolserver
        noneutral=avisotoolserver
        traduccion=avisotoolserver
        discutido=avisotoolserver
        nuevos=avisotoolserver
        nuevos_temp=[]
        
        for arttitle, pageid in artstitles:
            artnm=u''
            artnm_=u''
            if page[pageid]['nm']!=0:
                artnm=namespaces[page[pageid]['nm']]
                artnm_=namespaces_[page[pageid]['nm']]
            if page[pageid]['c']==2:
                buenos+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['c']==1:
                destacados+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['f']:
                fusionar+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['con']:
                contextualizar+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['rel']:
                sinrelevancia+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['wik']:
                wikificar+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['edit']:
                copyedit+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['ref']:
                sinreferencias+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['obras']:
                enobras+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['neutral']:
                noneutral+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['trad']:
                traduccion+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['discutido']:
                discutido+=u'# [[%s%s]]\n' % (artnm_, arttitle)
            if page[pageid]['nuevo']:
                nuevos_temp.append(arttitle) #los almacenamos para despues ordenarlos cronologicamente
        
        for arttitle in nuevos_list:
            if nuevos_temp.count(arttitle)!=0:
                nuevos+=u'# [[%s%s]] (Creado el %s por [[Usuario:%s|%s]])\n' % (artnm_, arttitle, re.sub(ur'\d\d\:\d\d ', ur'', nuevos_dic[arttitle]['date']), nuevos_dic[arttitle]['user'], nuevos_dic[arttitle]['user'])
        
        salida=u'== Calidad ==\n'
        subpages=[
            [destacados, u'Artículos destacados', u'[[Imagen:Cscr-featured.svg|14px|Artículo destacado]]'],
            [buenos, u'Artículos buenos', u'[[Imagen:Artículo bueno.svg|14px|Artículo bueno]]'],
            [clasea, u'Importancia Clase-A', u''],
            [claseb, u'Importancia Clase-B', u''],
            [fusionar, u'Fusionar', u''],
            [contextualizar, u'Contextualizar', u''],
            [sinrelevancia, u'Sin relevancia', u''],
            [wikificar, u'Wikificar', u''],
            [copyedit, u'Copyedit', u''],
            [sinreferencias, u'Sin referencias', u''],
            [enobras, u'En obras', u''],
            [noneutral, u'No neutral', u''],
            [traduccion, u'En traducción', u''],
            [discutido, u'Veracidad discutida', u''],
            [nuevos, u'Nuevos', u''],        
        ]
        c=0
        for output, subpage, image in subpages:
            if output:
                if output==avisotoolserver:
                    output+=nohay
                wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/%s' % (pr, subpage))
                wii.put(output, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
                salida+=u'=== %s %s ===\n' % (subpage, image)
                salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/%s|R}}<=%d*1024\n' % (pr, subpage, limkblist)
                salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/%s]]<nowiki>}}</nowiki>\'\'.\n' % (pr, subpage)
                salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/%s}}\n' % (pr, subpage)
                salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/%s]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr, subpage)
                salida+=u'}}\n\n'
            if c==3:
                salida+=u'== Mantenimiento ==\n'
        
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Detalles' % pr) #detalles
        wii.put(salida, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
        
        #pagina del pr
        #salida=u'{{Wikipedia:Contenido por wikiproyecto/Iconos|%s}}\nAnálisis del contenido en el ámbito de [[Wikiproyecto:%s]]. Para añadir páginas debes modificar la <span class="plainlinks">[http://es.wikipedia.org/w/index.php?title=Wikipedia:Contenido_por_wikiproyecto/%s/Categorías&action=edit lista de categorías]</span>.\n\n== Índice ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Índice}}\n\n== Resumen ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Resumen}}\n\n{{Wikipedia:Contenido por wikiproyecto/%s/Detalles}}\n\n[[Categoría:Wikipedia:Contenido por wikiproyecto|%s]]\n[[Categoría:Wikipedia:Contenido por wikiproyecto/%s| ]]' % (pr, pr, re.sub(u' ', u'_', pr), pr, pr, pr, pr, pr)
        salida=u'{{Wikipedia:Contenido por wikiproyecto/Iconos|%s}}\nAnálisis del contenido en el ámbito de [[Wikiproyecto:%s]]. Para añadir páginas debes modificar la <span class="plainlinks">[http://es.wikipedia.org/w/index.php?title=Wikipedia:Contenido_por_wikiproyecto/%s/Categorías&action=edit lista de categorías]</span>. {{Purgar|Actualizar esta página}}.\n\n== Índice ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Índice}}\n\n== Resumen ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Resumen}}\n\n{{Wikipedia:Contenido por wikiproyecto/%s/Detalles}}\n\n[[Categoría:Wikipedia:Contenido por wikiproyecto|%s]]\n[[Categoría:Wikipedia:Contenido por wikiproyecto/%s| ]]' % (pr, pr, re.sub(u' ', u'_', pr), pr, pr, pr, pr, pr)
        wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s' % pr) #principal
        wii.put(salida, u'BOT - Actualizando página de [[Wikiproyecto:%s]]' % pr)

    sqlitecursor.close()
    sqliteconn.close()
    cursor.close()
    conn.close()
    cursor2.close()
    conn2.close()

if __name__ == "__main__":
    main()
