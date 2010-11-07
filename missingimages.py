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
import gzip
import md5
import os
import re
import sys
import time

import wikipedia

import tarea000

lenguajeobjetivo = sys.argv[1] # de momento probar con 1 solo a la vez
lenguajefuente = 'en' # mirar nota1 si meto una lista en vez de individual
family = 'wikipedia'
imagelinks_pattern = re.compile(ur"\((\d+)\,\'([^\']+?)\'\)")
ex = ur'(?i)(%s)' % ('|'.join(wikipedia.Page(wikipedia.Site("en", "wikipedia"), u"User:Emijrp/Images for biographies/Exclusions").get().splitlines()))
exclusion_pattern=re.compile(ex) # los ' y " los filtramos al final

def percent(c, d=1000):
    if c % d == 0: sys.stderr.write('.') #print '\nLlevamos %d' % c

def utf8rm_(l):
    return re.sub('_', ' ', unicode(l, 'utf-8')

def main():
    pagetitle2pageid, pageid2pagetitle, pageid2pagetitle2, pagetitle2pageid2 = {}, {}, {}, {}
    sinimagenes = set()
    interwikis = {}
    imagescommons = set()
    
    dbname = tarea000.getDbname(lenguajeobjetivo, family)
    server = tarea000.getServer(lenguajeobjetivo, family)
    conn = _mysql.connect(host=server, db=dbname, read_default_file='~/.my.cnf')
    dbname = tarea000.getDbname(lenguajefuente, family)
    server = tarea000.getServer(lenguajefuente, family)
    conn2 = _mysql.connect(host=server, db=dbname, read_default_file='~/.my.cnf')
    
    #cargamos pageid/pagetitles para lenguajes objetivos
    print '-'*70
    print 'Loading pageid/pagetitles of %s.%s.org.' % (lenguajeobjetivo, family)
    conn.query("SELECT page_id, page_title FROM page WHERE page_namespace=0 AND page_is_redirect=0")
    r = conn.use_result()
    row = r.fetch_row(maxrows=1, how=1)
    c = 0
    while row:
        if len(row) == 1:
            pageid = int(row[0]['page_id'])
            pagetitle = utf8rm_(row[0]['page_title'])
            c += 1;percent(c)
            #pageid2pagetitle[pageid]=pagetitle
            pagetitle2pageid[pagetitle] = pageid
        row = r.fetch_row(maxrows=1, how=1)
    print '\nLoaded %d pageid/pagetitle of %s.%s.org.' % (c, lenguajeobjetivo, family)

    if c==0: sys.exit()

    #ahora rellenamos sinimagenes con page_ids que no tengan ningún imagelink
    print '-'*70
    print 'Loading imagelinks of %s.%s.org' % (lenguajeobjetivo, family)
    conn.query("SELECT page_id FROM page WHERE page_namespace=0 AND page_is_redirect=0 AND page_id NOT IN (SELECT DISTINCT il_from FROM imagelinks INNER JOIN page ON il_from=page_id WHERE page_namespace=0 AND page_is_redirect=0)")
    r = conn.use_result()
    row = r.fetch_row(maxrows=1, how=1)
    c = 0
    while row:
        if len(row) == 1:
            pageid = int(row[0]['page_id'])
            c+=1;percent(c)
            sinimagenes.add(pageid)
        row = r.fetch_row(maxrows=1, how=1)
    wikipedia.output(u"\nFound %d articles without images in %s.%s.org." % (c, lenguajeobjetivo, family)) #todo: sin ninguna, hasta las que tienen commons.svg se excluyen ?

    #cargamos interwikis a articulos de lenguajeobjetivo carentes de imagenes
    print '-'*70
    print 'Loading interwikis from %s.%s.org to %s.%s.org' % (lenguajefuente, family, lenguajeobjetivo, family)
    conn2.query("SELECT ll_from, page_title, ll_title FROM langlinks INNER JOIN page ON ll_from=page_id WHERE ll_lang=\'%s\';" % lenguajeobjetivo)
    r = conn2.use_result()
    row = r.fetch_row(maxrows=1, how=1)
    c = 0
    while row:
        pageid = int(row[0]['ll_from'])
        pagetitle = utf8rm_(row[0]['page_title'])
        interwiki = utf8rm_(row[0]['ll_title'])
        if pagetitle2pageid.has_key(interwiki) and pagetitle2pageid[interwiki] in sinimagenes:
            #si la pagina a la que apunta el iw existe en el lenguajeobjetivo, y no tiene imagenes...
            c += 1;percent(c)
            interwikis[pageid] = interwiki
            pageid2pagetitle2[pageid] = pagetitle
            #pagetitle2pageid2[pagetitle]=pageid
        row=r.fetch_row(maxrows=1, how=1)
    print '\nLoaded %d pageid/pagetitle (y su interwiki a %s:) de %swiki que tienen iw hacia articulos de %s: sin imagenes' % (c, lenguajeobjetivo, lenguajefuente, lenguajeobjetivo)

    #cargamos imágenes subidas a la inglesa y que cumplan los filtros
    print '-'*70
    print 'Cargando imagenes locales de %s.%s.org' % (lenguajefuente, family)
    images=set()
    filename='/home/emijrp/temporal/enwiki-images.txt'
    try:
        f=open(filename, 'r')
    except:
        os.system('mysql -h enwiki-p.db.toolserver.org -e "use enwiki_p;select img_name from image;" > %s' % filename) #no poner img_width<img_height, ya que hay que tenerlas para descartarlas
        f=open(filename, 'r')
    c=0
    for line in f:
        try:
            line = utf8rm_(line[:-1]) #evitamos \n
        except:
            continue
        trozos = line.split('    ')
        if len(trozos) == 1:
            image = trozos[0]
            if re.search(exclusion_pattern, image): #filtro
                continue
            c+=1;percent(c)
            images.add(image)
            #print image.encode('utf-8')
    print '\nCargadas %d imagenes locales de %s.%s.org (descartando iconos, escudos y http://en.wikipedia.org/wiki/User:Emijrp/Images_for_biographies/Exclusions... )' % (c, lenguajefuente, family)
    f.close()
    
    #cargamos pageid de templates de lenguaje fuente
    print '-'*70
    print 'Cargamos pageid de plantillas de %s.%s.org' % (lenguajefuente, family)
    templatesfuente=set()
    conn2.query("select page_id from page where page_namespace=10;")
    r=conn2.use_result()
    row=r.fetch_row(maxrows=1, how=1)
    c=0
    while row:
        pageid=int(row[0]['page_id'])
        templatesfuente.add(pageid)
        row=r.fetch_row(maxrows=1, how=1)
        c+=1;percent(c)
    wikipedia.output(u"\nCargadas %d plantillas %s.%s.org" % (c, lenguajefuente, family))
    
    #cargamos las imagenes que se usan (y no estan subidas en la inglesa (están en Commons)) y en que articulos se usan
    print '-'*70
    print 'Cargamos imagenes que se usan en %s: y en que articulos' % lenguajefuente #pesado
    candidatas={}
    listanegra=set()
    imagelinks_pattern=re.compile(ur"\((?P<ilfrom>\d+)\,\'(?P<ilto>[^\']+?)\'\)") #no hace falta (?i)
    # (607,'Flag_of_France.svg'),
    filename='/mnt/user-store/%swiki-latest-imagelinks.sql.gz' % lenguajefuente
    f=""
    try:
        f=gzip.open(filename, 'r')
    except:
        os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-imagelinks.sql.gz -O %s' % (lenguajefuente, lenguajefuente, filename))
        f=gzip.open(filename, 'r')
    c=0
    for line in f:
        line=re.sub('_', ' ', line)
        m=imagelinks_pattern.finditer(line)
        for i in m:
            pageid=int(i.group("ilfrom"))
            try:
                image=re.sub('_', ' ', unicode(i.group("ilto"), "utf-8"))
            except:
                wikipedia.output(i.group("ilto"))
                continue
            if image in listanegra: #debe estar lo primero
                continue
            if pageid in templatesfuente: #filtramos las imagenes insertadas por plantillas (cara de einstein en navbox de físcia, etc)
                listanegra.add(image)
                continue
            #filtro
            if re.search(exclusion_pattern, image):
                continue
            #print image.encode('utf-8')
            if image in images: #comprobamos si esta subida a la inglesa
                listanegra.add(image)
                continue
            if not pageid2pagetitle2.has_key(pageid): #si no existe tal pagina en la inglesa, hace falta?
                continue
            if pagetitle2pageid[interwikis[pageid]] not in sinimagenes: #si ya tiene imagen no hace falta seguir
                continue
            c+=1;percent(c)
            #if c % 100 == 0:
            #    print c
            #    linea='[[%s]] -> [[Image:%s]]' % (interwikis[pageid], image)
            #    print linea.encode('utf-8')
            if candidatas.has_key(pageid):
                candidatas[pageid].append(image)
            else:
                candidatas[pageid]=[image]
    print '\nCargadas %d imagenes que se usan en articulos de %s.%s.org y nos pueden servir quizás (candidatas)' % (c, lenguajefuente, family)
    f.close()
    
    #cargamos categorylinks de la inglesa que lleven a una categoria births o deaths, para cribar biografias, que es lo que nos interesa
    categories=set()
    categorylinks_pattern=re.compile(ur"\((?P<pageid>\d+)\,\'\d+ (births|deaths)\'\,\'[^\']*?\'\,\'\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d\'\)") #no hace falta (?i)
    # (1031,'1950 births','Blabla, Antonio',20080805144158)
    filename='/mnt/user-store/%swiki-latest-categorylinks.sql.gz' % lenguajefuente
    f=""
    try:
        f=gzip.open(filename, 'r')
    except:
        os.system('wget http://download.wikimedia.org/%swiki/latest/%swiki-latest-categorylinks.sql.gz -O %s' % (lenguajefuente, lenguajefuente, filename))
        f=gzip.open(filename, 'r')
    c=0
    for line in f:
        line=re.sub('_', ' ', line)
        m=categorylinks_pattern.finditer(line)
        for i in m:
            pageid=int(i.group("pageid"))
            c+=1;percent(c)
            categories.add(pageid)
    print '\nCargados %d categorylinks desde biografias para %s.%s.org' % (c, lenguajefuente, family)
    f.close()

    #cargamos imagenes subidas a commons y que cumplan los filtros
    #lo almacenamos en un fichero para no tener que hacer la query cada vez
    filename='/home/emijrp/temporal/commonswiki-images.txt'
    try:
        f=open(filename, 'r')
    except:
        os.system('mysql -h commonswiki-p.db.toolserver.org -e "use commonswiki_p;select img_name from image where img_width<img_height;" > %s' % filename)
        f=open(filename, 'r')
    c=0
    for line in f:
        try:
            line=unicode(line, 'utf-8')
        except:
            continue
        line=line[:len(line)-1] #evitamos \n
        line=re.sub('_', ' ', line)
        trozos=line.split('    ')
        if len(trozos)==1:
            image=trozos[0]
            #filtro
            if re.search(exclusion_pattern, image):
                continue
            c+=1;percent(c)
            imagescommons.add(image)
            #print image.encode('utf-8')
    print '\nCargadas %d images de commons (descartando iconos, escudos... y width>height)' % (c)
    f.close()

    c=0;cc=0
    f=open('/home/emijrp/temporal/candidatas-%s.txt' % lenguajeobjetivo, 'w')
    g=open('/home/emijrp/temporal/candidatas-%s.sql' % lenguajeobjetivo, 'w')
    for pageid, imagenescandidatas in candidatas.items():
        if pageid not in categories: #no es biografia?
            continue
        article=pageid2pagetitle2[pageid]
        c+=1
        for image in imagenescandidatas:
            iw=interwikis[pageid]
            if re.search(exclusion_pattern, iw):#evitamos imagenes y articulos que no sirven o erroneas que ya se han comprobado en otras actualizacione
                continue
            trocear=' '.join([iw, article]) #para aquellos idiomas como ar: con alfabetos distintos incluimos el nombre en inglés también
            trozos=re.sub(ur'[\(\)]', ur'', trocear).split(' ')
            trozos2=[]
            for t in trozos:
                t=t.strip()
                if len(t)>=3:
                    trozos2.append(t)
            temp="|".join(trozos2)
            
            if re.findall(ur'\|', temp)>=1: #al menos dos palabras para buscar (una|otra)
                if image not in listanegra:
                    if image in imagescommons:
                        if not re.search(exclusion_pattern, image): #evitamos imagenes que no sirven o erroneas que ya se han comprobado en otras actualizaciones
                            if not re.search(ur'([\'\"]|[^\d]0\d\d[^\d])', ' '.join([iw, image])): #?
                                if len(re.findall(ur"(?i)(%s)" % temp, image))>=2: #al menos dos ocurrencias en el nombre del fich
                                    cc+=1
                                    image_=re.sub(' ', '_', image)
                                    md5_=md5.new(image_.encode('utf-8')).hexdigest()
                                    
                                    salida='%s;%s;%s;\n' % (article, iw, image)
                                    salida=salida.encode('utf-8')
                                    
                                    salida2="INSERT INTO `imagesforbio` (`id`, `language`, `article`, `image`, `url`, `done`) VALUES (NULL, '%s', '%s', '%s', 'http://upload.wikimedia.org/wikipedia/commons/%s/%s/%s', 0);\n" % (lenguajeobjetivo, iw, image, md5_[0], md5_[0:2], image_)
                                    salida2=salida2.encode('utf-8')
                                    
                                    try:
                                        f.write(salida)
                                        g.write(salida2)
                                    except:
                                        pass
    f.close()
    g.close()
    conn.close()
    #print '\nFinalmente se encontraron %d articulos susceptibles de ser ilustrados con %d imagenes, en %s:' % (c, cc, lenguajeobjetivo)
    print '\n---->(((((Finalmente se encontraron %d imagenes posiblemente utiles, en %s:)))))<----' % (cc, lenguajeobjetivo)

if __name__ == "__main__":
    main()
