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
import string
import urllib
import wikipedia

#<monument country="es" lang="es" id="0000009" adm0="es" adm1="es-cm" adm2="es-cu" adm3="[[Cuenca (España)|Cuenca]]" adm4="" name="Museo Arqueológico de Cuenca" address="Calle Obispo Valero, 12" municipality="[[Cuenca (España)|Cuenca]]" lat="40.07819" lon="-2.129209" image="Museo de Cuenca. Fachada.JPG" source="http://es.wikipedia.org/w/index.php?title=Anexo:Bienes_de_interés_cultural_de_la_provincia_de_Cuenca&amp;redirect=no&amp;useskin=monobook&amp;oldid=59834709" monument_article="Museo_de_Cuenca" registrant_url="" changed="2013-01-28 05:00:17" />

def unquote(s):
    s = re.sub(ur'_', ur' ', s)
    s = re.sub(ur'&quot;', ur'"', s)
    return s

countries = { 'es': 'Spain', }
langs = { 'es': 'Spanish', }
adms = { 
    'ES-C': u'Province of A Coruña', 
    'ES-VI': u'Álava‎', 
    'ES-AB': u'Province of Albacete‎', 
    'ES-A': u'Province of Alicante‎', 
    'ES-O': u'Asturias', 
    'ES-AV': u'Province of Ávila‎', 
    'ES-BA': u'Province of Badajoz', 
    'ES-PM': u'Province of Balearic Islands‎', 
    'ES-B': u'Province of Barcelona‎', 
    'ES-BU': u'Province of Burgos‎', 
    'ES-CC': u'Province of Cáceres‎', 
    'ES-CA': u'Province of Cádiz‎', 
    'ES-S': u'Cantabria‎', 
    'ES-CS': u'Province of Castellón‎', 
    'ES-CR': u'Province of Ciudad Real', 
    'ES-CO': u'Province of Córdoba (Spain)‎', 
    'ES-CU': u'Province of Cuenca (Spain)', 
    'ES-GI': u'Province of Girona‎', 
    'ES-GR': u'Province of Granada‎', 
    'ES-GU': u'Province of Guadalajara‎', 
    'ES-SS': u'Gipuzkoa‎', 
    'ES-H': u'Province of Huelva‎', 
    'ES-HU': u'Province of Huesca‎', 
    'ES-J': u'Province of Jaén (Spain)‎', 
    'ES-LO': u' La Rioja (Spain)‎', 
    'ES-GC': u'Province of Las Palmas‎', 
    'ES-LE': u'Province of León‎', 
    'ES-L': u'Province of Lleida‎', 
    'ES-LU': u'Province of Lugo‎', 
    'ES-M': u'Community of Madrid', 
    'ES-MA': u'Province of Málaga‎', 
    'ES-MU': u'Region of Murcia‎', 
    'ES-NA': u'Navarre', 
    'ES-OR': u'Province of Ourense‎', 
    'ES-P': u'Province of Palencia‎', 
    'ES-PO': u'Province of Pontevedra‎', 
    'ES-SA': u'Province of Salamanca‎', 
    'ES-TF': u'Province of Santa Cruz de Tenerife‎', 
    'ES-SG': u'Province of Segovia‎', 
    'ES-SE': u'Province of Seville', 
    'ES-SO': u'Province of Soria', 
    'ES-T': u'Province of Tarragona', 
    'ES-TE': u'Province of Teruel', 
    'ES-TO': u'Province of Toledo', 
    'ES-V': u'Province of Valencia', 
    'ES-VA': u'Province of Valladolid', 
    'ES-BI': u'Biscay‎', 
    'ES-ZA': u'Province of Zamora', 
    'ES-Z': u'Province of Zaragoza', 
}

article_template = u"""
== [[$name]] ([[Talk:$name|talk]]) (#R [[$nativename]]) ==
<pre>
$translationtag{{Infobox Historic Site
| name = $name
| native_name = $nativename
| native_language = $nativelang
| image = $image
| caption = 
| locmapin = $country
| latitude = $lat
| longitude = $lon
| location = [[$municipality]], [[$country]]
| area = 
| built = 
| architect = 
| architecture = 
| governing_body = 
| designation1 = $country
| designation1_offname = $nativename
| designation1_type = Non-movable
| designation1_criteria = Monument
| designation1_date = $date<ref name="bic" />
| designation1_number = $id
}}

The '''$name''' ([[Spanish language|Spanish]]: ''$nativename'') is a $monumenttype located in [[$municipality]], [[$country]]. It was declared ''[[Bien de Interés Cultural]]'' in $date.<ref name="bic">{{Bien de Interés Cultural}}</ref>

== References ==
{{reflist}}

== See also ==

* [[$seealsolist]]

$stubtag

$categories

$interwikis
</pre>
"""
article_template = string.Template(article_template)

f = urllib.urlopen('http://toolserver.org/~erfgoed/api/api.php?action=search&srcountry=es&srlang=es&srimage=%jpg&limit=5000&format=xml')
raw = unicode(f.read(), 'utf-8')
f.close()

m = re.finditer(ur'(?im)<monument country="(?P<country>[^"]*?)" lang="(?P<lang>[^"]*?)" id="(?P<id>[^"]*?)" adm0="(?P<adm0>[^"]*?)" adm1="(?P<adm1>[^"]*?)" adm2="(?P<adm2>[^"]*?)" adm3="(?P<adm3>[^"]*?)" adm4="(?P<adm4>[^"]*?)" name="(?P<nativename>[^"]*?)" address="(?P<address>[^"]*?)" municipality="(?P<municipality>[^"]*?)" lat="(?P<lat>[^"]*?)" lon="(?P<lon>[^"]*?)" image="(?P<image>[^"]*?)" source="(?P<source>[^"]*?)" monument_article="(?P<monument_article>[^"]*?)" registrant_url="(?P<registrant_url>[^"]*?)" changed="(?P<changed>[^"]*?)" />', raw)

for i in m:
    if not re.search(ur"(?im)^R[\-\. ]?I[\-\. ]?", i.group('id')):
        print '--> Not a BIC', i.group('id')
        continue
    
    nativename = unquote(i.group('nativename'))
    name = nativename
    
    if '&' in name:
        nativename = nativename.split('&lt;i&gt;')[0].strip()
        name = nativename
        #print '--> Bad name', name.encode('utf-8')
        #continue
    
    adm = i.group('adm2').upper()
    if adm not in adms.keys():
        print adm, 'not in adms dictionary'
        continue
    
    if i.group('country') == 'es' and i.group('lang') == 'es' and i.group('id') and i.group('adm0') == 'es':
        #get date
        f = urllib.urlopen('http://toolserver.org/~platonides/wlm2011/ids.php?bic=%s' % (i.group('id')))
        raw2 = unicode(f.read(), 'utf-8')
        f.close()
        date = re.search(ur"(?im)<p>Fecha de Declaración: (.*?)</p>", raw2) and re.findall(ur"(?im)<p>Fecha de Declaración: (.*?)</p>", raw2)[0] or ''
        date = date.split('-')[-1].strip()
        if len(date) != 4:
            date = u''
            continue
        
        #conversions
        municipality = i.group('municipality')
        municipality = re.sub(ur"[\[\]]", ur"", municipality)
        
        monumenttype = u'XYZ'
        if re.search(ur'(?im)^Iglesia de', name):
            monumenttype = u'church'
            name = re.sub(ur"(?im)Iglesia (de|del|de la) ", ur"Church of ", name)
        elif re.search(ur'(?im)^Catedral de', name):
            monumenttype = u'cathedral'
            name = re.sub(ur"(?im)Catedral (de|del|de la) ", ur"Cathedral of ", name)
        elif re.search(ur'(?im)^Capilla de', name):
            monumenttype = u'chapel'
            name = re.sub(ur"(?im)Capilla (de|del|de la) ", ur"Chapel of ", name)
        elif re.search(ur'(?im)^Ermita de', name):
            monumenttype = u'hermitage'
            name = re.sub(ur"(?im)Ermita (de|del|de la) ", ur"Hermitage of ", name)
        elif re.search(ur'(?im)^Convento de', name):
            monumenttype = u'convent'
            name = re.sub(ur"(?im)Convento (de|del|de la) ", ur"Convent of ", name)
        elif re.search(ur'(?im)^Muralla de', name):
            monumenttype = u'wall'
            name = re.sub(ur"(?im)Muralla (de|del|de la) ", ur"Wall of ", name)
        elif re.search(ur'(?im)^Monasterio de', name):
            monumenttype = u'monastery'
            name = re.sub(ur"(?im)Monasterio (de|del|de la) ", ur"Monastery of ", name)
        elif re.search(ur'(?im)^Ex-Monasterio de', name):
            monumenttype = u'ex-monastery'
            name = re.sub(ur"(?im)Ex-Monasterio (de|del|de la) ", ur"Ex-Monastery of ", name)
        elif re.search(ur'(?im)^Puerta de', name):
            monumenttype = u'gate'
            name = re.sub(ur"(?im)Puerta (de|del|de la) ", ur"Gate of ", name)
        elif re.search(ur'(?im)^Arco de', name):
            monumenttype = u'arc'
            name = re.sub(ur"(?im)Arco (de|del|de la) ", ur"Arc of ", name)
        elif re.search(ur'(?im)^Castillo de', name):
            monumenttype = u'castle'
            name = re.sub(ur"(?im)Castillo (de|del|de la) ", ur"Castle of ", name)
        elif re.search(ur'(?im)^Colegiata de', name):
            monumenttype = u'collegiate church'
            name = re.sub(ur"(?im)Colegiata (de|del|de la) ", ur"Collegiate church of ", name)
        elif re.search(ur'(?im)^(Torre|Torreón) de', name):
            monumenttype = u'tower'
            name = re.sub(ur"(?im)(Torre|Torreón) (de|del|de la) ", ur"Tower of ", name)
        elif re.search(ur'(?im)^Museo de', name):
            monumenttype = u'museum'
            name = re.sub(ur"(?im)Museo (de|del|de la) ", ur"Museum of ", name)
        elif re.search(ur'(?im)^Palacio de', name):
            monumenttype = u'palace'
            name = re.sub(ur"(?im)Palacio (de|del|de la) ", ur"Palace of ", name)
        #iglesia-convento, 
        
        #stubtag
        stubtag = u'{{Spain-struct-stub}}'
        if re.search(u'(?im)(Church|Cathedral|Collegiate|Hermitage)', name):
            stubtag = u'{{Spain-church-stub}}'
        elif re.search(u'(?im)(Convent|Monastery)', name):
            stubtag = u'{{Spain-Christian-monastery-stub}}'
        elif re.search(u'(?im)(Castle)', name):
            stubtag = u'{{Spain-castle-stub}}'
        elif re.search(u'(?im)(Museum)', name):
            stubtag = u'{{Spain-museum-stub}}'
        elif re.search(u'(?im)(Palace)', name):
            stubtag = u'{{Spain-palace-stub}}'
        
        adm_division = adms[adm]
        if adm_division.startswith('Province') or adm_division.startswith('Community') or adm_division.startswith('Region'):
            adm_division = 'the %s' % (adm_division)
        if not adm_division:
            print 'Error in adm_division'
            continue
        
        #see also
        seealsolist = u'List of Bien de Interés Cultural in %s' % (adm_division)
        
        #categories
        cats = [u'Category:Bienes de Interés Cultural', u'Category:Bien de Interés Cultural landmarks in %s' % (adm_division), ]
        categories = u'\n'.join([u'[[%s]]' % (cat) for cat in cats])
        
        #interwikis
        monument_article = unquote(i.group('monument_article'))
        translationtag = u''
        interwikis = u''
        if monument_article:
            iwpage = wikipedia.Page(wikipedia.Site(i.group('lang'), 'wikipedia'), monument_article)
            if iwpage.exists() and not iwpage.isRedirectPage():
                translationtag = u'{{Expand Spanish|%s|date={{subst:CURRENTMONTHNAME}} {{subst:CURRENTYEAR}}}}\n' % (monument_article)
                iws = re.findall(ur"(?im)^(\[\[[a-z]{2}:[^\]]+?\]\])", iwpage.get())
                iws.append(u'[[es:%s]]' % (monument_article))
                iws.sort()
                interwikis = u'\n'.join(iws)
                if '[[en:' in interwikis:
                    print '--> Page for this monument exists:', iws
                    continue
        
        output = article_template.substitute({
            'name': name,
            'nativename': nativename,
            'nativelang': langs[i.group('lang')],
            'image': unquote(i.group('image')),
            'country': countries[i.group('country')], 
            'lat': i.group('lat'),
            'lon': i.group('lon'),
            'municipality': municipality,
            'date': date,
            'id': i.group('id'),
            'interwikis': interwikis,
            'monumenttype': monumenttype,
            'seealsolist': seealsolist,
            'categories': categories,
            'translationtag': translationtag,
            'stubtag': stubtag,
            'adm_division': adm_division,
            })
        
        g = open('wlmcreator.txt', 'a')
        g.write(output.encode('utf-8'))
        g.close()
        
        print '#'*50
        print output
        
