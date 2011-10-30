# -*- coding: utf-8 -*-

# Copyright (C) 2011 emijrp
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
import os
import re
import sys

import wikipedia
import xmlreader

def cleantitle(title):
    title = re.sub(ur"[&]", ur"-", title)
    return title

dumppath = ''
if len(sys.argv) == 2:
    dumpfilename = sys.argv[1]

#download commons dump
dumppath = '/mnt/user-store/emijrp'
dumpfilename = 'commonswiki-latest-pages-articles.xml.bz2'
os.system('wget -c http://dumps.wikimedia.org/commonswiki/latest/commonswiki-latest-pages-articles.xml.bz2 -O %s/%s' % (dumppath, dumpfilename))

xml = xmlreader.XmlDump('%s%s' % (dumppath and '%s/' % dumppath or '', dumpfilename), allrevisions=False)
errors = 0
minplaces = 1 #min places to show for year
maximages = 50 #max images to show in the sum all years
c = 0
s = 0
coord_dec_r = re.compile(ur"(?im)(?P<all>{{\s*(Location dec|Object location dec)\s*\|\s*(?P<lat>[\d\.\-\+]+)\s*\|\s*(?P<lon>[\d\.\-\+]+)\s*\|?\s*[^\|\}]*\s*}})")
coord_r = re.compile(ur"(?im)(?P<all>{{\s*(Location|Object location)\s*\|\s*(?P<lat_d>[\d\.\-\+]+)\s*\|\s*(?P<lat_m>[\d\.\-\+]+)\s*\|\s*(?P<lat_s>[\d\.\-\+]+)\s*\|\s*(?P<lat>[NS])\s*\|\s*(?P<lon_d>[\d\.\-\+]+)\s*\|\s*(?P<lon_m>[\d\.\-\+]+)\s*\|\s*(?P<lon_s>[\d\.\-\+]+)\s*\|\s*(?P<lon>[EW])\s*\|?\s*[^\|\}]*\s*}})")
date_r = re.compile(ur"(?im)^\s*\|\s*Date\s*=\s*(?P<date>(\d{4}(-\d{2}-\d{2})?))\D")

images_by_year = {}
for x in xml.parse(): #parsing the whole dump
    if not x.title.startswith('File:'):
        continue
    c += 1
    coord, date = [], ''
    x_text_encoded = x.text.encode('utf-8')
    
    #date
    m = re.finditer(date_r, x_text_encoded)
    year = ''
    for i in m:
        date = i.group('date')
        year = int(date[:4])
    
    if not date or year >= 2000 or year < 1825:
        continue
    
    #coord
    m = re.finditer(coord_dec_r, x_text_encoded)
    for i in m:
        coord = [float(i.group('lat')), float(i.group('lon'))]
        #print date, i.group('all'), coord
        break
    
    if not coord:
        m = re.finditer(coord_r, x_text_encoded)
        for i in m:
            lat = abs(float(i.group('lat_d'))) + abs(float(i.group('lat_m')))/60.0 + abs(float(i.group('lat_s')))/3600.0
            if i.group('lat').strip().upper() == 'N':
                lat = abs(lat)
            elif i.group('lat').strip().upper() == 'S':
                lat = abs(lat) * -1
            else:
                coord = []
                break
            lon = abs(float(i.group('lon_d'))) + abs(float(i.group('lon_m')))/60.0 + abs(float(i.group('lon_s')))/3600.0
            if i.group('lon').strip().upper() == 'E':
                lon = abs(lon)
            elif i.group('lon').strip().upper() == 'W':
                lon = abs(lon) * -1
            else:
                coord = []
                break
            coord = [lat, lon]
            #print date, i.group('all'), coord
            break
    
    if not coord:
        continue
    
    #print x.title, coord, date
    s += 1
    if images_by_year.has_key(year):
        images_by_year[year].append([x.title, coord[0], coord[1], date])
    else:
        images_by_year[year] = [[x.title, coord[0], coord[1], date]]

    if s and s % 10 == 0:
        print 'Total images', c, 'With useful metadata', s, 'Percent', s/(c/100.0),'%'

    if s and s % maximages == 0:
        break

kmlini = u"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
    <name>Wikimedia Commons Explorer</name>
    <description>Image maps by date</description>
    """
kmlend = u"""
    </Document>
</kml>"""

#generating KMLs by year
for year, images in images_by_year.items():
    if len(images) < minplaces:
        continue
    
    output = kmlini
    for title, lat, lon, date in images:
        imagesize = '150px'
        filename = re.sub('File:', ur'', title)
        filename = re.sub(' ', '_', filename)
        m5 = md5.new(filename.encode('utf-8')).hexdigest()
        thumburl = u'https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%s-%s' % (m5[0], m5[:2], filename, imagesize, filename)
        commonspage = u'https://commons.wikimedia.org/wiki/File:%s' % (filename)
        output += u"""
<Placemark>
<name>%s</name>
<description>
<![CDATA[
<a href="%s" target="_blank"><img src="%s" width=%s align=right/></a>
<table>
<tr><td><b>Coord:</b></td><td>%s, %s</td></tr>
<tr><td><b>Date:</b></td><td>%s</td></tr>
</table>
]]>
</description>
<Point>
<coordinates>%s,%s</coordinates>
</Point>
</Placemark>""" % (cleantitle(title), commonspage, thumburl, imagesize, lon, lat, date, lon, lat)
    
    output += kmlend
    f = open('/home/emijrp/public_html/commonsexplorer/%s.kml' % (year), 'w')
    f.write(output.encode('utf-8'))
    f.close()


#generating index.php
years = []
for year, v in images_by_year.items():
    if len(v) >= minplaces:
        years.append(year)
years.sort()
decade = ''
decadeyears = []
select = []
for year in years:
    decadeyears.append(year)
    if not decade:
        decade = year / 10 * 10
    if decade != year / 10 * 10:
        decadeyears.sort()
        select.append("""<a href="javascript:showHide('%ss-years')"><b>%ss</b></a><span id="%ss-years" style="display: none;">%s</span>""" % (decade, decade, decade, ', '.join(['<a href="index.php?year=%s">%s</a>' % (decadeyear, decadeyear) for decadeyear in decadeyears])))
        decade = year / 10 * 10
        decadeyears = [year]

output = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Wikimedia Commons Explorer</title>
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
$years = array(%s );
$year="1949";
if (isset($_GET['year']))
{
	$temp = $_GET['year'];
	if (in_array($temp, $years))
		$year = $temp;
}

?>

<body>

<center>
<big><big><big><b>Wikimedia Commons Explorer</b></big></big></big>
<br/>

<tr>
<td colspan=3>
<b>Select a year:</b> %s

<br/>

<iframe width="1200" height="500" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://maps.google.com/maps?f=q&amp;source=s_q&amp;hl=es&amp;geocode=&amp;q=http:%%2F%%2Ftoolserver.org%%2F~emijrp%%2Fcommonsexplorer%%2F<?php echo $year; ?>.kml%%3Fusecache%%3D0&amp;output=embed"></iframe>
<br/>

<i>Last update: %s (UTC)</i>

</center>

</body>

</html>
""" % (', '.join(['"%s"' % (year) for year in years]), ', '.join(select), datetime.datetime.now())

f = open('/home/emijrp/public_html/commonsexplorer/index.php', 'w')
f.write(output.encode('utf-8'))
f.close()
