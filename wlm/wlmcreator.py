#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 emijrp <emijrp@gmail.com>
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

import re
import urllib
#import wikipedia

#<monument country="es" lang="es" id="0000009" adm0="es" adm1="es-cm" adm2="es-cu" adm3="[[Cuenca (España)|Cuenca]]" adm4="" name="Museo Arqueológico de Cuenca" address="Calle Obispo Valero, 12" municipality="[[Cuenca (España)|Cuenca]]" lat="40.07819" lon="-2.129209" image="Museo de Cuenca. Fachada.JPG" source="http://es.wikipedia.org/w/index.php?title=Anexo:Bienes_de_interés_cultural_de_la_provincia_de_Cuenca&amp;redirect=no&amp;useskin=monobook&amp;oldid=59834709" monument_article="Museo_de_Cuenca" registrant_url="" changed="2013-01-28 05:00:17" />

f = urllib.urlopen('http://toolserver.org/~erfgoed/api/api.php?action=search&srcountry=es&srlang=es&srimage=%jpg&limit=100&format=xml')
raw = unicode(f.read(), 'utf-8')
f.close()

m = re.finditer(ur'(?im)<monument country="(?P<country>[^"]*?)" lang="(?P<lang>[^"]*?)" id="(?P<id>[^"]*?)" adm0="(?P<adm0>[^"]*?)" adm1="(?P<adm1>[^"]*?)" adm2="(?P<adm2>[^"]*?)" adm3="(?P<adm3>[^"]*?)" adm4="(?P<adm4>[^"]*?)" name="(?P<name>[^"]*?)" address="(?P<address>[^"]*?)" municipality="(?P<municipality>[^"]*?)" lat="(?P<lat>[^"]*?)" lon="(?P<lon>[^"]*?)" image="(?P<image>[^"]*?)" source="(?P<source>[^"]*?)" monument_article="(?P<monument_article>[^"]*?)" registrant_url="(?P<registrant_url>[^"]*?)" changed="(?P<changed>[^"]*?)" />', raw)

for i in m:
    if i.group('country') == 'es' and i.group('lang') == 'es' and i.group('id') and i.group('adm0') == 'es':
        print i.group('adm2')
        print i.group('name').encode('utf-8')

