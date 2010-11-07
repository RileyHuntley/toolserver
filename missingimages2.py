# -*- coding: utf-8 -*-

import _mysql
import os
import re
import sqlite3
import sys

import tarea000

bd_cats = { #birth/death categories
    'an': r'[0-9]+_\\((naixencias|muertes)\\)',
    'az': r'[0-9]+.+(doğulanlar|vəfat_edənlər)',
    'eu': r'[0-9]+.+_(jaiotzak|heriotzak)',
}

langs = ['an', 'az', ]#'eu']
family = 'wikipedia'

def percent(c, d=1000):
    if c % d == 0: sys.stderr.write('.') #print '\nLlevamos %d' % c

def utf8rm_(l):
    return re.sub('_', ' ', unicode(l, 'utf-8'))

def createDB(conn=None, cursor=None):
    cursor.execute('''create table pages (page_lang text, page_id integer, page_title text, page_has_images integer)''')
    cursor.execute('''create table imagelinks (il_lang text, il_page integer, il_image_name text)''')
    cursor.execute('''create table langlinks (ll_lang text, ll_page integer, ll_to_lang text, ll_to_title text)''')
    cursor.execute('''create table templateimages (ti_lang text, ti_page integer, ti_image text)''')
    #todo: indices?
    conn.commit()

def main():
    dbfilename = '/home/emijrp/temporal/missingimages.db'
    if os.path.exists(dbfilename):
        os.remove(dbfilename)
    
    conns3 = sqlite3.connect(dbfilename)
    cursors3 = conns3.cursor()
    cursors31 = conns3.cursor()
    cursors32 = conns3.cursor()
    createDB(conn=conns3, cursor=cursors3)
    
    for lang in langs:
        print '==== %s ====' % lang
        dbname = tarea000.getDbname(lang, family)
        server = tarea000.getServer(lang, family)
        conn = _mysql.connect(host=server, db=dbname, read_default_file='~/.my.cnf')

        #bios
        conn.query(r'''
            SELECT DISTINCT page_id, page_title
            FROM categorylinks, page
            WHERE cl_from=page_id AND page_namespace=0 AND cl_to RLIKE '%s'
            ''' % (bd_cats[lang]))
        r = conn.use_result()
        row = r.fetch_row(maxrows=1, how=1)
        c = 0
        while row:
            if len(row) == 1:
                page_id = int(row[0]['page_id'])
                page_title = utf8rm_(row[0]['page_title'])
                cursors3.execute('INSERT INTO pages VALUES (?,?,?,?)', (lang, page_id, page_title, 0))
                c += 1;percent(c)
            row = r.fetch_row(maxrows=1, how=1)
        conns3.commit()
        print '\nLoaded %d bios of %s.%s.org.' % (c, lang, family)
        
        #imagelinks
        conn.query(r'''
            SELECT DISTINCT il_from, page_title, il_to
            FROM imagelinks, page
            WHERE il_from=page_id
                AND il_from IN (
                SELECT DISTINCT cl_from
                FROM categorylinks, page
                WHERE cl_from=page_id AND page_namespace=0 AND cl_to RLIKE '%s'
                )
                AND il_to NOT IN (
                    SELECT DISTINCT il_to
                    FROM imagelinks
                    WHERE il_from IN (
                        SELECT page_id
                        FROM page
                        WHERE page_namespace=10
                        )
                AND il_to NOT IN (
                    SELECT img_name
                    FROM image
                    )
                )
            ''' % (bd_cats[lang]))
        r = conn.use_result()
        row = r.fetch_row(maxrows=1, how=1)
        c = 0
        while row:
            if len(row) == 1:
                il_from = int(row[0]['il_from'])
                page_title = utf8rm_(row[0]['page_title'])
                il_to = utf8rm_(row[0]['il_to'])
                cursors3.execute('INSERT INTO imagelinks VALUES (?,?,?)', (lang, il_from, il_to))
                cursors3.execute('UPDATE pages SET page_has_images=? WHERE page_lang=? AND page_id=? AND page_title=?', (1, lang, il_from, page_title))
                c += 1;percent(c)
            row = r.fetch_row(maxrows=1, how=1)
        conns3.commit()
        print '\nLoaded %d imagelinks of %s.%s.org.' % (c, lang, family)
    
        #interwikis
        conn.query(r'''
            SELECT DISTINCT ll_from, ll_lang, ll_title
            FROM langlinks
            WHERE ll_from IN (
                SELECT DISTINCT page_id
                FROM categorylinks, page
                WHERE cl_from=page_id AND page_namespace=0 AND cl_to RLIKE '%s'
                )
            ''' % (bd_cats[lang]))
        r = conn.use_result()
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
        print '\nLoaded %d langlinks of %s.%s.org.' % (c, lang, family)
        
        #templateimages
        conn.query(r'''
            SELECT DISTINCT il_from, il_to
            FROM imagelinks
            WHERE il_from IN (
                SELECT DISTINCT page_id
                FROM page
                WHERE page_namespace=10
                )
            ''')
        r = conn.use_result()
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
        print '\nLoaded %d templateimages of %s.%s.org.' % (c, lang, family)
        
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
    
    #check for missing images bios
    result = cursors3.execute(r'SELECT page_lang, page_id, page_title FROM pages WHERE page_has_images=?', (0,))
    for row in result:
        page_lang = row[0]
        page_id = int(row[1])
        page_title = row[2]
        
        result2 = cursors31.execute(r'SELECT ll_to_lang, ll_to_title, page_id FROM langlinks, pages WHERE page_lang=ll_to_lang AND page_title=ll_to_title AND ll_lang=? AND ll_page=?', (page_lang, page_id))
        for row2 in result2:
            #print row2
            ll_to_lang = row2[0]
            ll_to_title = row2[1]
            page_id = int(row2[2])
            
            result3 = cursors32.execute(r'SELECT il_image_name FROM imagelinks WHERE il_lang=? AND il_page=?', (ll_to_lang, page_id))
            for row3 in result3:
                il_image_name = row3[0]
                #filter unuseful or wrong images or images inserted with templates
                print "Recomendada la imagen %s de %s: para %s de %s:" % (il_image_name, ll_to_lang, page_title, page_lang)
                #sys.exit()
    
    cursors3.close()
    conns3.close()

if __name__ == "__main__":
    main()
