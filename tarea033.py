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

import os, re, wikipedia

#pages
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select page_title from page where page_namespace=0 and page_is_redirect=0;" > /home/emijrp/temporal/eswikipage.txt')
f=open('/home/emijrp/temporal/eswikipage.txt', 'r')
c=0
print 'Cargando paginas de eswiki'
pages={}
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
        pages[page_title]=False
print 'Cargadas %d paginas de eswiki' % c
f.close()

#redirects
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select page_title from page where page_namespace=0 and page_is_redirect=1;" > /home/emijrp/temporal/eswikipage.txt')
f=open('/home/emijrp/temporal/eswikipage.txt', 'r')
c=0
print 'Cargando redirecciones de eswiki'
reds={}
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
        reds[page_title]=False
print 'Cargadas %d redirecciones de eswiki' % c
f.close()

c=0
for red, v in reds.items():
    if not re.search(ur"(?i)[^a-záéíóúàèìòù0-9\-\. ]", red): #no meter (    ), A (desambiguacion) Pi (pelicula)
        red2=red
        red2=re.sub(ur"Á", ur"A", red2)
        red2=re.sub(ur"À", ur"A", red2)
        red2=re.sub(ur"É", ur"E", red2)
        red2=re.sub(ur"È", ur"E", red2)
        red2=re.sub(ur"Í", ur"I", red2)
        red2=re.sub(ur"Ì", ur"I", red2)
        red2=re.sub(ur"Ó", ur"O", red2)
        red2=re.sub(ur"Ò", ur"O", red2)
        red2=re.sub(ur"Ú", ur"U", red2)
        red2=re.sub(ur"Ù", ur"U", red2)
        
        red2=re.sub(ur"á", ur"a", red2)
        red2=re.sub(ur"à", ur"a", red2)
        red2=re.sub(ur"é", ur"e", red2)
        red2=re.sub(ur"è", ur"e", red2)
        red2=re.sub(ur"í", ur"i", red2)
        red2=re.sub(ur"ì", ur"i", red2)
        red2=re.sub(ur"ó", ur"o", red2)
        red2=re.sub(ur"ò", ur"o", red2)
        red2=re.sub(ur"ú", ur"u", red2)
        red2=re.sub(ur"ù", ur"u", red2)
        
        if red!=red2 and not pages.has_key(red2) and not reds.has_key(red2):
            c+=1
            
            if c % 50 == 0:
                print c
                wikipedia.output(red)
            
            redpage=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), red)
            red2page=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), red2)
            if redpage.isRedirectPage() and not red2page.exists():
                salida=u"#REDIRECT [[%s]]" % redpage.getRedirectTarget().title()
                wikipedia.output(salida)
                red2page.put(salida, u"BOT - %s" % salida)
                
