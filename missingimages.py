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
    'hif': r'[0-9]+_(janam|maut)',
    'hsb': r'(Rodź|Zemr)\._[0-9]+',
    'hy': r'[0-9]+_(ծնունդներ|մահեր)',
    'id': r'(Kelahiran|Kematian)_[0-9]+',
    'is': r'(Fólk_fætt_árið|Fólk_dáið_árið)_[0-9]+',
    'it': r'(Nati_nel|Morti_nel)_[0-9]+',
    'ja': r'[0-9]+(年生|年没)',
    'ka': r'(დაბადებული|გარდაცვლილი)_[0-9]+',
    'kk': r'[0-9]+(жылы_туғандар|жылы_қайтыс_болғандар)',
    'ko': r'[0-9]+(년 태어남|년 죽음)',
    'la': r'(Nati|Mortui)_[0-9]+',
    'lb': r'(Gebuer|Gestuerwen)_[0-9]+',
    'lv': r'[0-9]+\._(gadā_dzimušie|gadā_mirušie)',
    'mk': r'(Родени_во_[0-9]+_година|Починати_во_[0-9]+_година)',
    'ml': r'[0-9]+(\-ൽ_ജനിച്ചവർ|\-ൽ മരിച്ചവർ)',
    #mr numeros raros
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
    #error por el codigo del lenguaje? 'simple': r'[0-9]+_(births|deaths)',
    'sh': r'(Rođeni|Umrli)_[0-9]+\.',
    'sk': r'(Narodenia|Úmrtia)_v_[0-9]+',
    'sl': r'(Rojeni|Umrli)_leta_[0-9]+',
    'sq': r'(Lindje|Vdekje)_[0-9]+',
    'sr': r'(Рођени|Умрли)_[0-9]+\.',
    'sv': r'(Födda|Avlidna)_[0-9]+',
    'sw': r'(Waliozaliwa|Waliofariki)_[0-9]+',
    'ta': r'[0-9]+_(பிறப்புகள்|இறப்புகள்)',
    'te': r'[0-9]+_(జననాలు|మరణాలు)',
    'th': r'(บุคคลที่เกิดในปี_พ\.ศ\.|บุคคลที่เสียชีวิตในปี_พ\.ศ\.)_[0-9]+',
    'tl': r'(Ipinanganak|Namatay)_noong_[0-9]+',
    'tr': r'[0-9]+_(doğumlular|yılında_ölenler)',
    'uk': r'(Народились|Померли)_[0-9]+',
    'vi': r'(Sinh|Mất)_[0-9]+',
    'yo': r'(Àwọn_ọjọ́ìbí|Àwọn_ọjọ́aláìsí)_ní_[0-9]+',
    'zh': r'[0-9]+(年出生|年逝世)',
    'zh-yue': r'[0-9]+(年出世|年死)',
}

#EXCLUDED PROJECTS
excluded = set(['de'])
#ALL PROJECTS
alllangs = set(bd_cats.keys()) - excluded
#PROJECTS TO ANALYSE
langs = set(['da', 'eo', 'no', 'fr', 'ru', 'es', 'it', 'pl', 'fi', 'is', 'ja', 'sl', 'sk', ])
#['ab', 'af', 'ak', 'als', 'am', 'an', 'ang', 'ar', 'arc', 'arz', 'as', 'ast', 'av', 'ay', 'az', 'ba', 'bar', 'bat-smg', 'bcl', 'be', 'be-x-old', 'bg', 'bh', 'bi', 'bm', 'bn', 'bo', 'bpy', 'br', 'bs', 'bug', 'bxr', 'ca', 'cbk-zam', 'cdo', 'ce', 'ceb', 'ch', 'cho', 'chr', 'chy', 'closed-zh-tw', 'co', 'cr', 'crh', 'cs', 'csb', 'cu', 'cv', 'cy', 'cz', 'da', 'de', 'diq', 'dk', 'dsb', 'dv', 'dz', 'ee', 'el', 'eml', 'en', 'eo', 'epo', 'es', 'et', 'eu', 'ext', 'fa', 'ff', 'fi', 'fiu-vro', 'fj', 'fo', 'fr', 'frp', 'fur', 'fy', 'ga', 'gan', 'gd', 'gl', 'glk', 'gn', 'got', 'gu', 'gv', 'ha', 'hak', 'haw', 'he', 'hi', 'hif', 'ho', 'hr', 'hsb', 'ht', 'hu', 'hy', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'ilo', 'io', 'is', 'it', 'iu', 'ja', 'jbo', 'jp', 'jv', 'ka', 'kaa', 'kab', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'ksh', 'ku', 'kv', 'kw', 'ky', 'la', 'lad', 'lb', 'lbe', 'lg', 'li', 'lij', 'lmo', 'ln', 'lo', 'lt', 'lv', 'map-bms', 'mdf', 'mg', 'mh', 'mi', 'minnan', 'mk', 'ml', 'mn', 'mo', 'mr', 'ms', 'mt', 'mus', 'my', 'myv', 'mzn', 'na', 'nah', 'nan', 'nap', 'nb', 'nds', 'nds-nl', 'ne', 'new', 'ng', 'nl', 'nn', 'no', 'nomcom', 'nov', 'nrm', 'nv', 'ny', 'oc', 'om', 'or', 'os', 'pa', 'pag', 'pam', 'pap', 'pdc', 'pi', 'pih', 'pl', 'pms', 'ps', 'pt', 'qu', 'rm', 'rmy', 'rn', 'ro', 'roa-rup', 'roa-tara', 'ru', 'rw', 'sa', 'sah', 'sc', 'scn', 'sco', 'sd', 'se', 'sg', 'sh', 'si', 'simple', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'srn', 'ss', 'st', 'stq', 'su', 'sv', 'sw', 'szl', 'ta', 'te', 'tet', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tokipona', 'tp', 'tpi', 'tr', 'ts', 'tt', 'tum', 'tw', 'ty', 'udm', 'ug', 'uk', 'ur', 'uz', 've', 'vec', 'vi', 'vls', 'vo', 'wa', 'war', 'wo', 'wuu', 'xal', 'xh', 'yi', 'yo', 'za', 'zea', 'zh', 'zh-cfr', 'zh-classical', 'zh-min-nan', 'zh-yue', 'zu']
#REMOVING DUPES AND EXCLUDED
langs = langs - excluded
family = 'wikipedia'

if len(sys.argv) == 2 and sys.argv[1].lower() == 'all':
    print 'Analysing all available languages'
    langs = alllangs

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
    delete = True
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
        percent(c=cc, d=10)
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
