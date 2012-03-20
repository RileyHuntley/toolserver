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
kmlini = u"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
    <name>Images for places</name>
    <description>Missing images by place</description>
    <Style id="no">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/paddle/red-stars.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="mu">
      <IconStyle>
        <Icon>
          <href>http://google-maps-icons.googlecode.com/files/museum-historical.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="pa">
      <IconStyle>
        <Icon>
          <href>http://google-maps-icons.googlecode.com/files/park.png</href>
        </Icon>
      </IconStyle>
    </Style>
    """
kmlend = u"""
    </Document>
</kml>"""

zones = {
    'all': {'maxlat': 90, 'minlat': -90, 'maxlon': 179, 'minlon': -179},
    'spain': {'maxlat': 44, 'minlat': 35, 'maxlon': 5, 'minlon': -10}
}

#get all places without images
points = []
conn = MySQLdb.connect(host='sql-s7', db='eswiki_p', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT page_title, gc_lat, gc_lon, page_len from u_dispenser_p.coord_eswiki join page on page_id=gc_from where page_namespace=0 and gc_from not in (select distinct il_from from imagelinks where 1) group by page_title order by page_title")
row = cursor.fetchone()
while row:
    page_title = re.sub(ur"_", ur" ", unicode(row[0], "utf-8"))
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
        if title.startswith('Museo') or title.startswith(u'Galería'):
            placetype = 'mu'
        elif title.startswith('Parque') or title.startswith(u'Jardín'):
            placetype = 'pa'
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
<body>

<h2 align=center>Images for places</h2>

<center><iframe width="1000" height="600" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://maps.google.es/maps?f=q&amp;source=s_q&amp;hl=es&amp;geocode=&amp;q=http:%2F%2Ftoolserver.org%2F~emijrp%2Fimagesforplaces%2Fkml%2Fall.kml%3Fusecache%3D0&amp;output=embed"></iframe></center>

</body>
</html>
"""

f = open('%s/index.php' % (path), 'w')
f.write(output.encode('utf-8'))
f.close()
