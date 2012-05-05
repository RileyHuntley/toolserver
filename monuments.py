# -*- coding: utf-8 -*-

# Copyright (C) 2012 emijrp <emijrp@gmail.com>
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

import gzip
import re
import wikipedia

types = {'arco': 'arch', 'arco romano': 'Roman arch', 'castillo': 'castle', 'catedral': 'cathedral', 'concatedral': 'co-cathedral', 'ermita': 'hermitage', 'iglesia': 'church', 'monasterio': 'monastery', 'muralla': 'wall', 'palacio': 'palace', 'puente': 'bridge', 'puerta': 'gate', 'teatro': 'theatre'}

def uncode(t):
    return unicode(t, 'latin-1')

def translatename(name):
    nameen = name
    nameen = re.sub(ur"(?im)^Arco (árabe)? ?(de )?", ur"Arch of \1", nameen)
    nameen = re.sub(ur"(?im)^Castillo \((.*?)\)", ur"Castle of \1", nameen)
    nameen = re.sub(ur"(?im)^Castillo (de )?", ur"Castle of ", nameen)
    nameen = re.sub(ur"(?im)^Catedral (de )?", ur"Cathedral of ", nameen)
    nameen = re.sub(ur"(?im)^Concatedral (de )?", ur"Co-cathedral of ", nameen)
    nameen = re.sub(ur"(?im)^Ermita (de )?", ur"Hermitage of ", nameen)
    nameen = re.sub(ur"(?im)^Iglesia (Parroquial|Fortificada)? ?(de )?", ur"Church of ", nameen)
    nameen = re.sub(ur"(?im)^Monasterio (Cisterciense )?(de )?", ur"Monastery of ", nameen)
    nameen = re.sub(ur"(?im)^Muralla (de )?", ur"Walls of ", nameen)
    nameen = re.sub(ur"(?im)^Palacio (de )?", ur"Palace of ", nameen)
    nameen = re.sub(ur"(?im)^Puente (Romano)? ?(de )?", ur"Bridge of ", nameen)
    nameen = re.sub(ur"(?im)^Puerta (de )?", ur"Gate of ", nameen)
    nameen = re.sub(ur"(?im)^Teatro (de )?", ur"Theatre of ", nameen)
    return nameen

f = gzip.open('monuments_db.sql.gz', 'rb')
raw = f.read()
f.close()

#('RI-51-0010004','[[Castillo de los Moros]]','Castillo de los Moros','M','','[[Cartagena (Espa�a)|Cartagena]]','',0,0,'07-08-1997','','http://es.wikipedia.org/w/index.php?title=Anexo:Bienes_de_inter�s_cultural_de_la_Regi�n_de_Murcia&redirect=no&useskin=monobook&oldid=55416020','2012-04-26 03:12:36','Anexo:Bienes_de_inter�s_cultural_de_la_Regi�n_de_Murcia','','Castillo_de_los_Moros')
monuments = re.compile(ur"(?im)(\('(?P<id>RI-\d+-\d+)','(?P<pagelink>[^']*?)','(?P<name>[^']*?)','M','(?P<type>[^']*?)','(?P<location>[^']*?)','[^']*?',(?P<lat>[\d\-\.]+),(?P<lon>[\d\-\.]+),'(?P<date>[^']*?)','(?P<image>[^']*?)','http://[^']*?','[^']*?','[^']*?','[^']*?','(?P<page>[^']*?)'\))").finditer(raw)

c = 0
for monument in monuments:
    id = uncode(monument.group('id'))
    name = uncode(monument.group('name'))
    nameen = translatename(name)
    type_ = uncode(monument.group('type')).lower()
    pagename = uncode(monument.group('page'))
    image = uncode(monument.group('image'))
    date = uncode(monument.group('date'))
    location = uncode(monument.group('location'))
    lat = uncode(monument.group('lat'))
    lon = uncode(monument.group('lon'))
    
    if id and name and pagename and image and location and lat and lon and types.has_key(type_):
        #check if exists
        skip = False
        iws = []
        pagees = wikipedia.Page(wikipedia.Site('es', 'wikipedia'), pagename)
        if pagees.exists():
            while pagees.isRedirectPage():
                pagees = pagees.getRedirectTarget()
            for iw in pagees.interwiki():
                iws.append([iw.site().lang, iw.title()])
                if iw.site().lang == 'en':
                    print 'Existe en la inglesa'
                    skip = True
                    break
            iws.append(['es', pagees.title()]) #inside this if, add only if pagees exists!
        else:
            pagees = ''
        
        if skip:
            continue
        """mejor lo guardo y luego miro si está en azul y si es este monumento u otro q se llama igual (en ese caso creo desambiguación)
        pageen = wikipedia.Page(wikipedia.Site('en', 'wikipedia'), nameen)
        if pageen.exists():
            print 'Existe en la inglesa'
            continue"""
        
        iws.sort()
        iws_plain = ''
        for iwlang, iwtitle in iws:
            iws_plain += u'[[%s:%s]]\n' % (iwlang, iwtitle)
        
        year = u''
        yearsentence = u''
        if date:
            year = date.split('-')[-1].split('/')[-1]
            if year:
                yearsentence = year and u" It was declared ''[[Bien de Interés Cultural]]'' in %s." % (year) or u''
        
        c += 1
        print '#'*50, '\n', c, name, '\n', '#'*50
        
        output = u"""%s{{Infobox Historic Site
| name = %s
| native_name = %s
| native_language = Spanish
| image = %s
| caption = 
| locmapin = Spain
| latitude = %s
| longitude = %s
| location = %s, [[Spain]]
| area = 
| built = 
| architect = 
| architecture = 
| governing_body = 
| designation1 = Spain
| designation1_offname = %s
| designation1_type = Non-movable
| designation1_criteria = Monument
| designation1_date = %s<ref name="bic" />
| designation1_number = %s
}}

The '''%s''' ([[Spanish language|Spanish]]: ''%s'') is a %s located in %s, [[Spain]].%s<ref name="bic">{{Bien de Interés Cultural}}</ref>

== References ==
{{reflist}}

[[Category:Bien de Interés Cultural buildings]]

%s
{{Spain-struct-stub}}""" % (pagees and u"{{Expand Spanish|%s}}\n" % (pagees.title()) or '', nameen, name, image, lat, lon, location, name, year and year or u'', id, nameen, name, type_ and types[type_] or u'monument', location, yearsentence, iws_plain)
        print 'Guardando...'
        output = u'\n\n== [[%s]] ([[:es:%s|es]]) ==\n<pre>\n%s\n</pre>' % (nameen, pagename, output)
        print output
        
        f = open('monuments.output.txt', 'a')
        f.write(output.encode('utf-8'))
        f.close()

print c
