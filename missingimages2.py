# -*- coding: utf-8 -*-

import _mysql
import md5
import os
import re
import sqlite3
import sys
import MySQLdb
import time

import tarea000
import wikipedia

#todo
#qué hacer con las wikipedias que no tienen categorías de nacimientos y fallecimientos?

bd_cats = { #birth/death categories
    'an': r'\d+_\\((naixencias|muertes)\\)',
    #ar no consigo pegarlo por el lr
    'az': r'\d+.+(doğulanlar|vəfat_edənlər)',
    'bar': r'(Geboren|Gestorben)_\d+',
    'be': r'Нарадзіліся_ў_\d+_годзе', #no tienen de fallecimientos?
    'be-x-old': r'(Нарадзіліся_ў_\d+_годзе|Памерлі_ў_\d+_годзе)',
    'bg': r'(Родени_през_\d+_година|Починали_през_\d+_година)',
    #bn numeros raros
    'br': r'(Ganedigezhioù|Marvioù)_\d+',
    'bs': r'\d+_(rođenja|smrti)',
    #ca not
    'cs': r'(Narození|Úmrtí)_\d+',
    'cy': r'(Genedigaethau|Marwolaethau)_\d+',
    'da': r'(Født|Døde)_i_\d+',
    #de no están interesados, prohiben usar ciertas imágenes de commons (las que no son PD en Alemania, etc)
    #'de': r'(Geboren|Gestorben)_\d+',
    'el': r'(Γεννήσεις_το|Θάνατοι_το)_\d+',
    'en': r'\d+_(births|deaths)',
    'eo': r'(Naskiĝintoj|Mortintoj)_en_\d+',
    'es': r'(Nacidos|Fallecidos)_en_\d+',
    'et': r'(Sündinud|Surnud)_\d+',
    'eu': r'\d+.+_(jaiotzak|heriotzak)',
    #fa numeros raros
    'fr': r'(Naissance|Décès)_en_\d+',
    'ga': r'(Daoine_a_rugadh|Básanna)_i_\d+',
    'gan': r'\d+(年出世|年過世)',
    'hif': r'\d+_(janam|maut)',
    'it': r'(Nati_nel|Morti_nel)_\d+',
    'ja': r'\d+_(年生|年没)',
    #nl hasn't got?
    'no': r'(Fødsler|Dødsfall)_i_\d+',
    'pl': r'(Urodzeni_w|Zmarli_w)_\d+',
    #pt not
    'ru': r'(Умершие|Родившиеся)_в_\d+_году',
    'sv': r'(Födda|Avlidna)_\d+',
    'zh': r'\d+_(年出生|年逝世)',
}

#EXCLUDED PROJECTS
excluded = ['de']
#PROJECTS TO ANALYSE
langs = ['da', 'eo', 'no', 'fr', 'ru', 'es', 'it', 'pl']
#REMOVING DUPES AND EXCLUDED
excluded = set(excluded)
langs = set(langs)
for exc in excluded:
	if exc in langs:
		langs.remove(exc)
family = 'wikipedia'

def percent(c, d=1000):
    if c % d == 0: sys.stderr.write('.') #print '\nLlevamos %d' % c

def utf8rm_(l):
    return re.sub('_', ' ', unicode(l, 'utf-8'))

def createDB(conn=None, cursor=None):
    cursor.execute('''create table pages (page_lang text, page_id integer, page_title text, page_has_images integer)''')
    cursor.execute('''create table imagelinks (il_lang text, il_page integer, il_image_name text)''')
    cursor.execute('''create table langlinks (ll_lang text, ll_page integer, ll_to_lang text, ll_to_title text)''')
    cursor.execute('''create table templateimages (ti_lang text, ti_page integer, ti_image_name text)''')
    cursor.execute('''create table images (img_lang text, img_name text)''')
    cursor.execute('''create table commonsimages (ci_image_name text)''')
    #todo: indices?
    cursor.execute('''create index ind1 on pages (page_lang)''')
    cursor.execute('''create index ind2 on pages (page_lang, page_id)''')
    cursor.execute('''create index ind3 on pages (page_lang, page_id, page_title)''')
    cursor.execute('''create index ind4 on imagelinks (il_lang)''')
    cursor.execute('''create index ind5 on imagelinks (il_lang, il_page)''')
    cursor.execute('''create index ind6 on langlinks (ll_lang)''')
    cursor.execute('''create index ind7 on langlinks (ll_lang, ll_page)''')
    cursor.execute('''create index ind8 on templateimages (ti_lang)''')
    cursor.execute('''create index ind9 on templateimages (ti_lang, ti_page)''')
    cursor.execute('''create index ind10 on images (img_lang)''')
    cursor.execute('''create index ind11 on images (img_lang, img_name)''')
    cursor.execute('''create index ind12 on commonsimages (ci_image_name)''')
    conn.commit()

def main():
    delete = False
    dbfilename = '/mnt/user-store/emijrp/missingimages.db'
    if delete and os.path.exists(dbfilename):
        os.remove(dbfilename)
    
    conns3 = sqlite3.connect(dbfilename)
    cursors3 = conns3.cursor()
    cursors31 = conns3.cursor()
    cursors32 = conns3.cursor()
    if delete: #creamos estructura
        createDB(conn=conns3, cursor=cursors3)
    
    if not delete: #if we do not delete database to conservate commons images info, empty tables of previous analysis
        cursors3.execute('''delete from pages where 1''')
        cursors3.execute('''delete from imagelinks where 1''')
        cursors3.execute('''delete from langlinks where 1''')
        cursors3.execute('''delete from templateimages where 1''')
        cursors3.execute('''delete from images where 1''')
        conns3.commit()
    
    if delete: #si la hemos borrado, recargamos imagenes de commons
        #commons images
        dbname = tarea000.getDbname('en', 'commons')
        server = tarea000.getServer('en', 'commons')
        conn = MySQLdb.connect(host=server, db=dbname, read_default_file='~/.my.cnf')
        t1=time.time()
        conn.query(r'''
            SELECT img_name
            FROM image
            ''')
        r = conn.store_result()
        c = 0
        row = r.fetch_row(maxrows=1, how=1)
        while row:
            if len(row) == 1:
                img_name = utf8rm_(row[0]['img_name'])
                cursors3.execute('INSERT INTO commonsimages VALUES (?)', (img_name,))
                c += 1;percent(c)
            row = r.fetch_row(maxrows=1, how=1)
        conns3.commit()
        print '\nLoaded %d commons images %f' % (c, time.time()-t1)
        #end commons images
    
    for lang in langs:
        print '==== %s ====' % lang
        dbname = tarea000.getDbname(lang, family)
        server = tarea000.getServer(lang, family)
        conn = MySQLdb.connect(host=server, db=dbname, read_default_file='~/.my.cnf')

        #bios
        t1=time.time()
        conn.query(r'''
            SELECT DISTINCT page_id, page_title
            FROM categorylinks, page
            WHERE cl_from=page_id AND page_namespace=0 AND cl_to RLIKE '%s'
            ''' % (bd_cats[lang]))
        r = conn.store_result()
        c = 0
        row = r.fetch_row(maxrows=1, how=1)
        while row:
            if len(row) == 1:
                page_id = int(row[0]['page_id'])
                page_title = utf8rm_(row[0]['page_title'])
                cursors3.execute('INSERT INTO pages VALUES (?,?,?,?)', (lang, page_id, page_title, 0))
                c += 1;percent(c)
            row = r.fetch_row(maxrows=1, how=1)
        conns3.commit()
        print '\nLoaded %d bios of %s.%s.org %f' % (c, lang, family, time.time()-t1)
        
        #imagelinks
        t1=time.time()
        conn.query(r'''
            SELECT DISTINCT il_from, il_to
            FROM imagelinks, page, categorylinks
            WHERE il_from=page_id AND cl_from=page_id AND page_namespace=0 AND cl_to RLIKE '%s'
            ''' % (bd_cats[lang]))
        r = conn.store_result()
        row = r.fetch_row(maxrows=1, how=1)
        c = 0
        while row:
            if len(row) == 1:
                il_from = int(row[0]['il_from'])
                il_to = utf8rm_(row[0]['il_to'])
                cursors3.execute('INSERT INTO imagelinks VALUES (?,?,?)', (lang, il_from, il_to))
                cursors3.execute('UPDATE pages SET page_has_images=? WHERE page_lang=? AND page_id=?', (1, lang, il_from))
                c += 1;percent(c)
            row = r.fetch_row(maxrows=1, how=1)
        conns3.commit()
        print '\nLoaded %d imagelinks of %s.%s.org %f' % (c, lang, family, time.time()-t1)
    
        #interwikis
        t1=time.time()
        conn.query(r'''
            SELECT DISTINCT ll_from, ll_lang, ll_title
            FROM langlinks, page, categorylinks
            WHERE ll_from=page_id AND cl_from=page_id AND page_namespace=0 AND cl_to RLIKE '%s'
            ''' % (bd_cats[lang]))
        r = conn.store_result()
        row = r.fetch_row(maxrows=1, how=1)
        c = 0
        while row:
            if len(row) == 1:
                ll_from = int(row[0]['ll_from'])
                ll_lang = utf8rm_(row[0]['ll_lang'])
                ll_title = utf8rm_(row[0]['ll_title'])
                cursors3.execute('INSERT INTO langlinks VALUES (?,?,?,?)', (lang, ll_from, ll_lang, ll_title))
                c += 1;percent(c)
            row = r.fetch_row(maxrows=1, how=1)
        conns3.commit()
        print '\nLoaded %d langlinks of %s.%s.org %f' % (c, lang, family, time.time()-t1)
        
        #templateimages
        t1=time.time()
        conn.query(r'''
            SELECT DISTINCT il_from, il_to
            FROM imagelinks, page
            WHERE il_from=page_id AND page_namespace=10
            ''')
        r = conn.store_result()
        row = r.fetch_row(maxrows=1, how=1)
        c = 0
        while row:
            if len(row) == 1:
                il_from = int(row[0]['il_from'])
                il_to = utf8rm_(row[0]['il_to'])
                cursors3.execute('INSERT INTO templateimages VALUES (?,?,?)', (lang, il_from, il_to))
                c += 1;percent(c)
            row = r.fetch_row(maxrows=1, how=1)
        conns3.commit()
        print '\nLoaded %d templateimages of %s.%s.org %f' % (c, lang, family, time.time()-t1)
        
        #images
        t1=time.time()
        conn.query(r'''
            SELECT img_name
            FROM image
            ''')
        r = conn.store_result()
        row = r.fetch_row(maxrows=1, how=1)
        c = 0
        while row:
            if len(row) == 1:
                img_name = utf8rm_(row[0]['img_name'])
                cursors3.execute('INSERT INTO images VALUES (?,?)', (lang, img_name))
                c += 1;percent(c)
            row = r.fetch_row(maxrows=1, how=1)
        conns3.commit()
        print '\nLoaded %d localimages of %s.%s.org %f' % (c, lang, family, time.time()-t1)
        
        conn.close()
    
    bios = 0
    bioswithout = 0
    result = cursors3.execute(r'SELECT count(*) FROM pages')
    for row in result:
        bios = int(row[0])
    result = cursors3.execute(r'SELECT count(*) FROM pages WHERE page_has_images=?', (0,))
    for row in result:
        bioswithout = int(row[0])
    print 'There are %d bios without images (%.2f%%)' % (bioswithout, bioswithout/(bios/100.0))
    
    #filters
    ex = ur'(?i)(%s)' % ('|'.join(wikipedia.Page(wikipedia.Site("en", "wikipedia"), u"User:Emijrp/Images for biographies/Exclusions").get().splitlines()))
    exclusion_pattern=re.compile(ex) # los ' y " los filtramos al final
    #check for missing images bios
    result = cursors3.execute(r'SELECT page_lang, page_id, page_title FROM pages WHERE page_has_images=?', (0,))
    cc = 0
    candfile = '/home/emijrp/temporal/candidatas.sql'
    f = open(candfile, 'w')
    t1=time.time()
    for row in result:
        page_lang = row[0]
        page_id = int(row[1])
        page_title = row[2]
        
        candidatas = {}
        result2 = cursors31.execute(r'SELECT ll_to_lang, ll_to_title, page_id FROM langlinks, pages WHERE page_lang=ll_to_lang AND page_title=ll_to_title AND ll_lang=? AND ll_page=?', (page_lang, page_id))
        for row2 in result2:
            #print row2
            ll_to_lang = row2[0]
            ll_to_title = row2[1]
            ll_to_page = int(row2[2])
            
            result3 = cursors32.execute(r'SELECT il_image_name FROM imagelinks WHERE il_lang=? AND il_page=? AND il_image_name NOT IN (SELECT ti_image_name FROM templateimages WHERE ti_lang=?) AND il_image_name NOT IN (SELECT img_name FROM images WHERE img_lang=?) AND il_image_name IN (SELECT ci_image_name FROM commonsimages)', (ll_to_lang, ll_to_page, ll_to_lang, ll_to_lang)) #miramos las imágenes que usan las bios de los iws, excepto aquellas que están integradas en plantillas locales, o son imagenes locales
            for row3 in result3:
                il_image_name = row3[0]
                #filter unuseful or wrong images or images inserted with templates
                if re.search(exclusion_pattern, '%s %s' % (page_title, ll_to_title)):
                    #evitamos imagenes y articulos que no sirven o erroneas que ya se han comprobado en otras actualizacione
                    continue
                trocear = ' '.join([page_title, ll_to_title])
                #para aquellos idiomas como ar: con alfabetos distintos incluimos ambos títulos
                trozos = '|'.join([trozo for trozo in re.sub(ur'[\(\)]', ur'', trocear).split(' ') if len(trozo) >= 3])
                if len(re.findall(ur'\|', trozos)) >= 1: #al menos dos palabras para buscar (una|otra)
                    if not re.search(exclusion_pattern, il_image_name): #evitamos imagenes que no sirven o erroneas que ya se han comprobado en otras actualizaciones
                        if not re.search(ur'([\'\"]|[^\d]0\d\d[^\d])', ' '.join([page_title, ll_to_title, il_image_name])): #?
                            if len(re.findall(ur"(?i)(%s)" % trozos, il_image_name)) >= 2: #al menos dos ocurrencias en el nombre del fich
                                #ok il_image_name es una buena candidata
                                if candidatas.has_key(il_image_name):
                                    candidatas[il_image_name] += 1
                                else:
                                    candidatas[il_image_name] = 1
        
        #sort and choice the best candidate
        if candidatas:
            cand_list = [[v,k] for k,v in candidatas.items()]
            cand_list.sort()
            cand_list.reverse()
            
            il_image_name = cand_list[0][1]
            cc += 1
            il_image_name_ = re.sub(' ', '_', il_image_name)
            md5_ = md5.new(il_image_name_.encode('utf-8')).hexdigest()
            salida = "INSERT INTO `imagesforbio` (`id`, `language`, `article`, `image`, `url`, `done`) VALUES (NULL, '%s', '%s', '%s', 'http://upload.wikimedia.org/wikipedia/commons/%s/%s/%s', 0);\n" % (page_lang, page_title, il_image_name, md5_[0], md5_[0:2], il_image_name_)
            #print "Recomendada la imagen '%s' para la bio '%s' de %s:" % (il_image_name, page_title, page_lang)
            
            try:
                f.write(salida.encode('utf-8'))
            except:
                print "ERROR while writing to output file"
            
    f.close()
    cursors3.close()
    conns3.close()
    
    print '\n---->(((((Finalmente se encontraron %d imagenes posiblemente utiles %f)))))<----' % (cc, time.time()-t1)
    for lang in langs:
        os.system('mysql -h sql -e "use u_emijrp_yarrow;delete from imagesforbio where language=\'%s\';"' % lang)
    os.system('mysql -h sql u_emijrp_yarrow < %s' % candfile)

if __name__ == "__main__":
    main()
