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

import os, re, wikipedia, sys, sets

lang=sys.argv[1]
#pages
os.system("""mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title from page where page_title>='A' and page_title<'B' and page_namespace=0 and page_is_redirect=0;" > /home/emijrp/temporal/%swikipage.txt""" % (lang, lang, lang))
f=open('/home/emijrp/temporal/%swikipage.txt' % lang, 'r')
c=0
print 'Cargando paginas de %swiki' % lang
pages=sets.Set()
for line in f:
    if c==0: #saltamos la primera linea q es el describe de sql
        c+=1
        continue
    line=unicode(line, 'utf-8')
    line=line[:len(line)-1] #evitamos \n
    line=re.sub('_', ' ', line)
    trozos=line.split('    ')
    if len(trozos)==1:
        c+=1
        page_title=trozos[0]
        pages.add(page_title)
print 'Cargadas %d paginas de %swiki' % (c, lang)
f.close()

#redirects
os.system("""mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title from page where page_title>='A' and page_title<'B' and page_namespace=0 and page_is_redirect=1;" > /home/emijrp/temporal/%swikipage.txt""" % (lang, lang, lang))
f=open('/home/emijrp/temporal/%swikipage.txt' % lang, 'r')
c=0
print 'Cargando redirecciones de %swiki' % lang
redirects=sets.Set()
for line in f:
    if c==0: #saltamos la primera linea q es el describe de sql
        c+=1
        continue
    line=unicode(line, 'utf-8')
    line=line[:len(line)-1] #evitamos \n
    line=re.sub('_', ' ', line)
    trozos=line.split('    ')
    if len(trozos)==1:
        c+=1
        page_title=trozos[0]
        redirects.add(page_title)
print 'Cargadas %d redirecciones de %swiki' % (c, lang)
f.close()

c=0
for page in pages:
    if not re.search(ur"(?i)[^a-záéíóúàèìòù0-9\-\.\,\: ]", page): #no meter (    ), A (desambiguacion) Pi (pelicula)
        page2=page
        page2=re.sub(ur"Á", ur"A", page2)
        page2=re.sub(ur"À", ur"A", page2)
        page2=re.sub(ur"É", ur"E", page2)
        page2=re.sub(ur"È", ur"E", page2)
        page2=re.sub(ur"Í", ur"I", page2)
        page2=re.sub(ur"Ì", ur"I", page2)
        page2=re.sub(ur"Ó", ur"O", page2)
        page2=re.sub(ur"Ò", ur"O", page2)
        page2=re.sub(ur"Ú", ur"U", page2)
        page2=re.sub(ur"Ù", ur"U", page2)
        
        page2=re.sub(ur"á", ur"a", page2)
        page2=re.sub(ur"à", ur"a", page2)
        page2=re.sub(ur"é", ur"e", page2)
        page2=re.sub(ur"è", ur"e", page2)
        page2=re.sub(ur"í", ur"i", page2)
        page2=re.sub(ur"ì", ur"i", page2)
        page2=re.sub(ur"ó", ur"o", page2)
        page2=re.sub(ur"ò", ur"o", page2)
        page2=re.sub(ur"ú", ur"u", page2)
        page2=re.sub(ur"ù", ur"u", page2)
        
        if page != page2 and (page2 not in redirects) and (page2 not in pages):
            c+=1
            
            if c % 100 == 0:
                print c
                wikipedia.output(page)
            
            """page2page=wikipedia.Page(wikipedia.Site(lang, 'wikipedia'), page2)
            if not page2page.exists():
                salida=u"#REDIRECT [[%s]]" % page
                wikipedia.output(salida)
                page2page.put(salida, u"BOT - %s" % salida)
            """
