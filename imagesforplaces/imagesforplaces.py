# -*- coding: utf-8 -*-

# Copyright (C) 2012 emijrp
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

import MySQLdb
import datetime
import md5
import os
import re
import sys

import wikipedia
import xmlreader

def cleantitle(title):
    title = re.sub(ur"[&]", ur"-", title)
    return title

path = '/home/emijrp/public_html/imagesforplaces'
icons = [
    ['no', 'http://maps.google.com/mapfiles/kml/paddle/red-stars.png', 'Unknown'],
    ['ai', 'http://google-maps-icons.googlecode.com/files/airport.png', 'Airport, heliport'],
    ['br', 'http://google-maps-icons.googlecode.com/files/bridgemodern.png', 'Bridge, aqueduct'],
    ['ch', 'http://google-maps-icons.googlecode.com/files/church2.png', 'Church, cathedral, convent'],
    ['es', 'http://google-maps-icons.googlecode.com/files/stadium.png', 'Estadio'],
    ['fa', 'http://google-maps-icons.googlecode.com/files/lighthouse.png', 'Lighthouse'],
    ['mo', 'http://google-maps-icons.googlecode.com/files/beautiful.png', 'Mountain, cave'],
    ['monu', 'http://google-maps-icons.googlecode.com/files/monument.png', 'Monument'],
    ['mu', 'http://google-maps-icons.googlecode.com/files/museum-historical.png', 'Museums, Galleries'], 
    ['ob', 'http://google-maps-icons.googlecode.com/files/observatory.png', 'Observatory'],
    ['pa', 'http://google-maps-icons.googlecode.com/files/park.png', 'Parks'],
    ['sc', 'http://google-maps-icons.googlecode.com/files/school.png', 'School'],
    ['sta', 'http://google-maps-icons.googlecode.com/files/bus.png', 'Station'],
    ['th', 'http://google-maps-icons.googlecode.com/files/theater.png', 'Theatre'],
    ['un', 'http://google-maps-icons.googlecode.com/files/university.png', 'University, faculty'],
    ['ce', 'http://google-maps-icons.googlecode.com/files/cemetary.png', 'Cemetery'],
]
kmlini = u"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
    <name>Images for places</name>
    <description>Missing images by place</description>
    %s
    """ % ('\n'.join(["""<Style id="%s">
      <IconStyle>
        <Icon>
          <href>%s</href>
        </Icon>
      </IconStyle>
    </Style>""" % (tag, icon) for tag, icon, desc in icons]))
kmlend = u"""
    </Document>
</kml>"""

zones = {
    'all': {'maxlat': 90, 'minlat': -90, 'maxlon': 179, 'minlon': -179},
    #'spain': {'maxlat': 44, 'minlat': 35, 'maxlon': 5, 'minlon': -10}
}

#get all places without images
points = []
conn = MySQLdb.connect(host='sql-s7', db='eswiki_p', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT page_title, gc_lat, gc_lon, page_len from u_dispenser_p.coord_eswiki join page on page_id=gc_from where page_namespace=0 and gc_from not in (select distinct il_from from imagelinks where 1) group by page_title order by page_title")
row = cursor.fetchone()
while row:
    page_title = re.sub(ur"_", ur" ", unicode(row[0], "utf-8"))
    if page_title.isdigit(): #year articles
        row = cursor.fetchone()  
        continue
    gc_lat = row[1]
    gc_lon = row[2]
    page_len = row[3]
    points.append([page_title, gc_lat, gc_lon, page_len])
    row = cursor.fetchone()    
cursor.close()
conn.close()

#generating KMLs by zone
for zone, coordlimits in zones.items():
    output = kmlini
    for title, lat, lon, pagelen in points:
        if not lat < coordlimits['maxlat'] or not lat > coordlimits['minlat'] or \
           not lon < coordlimits['maxlon'] or not lon > coordlimits['minlon']:
            continue
        title_clean = cleantitle(title)
        placetype = 'no'
        if title.startswith(u'Aeropuerto') or title.startswith(u'Helicóptero') or title.startswith(u'Aeródromo'):
            placetype = 'ai'
        elif title.startswith(u'Cementerio'):
            placetype = 'ce'
        elif title.startswith(u'Puente ') or title.startswith(u'Acueducto'):
            placetype = 'br'
        elif title.startswith(u'Iglesia') or title.startswith(u'Ermita') or title.startswith(u'Catedral') or title.startswith(u'Convento') or title.startswith(u'Monasterio') or title.startswith(u'Mezquita'):
            placetype = 'ch'
        elif title.startswith(u'Estadio'):
            placetype = 'es'
        elif title.startswith(u'Faro '):
            placetype = 'fa'
        elif title.startswith(u'Montaña') or title.startswith(u'Monte') or title.startswith(u'Pico') or title.startswith(u'Cerro') or title.startswith(u'Meseta') or title.startswith(u'Cueva'):
            placetype = 'mo'
        elif title.startswith(u'Palacio') or title.startswith(u'Casa de'):
            placetype = 'monu'
        elif title.startswith(u'Museo') or title.startswith(u'Galería'):
            placetype = 'mu'
        elif title.startswith(u'Observatorio'):
            placetype = 'ob'
        elif title.startswith(u'Parque') or title.startswith(u'Jardín'):
            placetype = 'pa'
        elif title.startswith(u'Colegio') or title.startswith(u'Escuela'):
            placetype = 'sc'
        elif title.startswith(u'Estación'):
            placetype = 'sta'
        elif title.startswith(u'Teatro'):
            placetype = 'th'
        elif title.startswith(u'Universidad') or title.startswith(u'Facultad'):
            placetype = 'un'
        output += u"""
    <Placemark>
    <name>%s</name>
    <description>
        <![CDATA[
        <a href="http://es.wikipedia.org/wiki/%s">Wikipedia</a>
        </ul>
        ]]>
    </description>
    <styleUrl>#%s</styleUrl>
    <Point>
        <coordinates>%s,%s</coordinates>
    </Point>
    </Placemark>""" % (len(title_clean) > 37 and '%s...' % (title_clean[:37]) or title_clean, re.sub(' ', '_', title), placetype, lon, lat)
    
    output += kmlend
    f = open('%s/kml/%s.kml' % (path, zone), 'w')
    f.write(output.encode('utf-8'))
    f.close()

#generating index.php

output = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Images for places</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
</head>
<body style="background-color:#cedff2;">

<h1 align=center><i>Images for places</i> <img src="http://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Crystal_128_camera_SVG.svg/35px-Crystal_128_camera_SVG.svg.png" /></h1>

<center>This map contains the <a href="http://toolserver.org/~dispenser/dumps/">location</a> for <b>%d</b> Wikipedia articles which have no images. Check <a href="http://commons.wikimedia.org/">Wikimedia Commons</a> before going to take a photo!<br/>%s<br/>
<iframe width="99%%" height="570px" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://maps.google.es/maps?f=q&amp;source=s_q&amp;hl=es&amp;geocode=&amp;q=http:%%2F%%2Ftoolserver.org%%2F~emijrp%%2Fimagesforplaces%%2Fkml%%2Fall.kml%%3Fusecache%%3D0&amp;output=embed"></iframe></center>

<center><i>This page was last updated on <!-- timestamp -->%s<!-- timestamp --> (UTC)</i>. This tool has been developed by <a href="http://toolserver.org/~emijrp/">emijrp</a>.</center>
</body>
</html>
""" % (len(points), u'&nbsp;&nbsp;'.join([u"<img src='%s' alt='%s' title='%s' width=25px />" % (icon, desc, desc) for tag, icon, desc in icons]), datetime.datetime.now())

f = open('%s/index.php' % (path), 'w')
f.write(output.encode('utf-8'))
f.close()
