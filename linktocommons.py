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

import wikipedia, os, sys, re, time
import MySQLdb
import tarea000

def percent(c):
    if c % 10000 == 0:
        print 'Llevamos %d' % c

lang = 'en'
if len(sys.argv) >= 2:
    lang = sys.argv[1]
family = 'wikipedia'

plantillas = {
    'af':[u'Commons', u'CommonsKategorie', u'Commonscat', u'CommonsKategorie-inlyn'],
    'az':[u'Commons', u'Commons2', u'Commons3', u'CommonsKat', u'Commonscat', u'Commonskat', u'CommonsKat2', u'CommonsKat3'],
    'de':[u'Commons', u'Commonscat', u'CommonsCat'],
    'eo':[u'Commons', u'Commonscat'],
    'es':[u'Commonscat', u'Commons cat', u'Ccat', u'Commons'],
    'en':[u'Commons',u'Commons+cat',u'Pic',u'Commonspar',u'Commonspiped',u'Commonsme',u'Siisterlinkswp',u'Wikicommons',u'Commons-gallery',u'Gallery-link',u'Commons cat',u'Commonscat',u'Commons2',u'CommonsCat',u'Cms-catlit-up',u'Catlst commons',u'Commonscategory',u'Commonscat',u'Commonscat-inline',u'Commons cat left',u'Commons cat multi',u'Commons page',u'Commons-inline',u'Commonstiny',u'Commonstmp',u'Sistercommons',u'Sisterlinks',u'Sisterlinks2'],
    'hu':[u'Commons',u'Közvagyonkat',u'Commons-natúr',u'Taxobox'], #taxobox por http://hu.wikipedia.org/w/index.php?title=Szerkeszt%C5%91vita:Syp/Arch%C3%ADv06&diff=next&oldid=4606364#Taxobox_and_BOTijo
    #'it':[u'Commons',u'Commonscat'],
    'pt':[u'Commons',u'Commons1',u'Commonscat',u'Commons2',u'Correlato/commons',u'Correlatos'],
    'sl':[u'Commons',u'Zbirka'],
    'tr':[u'Commons',u'CommonsKatÇoklu',u'CommonsKat',u'Commonscat',u'Commons cat',u'CommonsKat-ufak',u'Commons1',u'Commons-ufak'],
}

regexp = {
    'af': ur'(?im)(^\=+ *Eksterne skakels *\=+$)',
    'az': ur'(?im)(^\=+ *Xarici keçidlər *\=+$)',
    'de': ur'(?im)(^\=+ *Weblinks *\=+$)',
    'eo': ur'(?im)(^\=+ *Eksteraj ligoj *\=+$)',
    'es': ur'(?im)(^\=+ *Enlaces externos *\=+$)',
    'en': ur'(?im)(^\=+ *External links *\=+$)',
    'hu': ur'(?im)(^\=+ *Külső hivatkozások *\=+$)',
    'pt': ur'(?im)(^\=+ *\{\{ *Ligações externas *\}\} *\=+$)',
    'sl': ur'(?im)(^\=+ *Zunanje povezave *\=+$)',
    'tr': ur'(?im)(^\=+ *Dış bağlantılar *\=+$)',
}

summaries = {
    'en': u'Adding link to Commons',
    'es': u'Añadiendo enlace a Commons',
    'pt': u'Adicionando ligação ao Commons',
}

dbname = tarea000.getDbname('en', 'commons')
server = tarea000.getServer('en', 'commons')
conncommons = MySQLdb.connect(host=server, db=dbname, read_default_file='~/.my.cnf')
dbname = tarea000.getDbname(lang, family)
server = tarea000.getServer(lang, family)
connlang = MySQLdb.connect(host=server, db=dbname, read_default_file='~/.my.cnf')

commons = {}
conncommons.query(r'''
    SELECT DISTINCT page_id, page_title, ll_title
    FROM langlinks, page
    WHERE ll_lang='%s' and page_id=ll_from and page_namespace=0;
    ''' % (lang))
r = conncommons.store_result()
c = 0
row = r.fetch_row(maxrows=1, how=1)
while row:
    if len(row) == 1:
        page_id = int(row[0]['page_id'])
        page_title = re.sub('_', ' ', unicode(row[0]['page_title'], 'utf-8'))
        ll_title = re.sub('_', ' ', unicode(row[0]['ll_title'], 'utf-8'))
        commons[page_id] = [page_title, ll_title, 0]
        c += 1;percent(c)
    row = r.fetch_row(maxrows=1, how=1)

print 'Cargados %d pageid/pagetitle/lltitle para commons con interwiki a %s:' % (c, lang)

#que paginas de lang.wikipedia.org tienen ya enlace hacia commons?
evitar=u'' #lo dejamos en blanco para que falle si no tenemos plantillas para cierto idioma
if plantillas.has_key(lang):
    for k in plantillas[lang]:
        evitar+=u'tl_title=\'%s\' or ' % re.sub(' ', '_', k)
    evitar=evitar[:len(evitar)-4]
wikipedia.output(evitar)

usocommons=set()
connlang.query(r'''
    SELECT DISTINCT page_title
    FROM templatelinks, page
    WHERE tl_from=page_id and page_namespace=0 and page_is_redirect=0 and (%s);
    ''' % (evitar.encode('utf-8')))
r = connlang.store_result()
c = 0
row = r.fetch_row(maxrows=1, how=1)
while row:
    if len(row) == 1:
        #page_id = int(row[0]['page_id'])
        page_title = re.sub('_', ' ', unicode(row[0]['page_title'], 'utf-8'))
        usocommons.add(page_title)
        c += 1;percent(c)
    row = r.fetch_row(maxrows=1, how=1)

print 'Cargados %d pageid/pagetitle de paginas de %s: que ya apuntan a Commons' % (c, lang)

#cuantas imagenes tienen las galerias? merece la pena enlazar?
conncommons.query(r'''
    SELECT il_from
    FROM imagelinks
    WHERE il_from IN (SELECT page_id FROM page WHERE page_namespace=0 AND page_is_redirect=0);
    ''') #no poner distinct
r = conncommons.store_result()
c = 0
row = r.fetch_row(maxrows=1, how=1)
while row:
    if len(row) == 1:
        il_from = int(row[0]['il_from'])
        if commons.has_key(il_from):
            commons[il_from][2] += 1
            c += 1;percent(c)
    row = r.fetch_row(maxrows=1, how=1)

print 'Cargadas %d imagenes en galerias' % (c)

#salida
evitar='' #lo dejamos en blanco para que falle si no tenemos plantillas para cierto idioma
if plantillas.has_key(lang):
    evitar = '|'.join([re.sub(' ', '_', k2) for k2 in plantillas[lang]])
wikipedia.output(evitar)

c=0
cc=0

summary=u'Adding link to Commons'
if summaries.has_key(lang):
    summary=summaries[lang]

for k, v in commons.items():
    if v[1] not in usocommons and v[2]>=5:
        c += 1
        wikipedia.output(u'%d) %s %s %s [Llevamos %d de %d]' % (c, k, v[0], v[1], cc, c))
        
        if re.search(ur'(?i)(atlas)', v[0]):
            continue
        
        try:
            page = wikipedia.Page(wikipedia.Site(lang, family), v[1])
            if page.exists() and not page.isRedirectPage() and not page.isDisambig():
                text = page.get()
                if evitar and not re.search(ur'(?i)(%s)' % evitar, text) and not re.search(ur'(?i)\{\{ *(taxo|takso)', text): #taxobox
                    if re.search(regexp[lang], text):
                        newtext=re.sub(regexp[lang], ur'\1\n{{Commons|%s}}' % v[0], text)
                        wikipedia.showDiff(text, newtext)
                        #page.put(newtext, u'BOT - Adding link to Commons: [[:commons:%s|%s]] (TESTING SOME EDITS, SUPERVISED)' % (v[0], v[0]))
                        page.put(newtext, u'BOT - %s: [[:commons:%s|%s]]' % (resume, v[0], v[0]))
                        #time.sleep(10)
                        cc += 1
        except:
            pass
