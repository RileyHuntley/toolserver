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

anexos = [
u'Anexo:Bienes de interés cultural de la provincia de Albacete',
u'Anexo:Bienes de interés cultural de la provincia de Almería',
u'Anexo:Bienes de interés cultural de Asturias',
u'Anexo:Bienes de interés cultural de la provincia de Ávila',
u'Anexo:Bienes de interés cultural de la provincia de Badajoz',
u'Anexo:Bienes de interés cultural de la provincia de Burgos',
u'Anexo:Bienes de interés cultural de Cantabria',
u'Anexo:Bienes de interés cultural de Ceuta',
u'Anexo:Bienes de interés cultural de la provincia de Ciudad Real',
u'Anexo:Bienes de interés cultural de la provincia de La Coruña',
u'Anexo:Bienes de interés cultural de la provincia de Cuenca',
u'Anexo:Bienes de interés cultural de la provincia de Cáceres',
u'Anexo:Bienes de interés cultural de la provincia de Cádiz',
u'Anexo:Bienes de interés cultural de la provincia de Córdoba',
u'Anexo:Bienes de interés cultural de la provincia de Granada',
u'Anexo:Bienes de interés cultural de la provincia de Guadalajara',
u'Anexo:Bienes de interés cultural de la provincia de Guipúzcoa',
u'Anexo:Bienes de interés cultural de la provincia de Huelva',
u'Anexo:Bienes de interés cultural de la provincia de Huesca',
u'Anexo:Bienes de interés cultural de la provincia de Jaén',
u'Anexo:Bienes de interés cultural de la provincia de Las Palmas',
u'Anexo:Bienes de interés cultural de la provincia de León',
u'Anexo:Bienes de interés cultural de la Comunidad de Madrid',
u'Anexo:Bienes de interés cultural de Melilla',
u'Anexo:Bienes de interés cultural de la Región de Murcia',
u'Anexo:Bienes de interés cultural de la provincia de Málaga',
u'Anexo:Bienes de interés cultural de Navarra',
u'Anexo:Bienes de interés cultural de la provincia de Palencia',
u'Anexo:Bienes de Interés Cultural de La Rioja (España)',
u'Anexo:Bienes de interés cultural de la provincia de Salamanca',
u'Anexo:Bienes de interés cultural de la provincia de Santa Cruz de Tenerife',
u'Anexo:Bienes de interés cultural de la provincia de Segovia',
u'Anexo:Bienes de interés cultural de la provincia de Sevilla',
u'Anexo:Bienes de interés cultural de la provincia de Soria',
u'Anexo:Bienes de Interés Cultural de la provincia de Teruel',
u'Anexo:Bienes de interés cultural de la provincia de Toledo',
u'Anexo:Bienes de interés cultural de la provincia de Valladolid',
u'Anexo:Bienes de interés cultural de la provincia de Vizcaya',
u'Anexo:Bienes de interés cultural de la provincia de Zamora',
u'Anexo:Bienes de interés cultural de la provincia de Zaragoza',
]
#u'Anexo:Bienes de interés cultural de la provincia de Álava',

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
"""
regexp = re.compile(ur'(?im)\{\{\s*fila BIC\s*\|\s*nombre\s*=\s*(?P<nombre>[^=}]*)\s*\|\s*nombrecoor\s*=\s*(?P<nombrecoor>[^=}]*)\s*\|\s*tipobic\s*=\s*(?P<tipobic>[^=}]*)\s*\|\s*tipo\s*=\s*(?P<tipo>[^=}]*)\s*\|\s*municipio\s*=\s*(?P<municipio>[^=}]*)\s*\|\s*lugar\s*=(?P<lugar>[^=}]*)\s*\|\s*lat\s*=\s*(?P<lat>[^=}]*)\s*\|\s*lon\s*=\s*(?P<lon>[^=}]*)\s*\|\s*bic\s*=\s*(?P<bic>[^=}]*)\s*\|\s*fecha\s*=\s*(?P<fecha>[^=}]*)\s*\|\s*imagen\s*=\s*(?P<imagen>[^=}]*)\s*\}\}')
s = wikipedia.Site('es', 'wikipedia')
bics = {}
for anexo in anexos:
    print anexo
    p = wikipedia.Page(s, anexo)
    wtext = p.get()
    m = regexp.finditer(wtext)
    if m:
        for i in m:
            bic = i.group('bic').strip()
            bics[bic] = {
                'nombre': i.group('nombre').strip(),
                'nombrecoor': i.group('nombrecoor').strip(),
                'tipobic': i.group('tipobic').strip(),
                'tipo': i.group('tipo').strip(),
                'municipio': i.group('municipio').strip(),
                'lugar': i.group('lugar').strip(),
                'lat': i.group('lat').strip(),
                'lon': i.group('lon').strip(),
                'bic': bic,
                'fecha': i.group('fecha').strip(),
                'imagen': i.group('imagen').strip(),
            }
            

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

missingcoordinates = 0
missingimages = 0
total = 0
imagesize = '150px'
for bic, props in bics.items():
    total += 1
    thumburl = ''
    commonspage = ''
    if props['imagen'] and not re.search(ur'(?im)(falta[_ ]imagen|\.svg)', props['imagen']):
        #http://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Toronto_-_ON_-_CN_Tower_bei_Nacht2.jpg/398px-Toronto_-_ON_-_CN_Tower_bei_Nacht2.jpg
        filename = re.sub(ur'(?im)([\[\]]|File:|Imagen?:|Archivo:|\|.*)', ur'', props['imagen'])
        filename = re.sub(' ', '_', filename)
        m5 = md5.new(filename.encode('utf-8')).hexdigest()
        thumburl = u'http://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%s-%s' % (m5[0], m5[:2], filename, imagesize, filename)
        commonspage = u'http://commons.wikimedia.org/wiki/File:%s' % (filename)
    else:
        missingimages += 1
    
    if not thumburl:
        thumburl = 'http://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Image-missing.svg/%s-Image-missing.svg.png' % (imagesize)
        commonspage = 'http://commons.wikimedia.org/wiki/Commons:Upload'
    
    articleurl = u'http://es.wikipedia.org/wiki/%s' % (re.sub(ur'([\[\]]|\|.*)', ur'', props['nombre']))
    articleurl = re.sub(u' ', u'_', articleurl)
    locatedin = re.sub(ur'([\[\]]|\|.*)', ur'', props['municipio'])
    if props['lat'] and props['lon']:
        output += u"""
        <Placemark>
          <name>%s</name>
          <description>
            <![CDATA[
              <table border=0>
              <tr><td align=right width=80px style="background-color: lightgreen;"><b>BIC:</b></td><td><a href="%s" target="_blank">%s</a></td><td rowspan=3><a href="%s" target="_blank"><img src="%s" width=%s/></a></td></tr>
              <tr><td align=right style="background-color: lightblue;"><b>Located in:</b></td><td>%s</td></tr>
              <tr><td align=center colspan=2><b>This BIC has %s<br/>you can upload yours</b><br/><span style="border: 2px solid black;background-color: pink;"><a href="http://commons.wikimedia.org/w/index.php?title=Special:Upload&uploadformstyle=basic&wpDestFile=%s - WLM.jpg" target="_blank">Upload</a></span></td></tr>
              </table>
            ]]>
          </description>
          <styleUrl>#%s</styleUrl>
          <Point>
            <coordinates>%s,%s</coordinates>
          </Point>
        </Placemark>""" % (props['nombrecoor'], articleurl, props['nombrecoor'], commonspage, thumburl, imagesize, locatedin, props['imagen'] and 'images, but' or 'no images,', props['nombrecoor'], props['imagen'] and 'imageyes' or 'imageno', props['lon'], props['lat'])
    else:
        missingcoordinates +=1

output += u"""
    </Document>
</kml>"""

f = open('/home/emijrp/public_html/wlm/wlm.kml', 'w')
f.write(output.encode('utf-8'))
f.close()

output = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="es" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Wiki Loves Monuments</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
</head>

<body>
<center>
<span style="position: absolute;top: 10px;left: 10px;"><a href="http://www.wikimedia.org.es/" target="_blank"><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Wikimedia-es-logo.svg/100px-Wikimedia-es-logo.svg.png" /></a></span>
<span style="position: absolute;top: 10px;right: 10px;"><a href="http://www.wikilm.es/" target="_blank"><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/LUSITANA_WLM_2011_d.svg/100px-LUSITANA_WLM_2011_d.svg.png" /></a></span>
<h2><a href="http://www.wikilm.es" target="_blank">Wiki <i>Loves</i> Monuments</a></h2>

<center>
Total listed <i><a href="http://es.wikipedia.org/wiki/Bien_de_Inter%%C3%%A9s_Cultural" target="_blank">BICs</a></i>: %d | Missing coordinates: %d (%.1f%%) | Missing images: %d (%.1f%%)
<br/>
Legend: With image <img src="%s" width=20px title="with image" alt="with image"/>, Without image <img src="%s" width=20px title="without image" alt="without image"/>
<br/>
Help editing <a href="http://es.wikipedia.org/wiki/Categor%%C3%%ADa:Anexos:Bienes_de_inter%%C3%%A9s_cultural_en_Espa%%C3%%B1a" target="_blank">Anexos:Bienes de interés cultural en España</a>
<br/>

<iframe width="800" height="550" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://maps.google.com/maps?f=q&amp;source=s_q&amp;hl=es&amp;geocode=&amp;q=http:%%2F%%2Ftoolserver.org%%2F~emijrp%%2Fwlm%%2Fwlm.kml%%3Fusecache%%3D0&amp;sll=40.913513,-4.504395&amp;sspn=11.352924,23.269043&amp;ie=UTF8&amp;ll=39.876019,-4.416504&amp;spn=9.271323,17.578125&amp;z=6&amp;output=embed"></iframe><br /><small><a href="http://maps.google.com/maps?f=q&amp;source=embed&amp;hl=es&amp;geocode=&amp;q=http:%%2F%%2Ftoolserver.org%%2F~emijrp%%2Fwlm%%2Fwlm.kml%%3Fusecache%%3D0&amp;sll=40.913513,-4.504395&amp;sspn=11.352924,23.269043&amp;ie=UTF8&amp;ll=39.876019,-4.416504&amp;spn=9.271323,17.578125&amp;z=6" style="color:#0000FF;text-align:left">Ver mapa más grande</a></small>
<br/>
<br/>
<i>Last update: %s (UTC)</i>
<br/>
</center>
</body>

</html>
""" % (total, missingcoordinates, missingcoordinates/(total/100.0), missingimages, missingimages/(total/100.0), imageyesurl, imagenourl, datetime.datetime.now())

f = open('/home/emijrp/public_html/wlm/index.php', 'w')
f.write(output.encode('utf-8'))
f.close()

