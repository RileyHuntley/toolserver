# -*- coding: utf-8 -*-

# Copyright (C) 2011 emijrp
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

#http://en.wikipedia.org/wiki/Category:Rivers_by_country
river_cats = {
    'an': r'Ríos_d',
    'az': r'.+_çayları',
    'be': r'Рэкі_.+',
    'en': r'Rivers_of_',
    'eu': r'.+_ibaiak',
    'fr': r'Cours_d\'eau_',
    'zh-min-nan': r'.+_ê_hô',
}

#no usar \d+ sino [0-9]+
bd_cats = { #birth/death categories
    'an': r'[0-9]+_\\((naixencias|muertes)\\)',
    #ar no consigo pegarlo por el lr
    #arz problemas lr
    'az': r'[0-9]+.+(doğulanlar|vəfat_edənlər)',
    'bar': r'(Geboren|Gestorben)_[0-9]+',
    'be': r'Нарадзіліся_ў_[0-9]+_годзе', #no tienen de fallecimientos?
    'be-x-old': r'(Нарадзіліся_ў_[0-9]+_годзе|Памерлі_ў_[0-9]+_годзе)',
    'bg': r'(Родени_през_[0-9]+_година|Починали_през_[0-9]+_година)',
    #bn numeros raros
    #bpy numeros raros
    'br': r'(Ganedigezhioù|Marvioù)_[0-9]+',
    'bs': r'[0-9]+_(rođenja|smrti)',
    #ca not
    'crh': r'[0-9]+_senesinde_(doğğanlar|ölgenler)',
    'cs': r'(Narození|Úmrtí)_[0-9]+',
    'cy': r'(Genedigaethau|Marwolaethau)_[0-9]+',
    'da': r'(Født|Døde)_i_[0-9]+',
    #de no están interesados, prohiben usar ciertas imágenes de commons (las que no son PD en Alemania, etc)
    #'de': r'(Geboren|Gestorben)_[0-9]+',
    'dsb': r'(Roź|Wum)\._[0-9]+',
    'ee': r'[0-9]+_(vidzidziwo|kuwo)',
    'el': r'(Γεννήσεις_το|Θάνατοι_το)_[0-9]+',
    'en': r'[0-9]+_(births|deaths)',
    'eo': r'(Naskiĝintoj|Mortintoj)_en_[0-9]+',
    'es': r'(Nacidos|Fallecidos)_en_[0-9]+',
    'et': r'(Sündinud|Surnud)_[0-9]+',
    'eu': r'[0-9]+.+_(jaiotzak|heriotzak)',
    #fa numeros raros
    'fi': r'Vuonna_[0-9]+_(syntyneet|kuolleet)',
    'fr': r'(Naissance|Décès)_en_[0-9]+',
    'ga': r'(Daoine_a_rugadh|Básanna)_i_[0-9]+',
    'gan': r'[0-9]+(年出世|年過世)',
    'gl': r'(Nados|Finados)_en_[0-9]+',
    'hif': r'[0-9]+_(janam|maut)',
    'hsb': r'(Rodź|Zemr)\._[0-9]+',
    'hy': r'[0-9]+_(ծնունդներ|մահեր)',
    'id': r'(Kelahiran|Kematian)_[0-9]+',
    'is': r'(Fólk_fætt_árið|Fólk_dáið_árið)_[0-9]+',
    'it': r'(Nati_nel|Morti_nel)_[0-9]+',
    'ja': r'[0-9]+(年生|年没)',
    'ka': r'(დაბადებული|გარდაცვლილი)_[0-9]+',
    'kk': r'[0-9]+_(жылы_туғандар|жылы_қайтыс_болғандар)',
    'ko': r'[0-9]+(년 태어남|년 죽음)',
    'la': r'(Nati|Mortui)_[0-9]+',
    'lb': r'(Gebuer|Gestuerwen)_[0-9]+',
    'lv': r'[0-9]+\._(gadā_dzimušie|gadā_mirušie)',
    'mk': r'(Родени_во_[0-9]+_година|Починати_во_[0-9]+_година)',
    'ml': r'[0-9]+(\-ൽ_ജനിച്ചവർ|\-ൽ മരിച്ചവർ)',
    'mn': r'[0-9]+_(онд_төрөгсөд|онд_нас_барагсад)',
    #mr numeros raros
    'ms': r'(Kelahiran|Kematian)_[0-9]+',
    'mt': r'(Twieldu_fl\-|Mietu_fl\-)[0-9]+',
    #new numeros raros
    #nl hasn't got?
    'nn': r'(Fødde|Døde)_i_[0-9]+',
    'no': r'(Fødsler|Dødsfall)_i_[0-9]+',
    'oc': r'(Naissença|Decès)_en_[0-9]+',
    'pl': r'(Urodzeni|Zmarli)_w_[0-9]+',
    #pt not
    'qu': r'(Paqarisqa|Wañusqa)_[0-9]+',
    'ro': r'(Nașteri|Decese)_în_[0-9]+',
    'ru': r'(Умершие|Родившиеся)_в_[0-9]+_году',
    'sah': r'[0-9]+_(сыллаахха_төрөөбүттэр|сыллаахха_өлбүттэр)',
    'se': r'(Riegádeamit|Jápmimat)_[0-9]+',
    #error por el codigo del lenguaje? 'simple': r'[0-9]+_(births|deaths)',
    'sh': r'(Rođeni|Umrli)_[0-9]+\.',
    'si': r'[0-9]+_(උපත්|මරණ)',
    'sk': r'(Narodenia|Úmrtia)_v_[0-9]+',
    'sl': r'(Rojeni|Umrli)_leta_[0-9]+',
    'sq': r'(Lindje|Vdekje)_[0-9]+',
    'sr': r'(Рођени|Умрли)_[0-9]+\.',
    'su': r'(Nu_babar_taun|Nu_pupus_taun)_[0-9]+',
    'sv': r'(Födda|Avlidna)_[0-9]+',
    'sw': r'(Waliozaliwa|Waliofariki)_[0-9]+',
    'szl': r'(Rodzyńi_we|Umarći_we)_[0-9]+',
    'ta': r'[0-9]+_(பிறப்புகள்|இறப்புகள்)',
    'te': r'[0-9]+_(జననాలు|మరణాలు)',
    'th': r'(บุคคลที่เกิดในปี_พ\.ศ\.|บุคคลที่เสียชีวิตในปี_พ\.ศ\.)_[0-9]+',
    'tl': r'(Ipinanganak|Namatay)_noong_[0-9]+',
    'tr': r'[0-9]+_(doğumlular|yılında_ölenler)',
    'tt': r'[0-9]+_(елда_туганнар|елда_вафатлар)',
    'uk': r'(Народились|Померли)_[0-9]+',
    'uz': r'[0-9]+\-(yilda_tugʻilganlar|yilda_vafot_etganlar)',
    'vi': r'(Sinh|Mất)_[0-9]+',
    'yo': r'(Àwọn_ọjọ́ìbí|Àwọn_ọjọ́aláìsí)_ní_[0-9]+',
    'zh': r'[0-9]+(年出生|年逝世)',
    'zh-yue': r'[0-9]+(年出世|年死)',
}

cats = {}
subproject = ''
if len(sys.argv) == 3:
    if sys.argv[1].lower() == 'bios':
        cats = bd_cats
        subproject = 'bios'
    elif sys.argv[1].lower() == 'rivers':
        cats = river_cats
        subproject = 'rivers'
    else:
        print 'Missing parameters: python missingimages.py [bios|rivers] [all|big|small|test|testen]'
        sys.exit()

#http://meta.wikimedia.org/wiki/List_of_Wikipedias
langs = set([])
#EXCLUDED PROJECTS
excluded = set(['de']) # de doesn't allow paintings as pics
#ALL PROJECTS
alllangs = set(cats.keys()) - excluded
#PROJECTS TO ANALYSE
biglangs = set(['en', 'fr', 'it', 'pl', 'es', 'ja', 'nl', 'ru', 'pt', 'sv', 'zh', 'ca', 'no', 'uk', 'fi', 'vi', 'cs', 'hu', 'tr', 'id', 'ko', 'ro', 'fa', 'da', 'ar', 'eo', 'sr', 'lt', 'sk', 'he', 'ms', 'sl', 'vo', 'bg', 'eu', 'war', 'hr', ]) #biggest wikipedias (over 100k articles) except DE
testlangs = set(['qu', 'yo', 'cy', 'tl', 'kk']) #some minor languages for testing
testenlangs = set(['en', 'fr'])
smalllangs = alllangs - biglangs
family = 'wikipedia'

if sys.argv[2].lower() == 'all':
    print 'Analysing all available languages excluding: %s' % (', '.join(excluded))
    langs = alllangs
elif sys.argv[2].lower() == 'big':
    print 'Analysing only big languages'
    langs = biglangs
elif sys.argv[2].lower() == 'small':
    print 'Analysing only small languages'
    langs = smalllangs
elif sys.argv[2].lower() == 'test':
    print 'Analysing some minor languages for testing'
    langs = testlangs
elif sys.argv[2].lower() == 'testen':
    print 'Analysing en: and other language for testing'
    langs = testenlangs
else:
    print 'Missing parameters: python missingimages.py [bios|rivers] [all|big|small|test|testen]'
    sys.exit()

#REMOVING DUPES AND EXCLUDED
langs = langs - excluded
#REMOVING LANGUAGES WHICH HAVE NOT BIOGRAPHICAL CATEGORY INFO
langs = langs & set(cats.keys()) # conjuction

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
    t2 = time.time()
    delete = False #delete database
    commitlimit = 10000
    dbfilename = '/mnt/user-store/emijrp/missingimages%s.db' % (subproject)
    create = False #create database structure
    if os.path.exists(dbfilename):
        if delete:
            os.remove(dbfilename)
    else:
        delete = True
        create = True
    
    #filters
    ex = ur'(?i)(%s)' % ('|'.join(wikipedia.Page(wikipedia.Site("en", "wikipedia"), u"User:Emijrp/Images for biographies/Exclusions").get().splitlines()))
    exclusion_pattern = re.compile(ex) # los ' y " los filtramos al final
    
    #db
    conns3 = sqlite3.connect(dbfilename)
    cursors3 = conns3.cursor()
    cursors31 = conns3.cursor()
    cursors32 = conns3.cursor()
    if delete or create: #creamos estructura
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
            /* missingimages.py SLOW_OK */ 
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
    
    print 'We are going to analyse %d langs: %s' % (len(langs), ', '.join(langs))
    for lang in langs:
        print '==== %s ====' % lang
        dbname = tarea000.getDbname(lang, family)
        server = tarea000.getServer(lang, family)
        conn = MySQLdb.connect(host=server, db=dbname, read_default_file='~/.my.cnf')

        #bios
        t1=time.time()
        conn.query(r'''
            /* missingimages.py SLOW_OK */
            SELECT DISTINCT page_id, page_title
            FROM categorylinks, page
            WHERE cl_from=page_id AND page_namespace=0 AND cl_to RLIKE '%s'
            ''' % (cats[lang]))
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
            if c % commitlimit == 0: conns3.commit()
        conns3.commit()
        print '\nLoaded %d %s of %s.%s.org %f' % (c, subproject, lang, family, time.time()-t1)
        
        #imagelinks
        t1=time.time()
        conn.query(r'''
            /* missingimages.py SLOW_OK */
            SELECT DISTINCT il_from, il_to
            FROM imagelinks, page, categorylinks
            WHERE il_from=page_id AND cl_from=page_id AND page_namespace=0 AND cl_to RLIKE '%s'
            ''' % (cats[lang]))
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
            if c % commitlimit == 0: conns3.commit()
        conns3.commit()
        print '\nLoaded %d imagelinks of %s.%s.org %f' % (c, lang, family, time.time()-t1)
    
        #interwikis
        t1=time.time()
        conn.query(r'''
            /* missingimages.py SLOW_OK */
            SELECT DISTINCT ll_from, ll_lang, ll_title
            FROM langlinks, page, categorylinks
            WHERE ll_from=page_id AND cl_from=page_id AND page_namespace=0 AND cl_to RLIKE '%s'
            ''' % (cats[lang]))
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
            if c % commitlimit == 0: conns3.commit()
        conns3.commit()
        print '\nLoaded %d langlinks of %s.%s.org %f' % (c, lang, family, time.time()-t1)
        
        #templateimages
        t1=time.time()
        conn.query(r'''
            /* missingimages.py SLOW_OK */
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
            if c % commitlimit == 0: conns3.commit()
        conns3.commit()
        print '\nLoaded %d templateimages of %s.%s.org %f' % (c, lang, family, time.time()-t1)
        
        #images
        t1=time.time()
        conn.query(r'''
            /* missingimages.py SLOW_OK */
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
            if c % commitlimit == 0: conns3.commit()
        conns3.commit()
        print '\nLoaded %d localimages of %s.%s.org %f' % (c, lang, family, time.time()-t1)
        
        conn.close()
    
    arts = 0
    artswithout = 0
    result = cursors3.execute(r'SELECT count(*) FROM pages')
    for row in result:
        arts = int(row[0])
    result = cursors3.execute(r'SELECT count(*) FROM pages WHERE page_has_images=?', (0,))
    for row in result:
        artswithout = int(row[0])
    print 'There are %d %s without images (%.2f%%)' % (artswithout, subproject, artswithout/(arts/100.0))
    
    #check for missing images bios
    result = cursors3.execute(r'SELECT page_lang, page_id, page_title FROM pages WHERE page_has_images=?', (0,))
    cc = 0
    candfile = '/home/emijrp/temporal/candidatas%s.sql' % (subproject)
    f = open(candfile, 'w')
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
                
                #para bios al menos dos palabras para buscar (una|otra)
                #para rivers una palabra de 3 o más caracteres
                if (subproject == 'bios' and len(re.findall(ur'\|', trozos)) >= 1) or \
                   (subproject == 'rivers' and len(trozos) >= 3): 
                    if not re.search(exclusion_pattern, il_image_name): #evitamos imagenes que no sirven o erroneas que ya se han comprobado en otras actualizaciones
                        if not re.search(ur'([\'\"\&]|[^\d]0\d\d[^\d])', ' '.join([page_title, ll_to_title, il_image_name])):
                            #excluimos imágenes con ' " en el título que causan errores al generar el sql de candidatas y & en el PHP, también listados de imágenes 001, 002, 003...
                            if len(re.findall(ur"(?i)(%s)" % trozos, il_image_name)) >= 2: #al menos dos ocurrencias en el nombre del fich
                                #ok il_image_name es una buena candidata
                                if candidatas.has_key(il_image_name):
                                    candidatas[il_image_name] += 1
                                else:
                                    candidatas[il_image_name] = 1
        
        #sort and choice the best candidate
        if candidatas:
            cand_list = [[v, k] for k, v in candidatas.items()]
            cand_list.sort()
            cand_list.reverse()
            
            il_image_name = cand_list[0][1] #we choose the most used image on candidate list
            cc += 1;percent(c=cc, d=10)
            il_image_name_ = re.sub(' ', '_', il_image_name)
            md5_ = md5.new(il_image_name_.encode('utf-8')).hexdigest()
            salida = "INSERT INTO `imagesfor%s` (`id`, `language`, `article`, `image`, `url`, `done`) VALUES (NULL, '%s', '%s', '%s', 'http://upload.wikimedia.org/wikipedia/commons/%s/%s/%s', 0);\n" % (subproject, page_lang, page_title, il_image_name, md5_[0], md5_[0:2], il_image_name_)
            #print "Recomendada la imagen '%s' para la bio '%s' de %s:" % (il_image_name, page_title, page_lang)
            
            try:
                f.write(salida.encode('utf-8'))
            except:
                print "ERROR while writing to output file"
            
    f.close()
    cursors3.close()
    conns3.close()
    
    print '\n---->(((((Finalmente se encontraron %d imagenes posiblemente utiles en %d segundos [%.2f horas])))))<----' % (cc, time.time()-t2, (time.time()-t2)/3600)
    for lang in langs:
        os.system('mysql -h sql -e "use u_emijrp_yarrow;delete from imagesfor%s where language=\'%s\';"' % (subproject, lang))
    os.system('mysql -h sql u_emijrp_yarrow < %s' % (candfile))

if __name__ == "__main__":
    main()
