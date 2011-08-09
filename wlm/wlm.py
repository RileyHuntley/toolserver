#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 emijrp <emijrp@gmail.com>
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

import datetime
import md5
import re
import wikipedia

#subida fácil: http://commons.wikimedia.org/w/index.php?title=Special:Upload&wpDestFile=BBBB.jpg&uploadformstyle=basic&wpUploadDescription={{Information|Description=|Source=|Date=|Author=|Permission=|other_versions=}}

placenames = {
"alava": u"Álava",
"coruna": u"A&nbsp;Coruña", "albacete": u"Albacete", "almeria": u"Almería", "asturias": u"Asturias", "avila": u"Ávila",
"badajoz": u"Badajoz", "burgos": u"Burgos",
"cantabria": u"Cantabria", "catalunya": u"Catalunya", "ceuta": u"Ceuta", "ciudadreal": u"Ciudad&nbsp;Real", "cuenca": u"Cuenca", "caceres": u"Cáceres", "cadiz": u"Cádiz", "cordoba": u"Córdoba",
"granada": u"Granada", "guadalajara": u"Guadalajara", "guipuzcoa": u"Guipuzkoa",
"huelva": u"Huelva", "huesca": u"Huesca",
"baleares": u"Illes&nbsp;Balears",
"jaen": u"Jaén", 
"laspalmas": u"Las&nbsp;Palmas", "leon": u"León", "lugo": u"Lugo",
"madrid": u"Madrid", "melilla": u"Melilla", "murcia": u"Murcia", "malaga": u"Málaga", 
"navarra": u"Navarra",
"valencia": u"País&nbsp;Valencià", "palencia": u"Palencia", "larioja": u"La Rioja", "ourense": u"Ourense", "pontevedra": u"Pontevedra",
"salamanca": u"Salamanca", "tenerife": u"Tenerife", "segovia": u"Segovia", "sevilla": u"Sevilla", "soria": u"Soria", 
"teruel": u"Teruel", "toledo": u"Toledo", "valladolid": u"Valladolid", "vizcaya": u"Vizcaya", 
"zamora": u"Zamora", "zaragoza": u"Zaragoza",
}

def colors(percent):
    if percent < 25:
        return 'red'
    elif percent < 50:
        return 'pink'
    elif percent < 75:
        return 'yellow'
    elif percent < 100:
        return 'lightgreen'
    elif percent == 100:
        return 'lightblue'
    return 'white'

#mejor no mezclar varios anexos de varios idiomas para una misma provincia
anexos = {
'alava': [u'es:Anexo:Bienes de interés cultural de la provincia de Álava', ], 

'albacete': [u'es:Anexo:Bienes de interés cultural de la provincia de Albacete', ],
'almeria': [u'es:Anexo:Bienes de interés cultural de la provincia de Almería', ],
'asturias': [u'es:Anexo:Bienes de interés cultural de Asturias', ],
'avila': [u'es:Anexo:Bienes de interés cultural de la provincia de Ávila', ],
'badajoz': [u'es:Anexo:Bienes de interés cultural de la provincia de Badajoz', ],
'baleares': [u"ca:Llista de monuments d'Eivissa", u'ca:Llista de monuments de Formentera', 
    u"ca:Llista de monuments d'Alaior", u"ca:Llista de monuments des Castell", u"ca:Llista de monuments de Ciutadella", u"ca:Llista de monuments de Ferreries", u"ca:Llista de monuments de Maó", u"ca:Llista de monuments des Mercadal", u"ca:Llista de monuments des Migjorn Gran", u"ca:Llista de monuments de Sant Lluís",
    
    u"ca:Llista de monuments d'Alaró", u"ca:Llista de monuments d'Alcúdia", u"ca:Llista de monuments d'Algaida", u"ca:Llista de monuments d'Andratx", u"ca:Llista de monuments d'Ariany", u"ca:Llista de monuments d'Artà", u"ca:Llista de monuments de Banyalbufar", u"ca:Llista de monuments de Binissalem", u"ca:Llista de monuments de Búger", u"ca:Llista de monuments de Bunyola", u"ca:Llista de monuments de Calvià", u"ca:Llista de monuments de Campanet", u"ca:Llista de monuments de Campos", u"ca:Llista de monuments de Capdepera", u"ca:Llista de monuments de Consell", u"ca:Llista de monuments de Costitx", u"ca:Llista de monuments de Deià", u"ca:Llista de monuments d'Escorca", u"ca:Llista de monuments d'Esporles", u"ca:Llista de monuments d'Estellencs", u"ca:Llista de monuments de Felanitx", u"ca:Llista de monuments de Fornalutx", u"ca:Llista de monuments d'Inca", u"ca:Llista de monuments de Lloret de Vistalegre", u"ca:Llista de monuments de Lloseta", u"ca:Llista de monuments de Llubí", u"ca:Llista de monuments de Llucmajor", u"ca:Llista de monuments de Manacor", u"ca:Llista de monuments de Mancor de la Vall", u"ca:Llista de monuments de Maria de la Salut", u"ca:Llista de monuments de Marratxí",  u"ca:Llista de monuments de Montuïri",  u"ca:Llista de monuments de Muro",  u"ca:Llista de monuments de Palma",  u"ca:Llista de monuments de Petra",  u"ca:Llista de monuments de sa Pobla",  u"ca:Llista de monuments de Pollença",  u"ca:Llista de monuments de Porreres",  u"ca:Llista de monuments de Puigpunyent",  u"ca:Llista de monuments de ses Salines",  u"ca:Llista de monuments de Sant Joan",  u"ca:Llista de monuments de Sant Llorenç des Cardassar",  u"ca:Llista de monuments de Santa Eugènia",  u"ca:Llista de monuments de Santa Margalida",  u"ca:Llista de monuments de Santa Maria del Camí",  u"ca:Llista de monuments de Santanyí",  u"ca:Llista de monuments de Selva",  u"ca:Llista de monuments de Sencelles",  u"ca:Llista de monuments de Sineu",  u"ca:Llista de monuments de Sóller",  u"ca:Llista de monuments de Son Servera",  u"ca:Llista de monuments de Valldemossa",  u"ca:Llista de monuments de Vilafranca de Bonany",
    ],
    
'burgos': [u'es:Anexo:Bienes de interés cultural de la provincia de Burgos', ],
'cantabria': [u'es:Anexo:Bienes de interés cultural de Cantabria', ],

'catalunya': [u"ca:Llista de monuments de l'Alt Camp", u"ca:Llista de monuments de l'Alt Empordà", u"ca:Llista de monuments de l'Alt Penedès", 
    u"ca:Llista de monuments de l'Alt Urgell", u"ca:Llista de monuments de l'Alta Ribagorça", u"ca:Llista de monuments de l'Anoia", u"ca:Llista de monuments del Bages", u"ca:Llista de monuments del Baix Camp", u"ca:Llista de monuments del Baix Ebre", u"ca:Llista de monuments del Baix Empordà", u"ca:Llista de monuments del Baix Llobregat", u"ca:Llista de monuments del Baix Penedès", u"ca:Llista de monuments de la Baixa Cerdanya", u"ca:Llista de monuments del Barcelonès", u"ca:Llista de monuments del Berguedà", u"ca:Llista de monuments de la Conca de Barberà", u"ca:Llista de monuments del Garraf", u"ca:Llista de monuments de les Garrigues", u"ca:Llista de monuments de la Garrotxa", u"ca:Llista de monuments del Gironès", u"ca:Llista de monuments del Maresme", u"ca:Llista de monuments del Montsià", u"ca:Llista de monuments de la Noguera", u"ca:Llista de monuments d'Osona", u"ca:Llista de monuments del Pallars Jussà", u"ca:Llista de monuments del Pallars Sobirà", u"ca:Llista de monuments del Pla de l'Estany", u"ca:Llista de monuments del Pla d'Urgell", u"ca:Llista de monuments del Priorat", u"ca:Llista de monuments de la Ribera d'Ebre", u"ca:Llista de monuments del Ripollès", u"ca:Llista de monuments de la Segarra", u"ca:Llista de monuments del Segrià", u"ca:Llista de monuments de la Selva", u"ca:Llista de monuments del Solsonès", u"ca:Llista de monuments del Tarragonès", u"ca:Llista de monuments de la Terra Alta", u"ca:Llista de monuments de l'Urgell", u"ca:Llista de monuments de la Vall d'Aran", u"ca:Llista de monuments del Vallès Occidental", u"ca:Llista de monuments del Vallès Oriental", 
    ],

'ceuta': [u'es:Anexo:Bienes de interés cultural de Ceuta', ],
'ciudadreal': [u'es:Anexo:Bienes de interés cultural de la provincia de Ciudad Real', ],
'coruna': [u'gl:Lista de monumentos da provincia da Coruña', ],
'cuenca': [u'es:Anexo:Bienes de interés cultural de la provincia de Cuenca', ],
'caceres': [u'es:Anexo:Bienes de interés cultural de la provincia de Cáceres', ],
'cadiz': [u'es:Anexo:Bienes de interés cultural de la provincia de Cádiz', ],
'cordoba': [u'es:Anexo:Bienes de interés cultural de la provincia de Córdoba', ],

'granada': [u'es:Anexo:Bienes de interés cultural de la provincia de Granada', ],

'guadalajara': [u'es:Anexo:Bienes de interés cultural de la provincia de Guadalajara', ],
'guipuzcoa': [u'es:Anexo:Bienes de interés cultural de la provincia de Guipúzcoa', ],

'huelva': [u'es:Anexo:Bienes de interés cultural de la provincia de Huelva', ],

'huesca': [u'es:Anexo:Bienes de interés cultural de la provincia de Huesca', ],
'jaen': [u'es:Anexo:Bienes de interés cultural de la provincia de Jaén', ],
'laspalmas': [u'es:Anexo:Bienes de interés cultural de la provincia de Las Palmas', ],
'leon': [u'es:Anexo:Bienes de interés cultural de la provincia de León', ],
'madrid': [u'es:Anexo:Bienes de interés cultural de la Comunidad de Madrid', ],
'melilla': [u'es:Anexo:Bienes de interés cultural de Melilla', ],
'murcia': [u'es:Anexo:Bienes de interés cultural de la Región de Murcia', ],
'malaga': [u'es:Anexo:Bienes de interés cultural de la provincia de Málaga', ],
'navarra': [u'es:Anexo:Bienes de interés cultural de Navarra', ],
'palencia': [u'es:Anexo:Bienes de interés cultural de la provincia de Palencia', ],
'larioja': [u'es:Anexo:Bienes de Interés Cultural de La Rioja (España)', ],
'lugo': [u'gl:Lista de monumentos da provincia de Lugo', ],
'ourense': [u'gl:Lista de monumentos da provincia de Ourense', ],
'pontevedra': [u'gl:Lista de monumentos da provincia de Pontevedra', ],
'salamanca': [u'es:Anexo:Bienes de interés cultural de la provincia de Salamanca', ],
'tenerife': [u'es:Anexo:Bienes de interés cultural de la provincia de Santa Cruz de Tenerife', ],
'segovia': [u'es:Anexo:Bienes de interés cultural de la provincia de Segovia', ],
'sevilla': [u'es:Anexo:Bienes de interés cultural de la provincia de Sevilla', ],
'soria': [u'es:Anexo:Bienes de interés cultural de la provincia de Soria', ],
'teruel': [u'es:Anexo:Bienes de Interés Cultural de la provincia de Teruel', ],
'toledo': [u'es:Anexo:Bienes de interés cultural de la provincia de Toledo', ],

'valencia': [u"ca:Llista de monuments de l'Alacantí", u"ca:Llista de monuments de l'Alcalatén", 
    u"ca:Llista de monuments de l'Alcoià", u"ca:Llista de monuments de l'Alt Maestrat", u"ca:Llista de monuments de l'Alt Millars", u"ca:Llista de monuments de l'Alt Palància", u"ca:Llista de monuments de l'Alt Vinalopó", u"ca:Llista de monuments del Baix Maestrat", u"ca:Llista de monuments del Baix Segura", u"ca:Llista de monuments del Baix Vinalopó", u"ca:Llista de monuments del Camp de Morvedre", u"ca:Llista de monuments del Camp de Túria", u"ca:Llista de monuments de la Canal de Navarrés", u"ca:Llista de monuments del Comtat", u"ca:Llista de monuments de la Costera", u"ca:Llista de monuments de la Foia de Bunyol", u"ca:Llista de monuments de l'Horta Nord", u"ca:Llista de monuments de l'Horta Oest", u"ca:Llista de monuments de l'Horta Sud", u"ca:Llista de monuments de la Marina Alta", u"ca:Llista de monuments de la Marina Baixa", u"ca:Llista de monuments de la Plana Alta", u"ca:Llista de monuments de la Plana Baixa", u"ca:Llista de monuments de la Plana d'Utiel", u"ca:Llista de monuments dels Ports", u"ca:Llista de monuments del Racó d'Ademús", u"ca:Llista de monuments de la Ribera Alta", u"ca:Llista de monuments de la Ribera Baixa", u"ca:Llista de monuments de la Safor", u"ca:Llista de monuments dels Serrans", u"ca:Llista de monuments de València", u"ca:Llista de monuments de la Vall d'Albaida", u"ca:Llista de monuments de la Vall de Cofrents", u"ca:Llista de monuments del Vinalopó Mitjà", ],

'valladolid': [u'es:Anexo:Bienes de interés cultural de la provincia de Valladolid', ],
'vizcaya': [u'es:Anexo:Bienes de interés cultural de la provincia de Vizcaya', ],
'zamora': [u'es:Anexo:Bienes de interés cultural de la provincia de Zamora', ],
'zaragoza': [u'es:Anexo:Bienes de interés cultural de la provincia de Zaragoza', ],
}

"""
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Placemark>
      <name>CDATA example</name>
      <description>
        <![CDATA[
          <h1>CDATA Tags are useful!</h1>
          <p><font color="red">Text is <i>more readable</i> and 
          <b>easier to write</b> when you can avoid using entity 
          references.</font></p>
        ]]>
      </description>
      <Point>
        <coordinates>102.595626,14.996729</coordinates>
      </Point>
    </Placemark>
  </Document>
</kml>
"""

"""
{{fila BIC
 | nombre = [[Castillo de Matrera]]
 | nombrecoor = Castillo de Matrera
 | tipobic = M
 | tipo = 
 | municipio = [[Villamartín]]
 | lugar = 
 | lat = 36.807153 | lon = -5.565698
 | bic = RI-51-0007646
 | fecha = 22-06-1993
 | imagen = 
}}

{{Fila BIC 2
 | nombre = [[Archivo Histórico Provincial (Granada)|Archivo Histórico Provincial de Granada]]
 | nombrecoor = Archivo Histórico Provincial de Granada
 | tipobic = A
 | tipo = Archivo
 | municipio = [[Granada]]
 | lugar = C/ San Agapito, s/n
 | lat =  | lon = 
 | bic = R.I.-AR-0000056-00000
 | id_aut = 180870383
 | fecha = 25/06/1985<ref name="Patrimonio">http://www.boe.es/boe/dias/1985/06/29/pdfs/A20342-20352.pdf La Ley de Patrimonio del Estado califica como Bienes de Interés Cultural cuantos edificios estaban declarados con anterioridad como Monumento Nacional</ref>
 | imagen = 
}}
"""
regexp_es = re.compile(ur"""(?im)\{\{\s*fila (BIC|BIC 2)\s*(\|\s*(nombre\s*=\s*(?P<nombre>[^=}]*?)|nombrecoor\s*=\s*(?P<nombrecoor>[^=}]*?)|tipobic\s*=\s*(?P<tipobic>[^=}]*?)|tipo\s*=\s*(?P<tipo>[^=}]*?)|municipio\s*=\s*(?P<municipio>[^=}]*?)|lugar\s*=(?P<lugar>[^=}]*?)|lat\s*=\s*(?P<lat>[0-9\.\-\+]*?)|lon\s*=\s*(?P<lon>[0-9\.\-\+]*?)|bic\s*=\s*(?P<bic>[^=}]*?)|id[_ ]aut\s*=\s*(?P<id_aut>[^=}]*?)|fecha\s*=\s*(?P<fecha>[^=}]*?)|imagen\s*=\s*(?P<imagen>[^=}]*?))\s*)+\s*\|*\s*\}\}""")

"""
{{BIC
| nomeoficial = Castelo da Peroxa
| outrosnomes = 
| paxina = 
| idurl = 
| concello =  [[A Peroxa]]
| lugar = 
| lat = 42.434208 | lon = -7.786825
| id =  RI-51-0008954
| data_declaracion = 17-11-1994
| imaxe = Castelo da Peroxa.JPG
}}
"""

#el campo idurl no aparece en algunas listas, lo ponemos opcional
regexp_gl = re.compile(ur"""(?im)\{\{\s*BIC\s*(\|\s*(nomeoficial\s*=\s*(?P<nombre>[^=}]*?)|\s*outrosnomes\s*=\s*(?P<nombrecoor>[^=}]*?)|\s*paxina\s*=\s*(?P<paxina>[^=}]*?)|idurl\s*=\s*(?P<idurl>[^=}]*?)|concello\s*=(?P<lugar>[^=}]*?)|lugar\s*=(?P<municipio>[^=}]*?)|lat\s*=\s*(?P<lat>[0-9\.\-\+]*?)|lon\s*=\s*(?P<lon>[0-9\.\-\+]*?)|id\s*=\s*(?P<bic>[^=}]*?)|data[_ ]declaracion\s*=\s*(?P<fecha>[^=}]*?)|imaxe\s*=\s*(?P<imagen>[^=}]*?))\s*)+\s*\|*\s*\}\}""")

"""
{{filera BIC
 | nom = [[Murades d'Eivissa|Antigues murades]] i Torre del Campanar
 | nomcoor = Antigues murades i Torre del Campanar (Eivissa)
 | tipus = Arquitectura militar
 | municipi = [[Eivissa (municipi)|Eivissa]]
 | lloc = Dalt Vila
 | lat = 38.908252 | lon = 1.436645
 | bic = RI-51-0001114
 | imatge = EIVISSA 03 (1590948910).jpg
}}

{{filera BCIN
 | nom = [[Palau dels Barons de Pinós|El Palau]] <br/>''Castell de Bagà''
 | nomcoor = El Palau (Bagà)
 | estil = Obra popular, barroc
 | època = XIII / XVIII
 | municipi = [[Bagà]]
 | lloc = Pujada del Palau, 7
 | lat = 42.253394 | lon = 1.861108
 | idurl = 576
 | prot = BCIN
 | bcin = 497-MH
 | bic = RI-51-0005193
 | imatge = 
}}
"""
regexp_ca = re.compile(ur"""(?im)\{\{\s*filera (BIC|BCIN|BIC Val)\s*(\|\s*(nom\s*=\s*(?P<nombre>[^=}]*?)|nomcoor\s*=\s*(?P<nombrecoor>[^=}]*?)|tipus\s*=\s*(?P<tipobic>[^=}]*?)|estil\s*=\s*([^=}]*?)|època\s*=\s*([^=}]*?)|municipi\s*=\s*(?P<municipio>[^=}]*?)|lloc\s*=(?P<lugar>[^=}]*?)|lat\s*=\s*(?P<lat>[0-9\.\-\+]*?)|lon\s*=\s*(?P<lon>[0-9\.\-\+]*?)|idurl\s*=\s*([^=}]*?)|prot\s*=\s*([^=}]*?)|bcin\s*=\s*([^=}]*?)|bic\s*=\s*(?P<bic>[^=}]*?)|fecha\s*=\s*(?P<fecha>[^=}]*?)|imatge\s*=\s*(?P<imagen>[^=}]*?))\s*)+\s*\|*\s*\}\}""")

def isvalidimage(img):
    if img and not re.search(ur'(?im)(falta[_ ]imagen|\.svg)', img):
        return True
    return False

def clean(t):
    t = re.sub(ur'(?i)([\[\]]|\|.*|\<ref.*)', ur'', t).strip()
    t = re.sub(ur'(?im)<\s*br\s*/?\s*>', ur'-', t).strip()
    return t

def removerefs(t):
    t = re.sub(ur"(?im)\{\{\s*(?!(fila (BIC|BIC 2)|BIC|filera (BIC|BCIN|BIC Val)))\s*\|[^{}]*?\}\}", ur"", t)
    t = re.sub(ur"(?im)<\s*ref[^<>]*?\s*>[^<>]*?<\s*/\s*ref\s*>", ur"", t)
    return t

missingcoordinates = 0
missingimages = 0
total = 0
provincesstats = []
errors = {}
totalerrors = 0
for anexoid, anexolist in anexos.items():
    bics = {}
    if not errors.has_key(anexoid):
        errors[anexoid] = '&nbsp;'
    for anexo in anexolist:
        print anexo
        lang = anexo.split(':')[0]
        s = wikipedia.Site(lang, 'wikipedia')
        wtitle = ':'.join(anexo.split(':')[1:])
        p = wikipedia.Page(s, wtitle)
        wtext = p.get()
        wtext = removerefs(wtext)
        
        m = ''
        if lang == 'es':
            m = regexp_es.finditer(wtext)
        elif lang == 'gl':
            m = regexp_gl.finditer(wtext)
        elif lang == 'ca':
            m = regexp_ca.finditer(wtext)
        if m:
            for i in m:
                bic = '?'
                try:
                    bic = i.group('bic').strip()
                    bics[bic] = {
                        'lang': lang,
                        'nombre': clean(i.group('nombre').strip()),
                        #'nombrecoor': i.group('nombrecoor').strip(),
                        #'tipobic': i.group('tipobic').strip(),
                        #'tipo': i.group('tipo').strip(),
                        'municipio': clean(i.group('municipio').strip()),
                        'lugar': clean(i.group('lugar').strip()),
                        'lat': i.group('lat').strip(),
                        'lon': i.group('lon').strip(),
                        'bic': bic,
                        #'fecha': i.group('fecha').strip(), #no existe en ca:
                        'imagen': i.group('imagen').strip(),
                    }
                except:
                    totalerrors += 1
                    print anexoid, wtitle, bic
                    errors[anexoid] += '<a href="http://%s.wikipedia.org/wiki/%s" target="_blank">%s</a>, \n' % (lang, wtitle, bic)

    imageyesurl = 'http://maps.google.com/mapfiles/kml/paddle/red-stars.png'
    imagenourl = 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
    output = u"""<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://www.opengis.net/kml/2.2">
        <Document>
        <name>Wiki Loves Monuments</name>
        <description>A map with missing images by location</description>
        <Style id="imageyes">
          <IconStyle>
            <Icon>
              <href>%s</href>
            </Icon>
          </IconStyle>
        </Style>
        <Style id="imageno">
          <IconStyle>
            <Icon>
              <href>%s</href>
            </Icon>
          </IconStyle>
        </Style>
    """ % (imageyesurl, imagenourl)

    submissingcoordinates = 0
    submissingimages = 0
    subtotal = 0
    imagesize = '150px'
    for bic, props in bics.items():
        total += 1
        subtotal += 1
        thumburl = ''
        commonspage = ''
        if isvalidimage(props['imagen']):
            #http://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Toronto_-_ON_-_CN_Tower_bei_Nacht2.jpg/398px-Toronto_-_ON_-_CN_Tower_bei_Nacht2.jpg
            filename = re.sub(ur'(?im)([\[\]]|File:|Imagen?:|Archivo:|\|.*)', ur'', props['imagen'])
            filename = re.sub(' ', '_', filename)
            m5 = md5.new(filename.encode('utf-8')).hexdigest()
            thumburl = u'http://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%s-%s' % (m5[0], m5[:2], filename, imagesize, filename)
            commonspage = u'http://commons.wikimedia.org/wiki/File:%s' % (filename)
        else:
            missingimages += 1
            submissingimages += 1
        
        if not thumburl:
            thumburl = 'http://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Image-missing.svg/%s-Image-missing.svg.png' % (imagesize)
            commonspage = ''
        
        articleurl = u'http://%s.wikipedia.org/wiki/%s' % (props['lang'], props['nombre'])
        articleurl = re.sub(u' ', u'_', articleurl)
        locatedin = props['municipio']
        if props['lat'] and props['lon']:
            output += u"""
<Placemark>
<name>%s</name>
<description>
<![CDATA[
<table border=0 cellspacing=3px cellpadding=3px>
<tr><td align=right width=80px style="background-color: lightgreen;"><b>BIC:</b></td><td><a href="%s" target="_blank">%s</a></td><td rowspan=4><a href="%s" target="_blank"><img src="%s" width=%s/></a></td></tr>
<tr><td align=right style="background-color: lightblue;"><b>Located in:</b></td><td>%s</td></tr>
<tr><td align=right style="background-color: yellow;"><b>ID:</b></td><td>%s</td></tr>
<tr><td align=center colspan=2><br/><b>This BIC has %s<br/>you can upload yours. Thanks!</b><br/><br/><span style="border: 2px solid black;background-color: pink;padding: 3px;"><a href="http://commons.wikimedia.org/w/index.php?title=Special:Upload&uploadformstyle=basic&wpDestFile=%s - %s - WLM.jpg&wpUploadDescription={{Information%%0D%%0A| Description = %s%%0D%%0A| Source = {{Own}}%%0D%%0A| Date = %%0D%%0A| Author = [[User:{{subst:REVISIONUSER}}|{{subst:REVISIONUSER}}]]%%0D%%0A| Permission = %%0D%%0A| other_versions = %%0D%%0A}}%%0D%%0A{{Selected for WLM 2011 ES|%s}}" target="_blank"><b>Upload</b></a></span></td></tr>
</table>
]]>
</description>
<styleUrl>#%s</styleUrl>
<Point>
<coordinates>%s,%s</coordinates>
</Point>
</Placemark>""" % (props['nombre'], articleurl, props['nombre'], commonspage, thumburl, imagesize, locatedin, props['bic'], isvalidimage(props['imagen']) and 'images, but' or 'no images,', props['nombre'], props['bic'], props['nombre'], props['bic'], isvalidimage(props['imagen']) and 'imageyes' or 'imageno', props['lon'], props['lat'])
        else:
            missingcoordinates +=1
            submissingcoordinates +=1
    
    provincesstats.append([anexoid, subtotal, submissingcoordinates, submissingimages])
    
    output += u"""
    </Document>
</kml>"""

    f = open('/home/emijrp/public_html/wlm/wlm-%s.kml' % (anexoid), 'w')
    f.write(output.encode('utf-8'))
    f.close()

tablestats = u'<table border=1px style="text-align: center;">\n'
tablestats += u'<tr><th width=100px>Place</th><th width=100px>Total BICs</th><th width=150px>With coordinates</th><th width=100px>With images</th><th width=175px>Details</th><th width=175px>Errors</th></tr>\n'
provincesstats.sort()
for p, ptotal, pmissingcoordinates, pmissingimages in provincesstats:
    pcoordper = ptotal and (ptotal-pmissingcoordinates)/(ptotal/100.0) or 0
    pimageper = ptotal and (ptotal-pmissingimages)/(ptotal/100.0) or 0
    refs = u''
    c = 1
    for i in anexos[p]:
        refs += u'<a href="http://%s.wikipedia.org/wiki/%s" target="_blank">[%d]</a> ' % (i.split(':')[0], ':'.join(i.split(':')[1:]), c)
        c += 1
    refs = u"""[ <a href="javascript:showHide('%s-refs')">Show/Hide</a> ]<div id="%s-refs" style="display: none;">%s</div>""" % (p, p, refs)
    errorstext = u"""[ <a href="javascript:showHide('%s-errors')">Show/Hide</a> ]<div id="%s-errors" style="display: none;">%s</div>""" % (p, p, errors[p])
    tablestats += u'<tr><td><a href="index.php?place=%s">%s</a></td><td>%d</td><td bgcolor=%s>%d (%.1f%%)</td><td bgcolor=%s>%d (%.1f%%)</td><td>%s</td><td>%s</td></tr>\n' % (p, placenames[p], ptotal, colors(pcoordper),ptotal-pmissingcoordinates, pcoordper, colors(pimageper), ptotal-pmissingimages, pimageper, refs, errorstext)

tablestats += u'<tr><td><b>Total</b></td><td><b>%d</b></td><td bgcolor=%s><b>%d (%.1f%%)</b></td><td bgcolor=%s><b>%d (%.1f%%)</b></td><td><a href="http://ca.wikipedia.org/wiki/Categoria:Llistes_de_monuments" target="_blank">[1]</a> <a href="http://es.wikipedia.org/wiki/Categor%%C3%%ADa:Anexos:Bienes_de_inter%%C3%%A9s_cultural_en_Espa%%C3%%B1a" target="_blank">[2]</a> <a href="http://gl.wikipedia.org/wiki/Categor%%C3%%ADa:Bens_de_Interese_Cultural_de_Galicia" target="_blank">[3]</a></td><td>%d</td></tr>\n' % (total, colors((total-missingcoordinates)/(total/100.0)), total-missingcoordinates, (total-missingcoordinates)/(total/100.0), colors((total-missingimages)/(total/100.0)), total-missingimages, (total-missingimages)/(total/100.0), totalerrors)
tablestats += u'</table>\n'

anexoskeys = anexos.keys()
anexoskeys.sort()

output = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Wiki Loves Monuments</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />

<script language="javascript">
function showHide(id){
    if (document.getElementById(id).style.display == 'none') {
        document.getElementById(id).style.display = 'block';
    }else{
        document.getElementById(id).style.display = 'none';
    }
}

</script>

</head>

<?php
$places = array(%s );
$place="madrid";
if (isset($_GET['place']))
{
	$temp = $_GET['place'];
	if (in_array($temp, $places))
		$place = $temp;
}

?>

<body>
<center>
<table width=1000px style="text-align: center;">
<tr>
<td>
<a href="http://www.wikimedia.org.es/" target="_blank"><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Wikimedia-es-logo.svg/100px-Wikimedia-es-logo.svg.png" /></a>
</td>
<td>
<center>
<big><big><big><b><a href="http://www.wikilm.es" target="_blank">Wiki <i>Loves</i> Monuments</a></b></big></big></big>
<br/>
<b>Spain, September 1–30, 2011</b>
<br/>
<br/>
Total registered <i><a href="http://es.wikipedia.org/wiki/Bien_de_Inter%%C3%%A9s_Cultural" target="_blank">BICs</a></i> in Spain: %d | With coordinates: %d (%.1f%%) | With images: %d (%.1f%%)
<br/>
Legend: With image <img src="%s" width=20px title="With image" alt="With image"/>, Without image <img src="%s" width=20px title="Without image" alt="Without image"/>
</td>
<td>
<a href="http://www.wikilm.es/" target="_blank"><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/LUSITANA_WLM_2011_d.svg/100px-LUSITANA_WLM_2011_d.svg.png" /></a>
</td>
</tr>
<tr>
<td colspan=3>
Select a place: %s

<iframe width="1000" height="450" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://maps.google.com/maps?f=q&amp;source=s_q&amp;hl=es&amp;geocode=&amp;q=http:%%2F%%2Ftoolserver.org%%2F~emijrp%%2Fwlm%%2Fwlm-<?php echo $place; ?>.kml%%3Fusecache%%3D0&amp;output=embed"></iframe>
<br/>
<br/>
<center>
%s
</center>
<i>Last update: %s (UTC)</i>
<br/>
</td>
</tr>
</table>

</center>
</body>

</html>
""" % (', '.join(['"%s"' % (i) for i in anexoskeys]), total, total-missingcoordinates, (total-missingcoordinates)/(total/100.0), total-missingimages, (total-missingimages)/(total/100.0), imageyesurl, imagenourl, ', '.join(['<a href="index.php?place=%s">%s</a>' % (i, placenames[i]) for i in anexoskeys]), tablestats, datetime.datetime.now())

f = open('/home/emijrp/public_html/wlm/index.php', 'w')
f.write(output.encode('utf-8'))
f.close()

