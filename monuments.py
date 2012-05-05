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

def uncode(t):
    return unicode(t, 'latin-1')

f = gzip.open('monuments_db.sql.gz', 'rb')
raw = f.read()
f.close()

#('RI-51-0010004','[[Castillo de los Moros]]','Castillo de los Moros','M','','[[Cartagena (Espa�a)|Cartagena]]','',0,0,'07-08-1997','','http://es.wikipedia.org/w/index.php?title=Anexo:Bienes_de_inter�s_cultural_de_la_Regi�n_de_Murcia&redirect=no&useskin=monobook&oldid=55416020','2012-04-26 03:12:36','Anexo:Bienes_de_inter�s_cultural_de_la_Regi�n_de_Murcia','','Castillo_de_los_Moros')
monuments = re.compile(ur"(?im)(\('(?P<id>RI-\d+-\d+)','(?P<pagelink>[^']*?)','(?P<name>[^']*?)','M','(?P<type>[^']*?)','(?P<location>[^']*?)','[^']*?',(?P<lat>[\d\-\.\,]+),(?P<lon>[\d\-\.\,]+),'(?P<date>[^']*?)','(?P<image>[^']*?)','http://[^']*?','[^']*?','[^']*?','[^']*?','(?P<page>[^']*?)'\))").finditer(raw)

c = 0
for monument in monuments:
    id = uncode(monument.group('id'))
    name = uncode(monument.group('name'))
    page = uncode(monument.group('page'))
    image = uncode(monument.group('image'))
    lat = uncode(monument.group('lat'))
    lon = uncode(monument.group('lon'))
    
    if id and name and page and image and lat and lon:
        print name
        c += 1

print c
