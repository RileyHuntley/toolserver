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
minpics = 1 #min pics to show for year
maximages = 10 #max images to show in the sum all years
maxyear = 2000
minyear = 1900
c = 0
s = 0
coord_dec_r = re.compile(ur"(?im)(?P<all>{{\s*(Location dec|Object location dec)\s*\|\s*(?P<lat>[\d\.\-\+]+)\s*\|\s*(?P<lon>[\d\.\-\+]+)\s*\|?\s*[^\|\}]*\s*}})")
coord_r = re.compile(ur"(?im)(?P<all>{{\s*(Location|Object location)\s*\|\s*(?P<lat_d>[\d\.\-\+]+)\s*\|\s*(?P<lat_m>[\d\.\-\+]+)\s*\|\s*(?P<lat_s>[\d\.\-\+]+)\s*\|\s*(?P<lat>[NS])\s*\|\s*(?P<lon_d>[\d\.\-\+]+)\s*\|\s*(?P<lon_m>[\d\.\-\+]+)\s*\|\s*(?P<lon_s>[\d\.\-\+]+)\s*\|\s*(?P<lon>[EW])\s*\|?\s*[^\|\}]*\s*}})")
date_r = re.compile(ur"(?im)^\s*\|\s*Date\s*=\s*(?P<date>(\d{4}(-\d{2}-\d{2})?))\D")
description_r = re.compile(ur"(?im)\{\{\s*en\s*\|\s*(1\s*\=)?\s*(?P<description>[^\{\}]{10,300})\s*\}\}")

images_by_year = {}
for x in xml.parse(): #parsing the whole dump
    if not x.title.startswith('File:'):
        continue
    c += 1
    coord, date, description = [], '', ''
    
    #date
    m = re.finditer(date_r, x.text)
    year = ''
    for i in m:
        date = i.group('date')
        year = int(date[:4])
    
    if not date or year >= maxyear or year < minyear:
        continue
    
    #coord
    m = re.finditer(coord_dec_r, x.text)
    for i in m:
        coord = [float(i.group('lat')), float(i.group('lon'))]
        #print date, i.group('all'), coord
        break
    
    if not coord:
        m = re.finditer(coord_r, x.text)
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
    
    #description
    m = re.finditer(description_r, x.text)
    for i in m:
        description = i.group('description')
        description = re.sub(ur"\[\[[^\[\]\|]*\|([^\[\]\|]*)\]\]", ur"\1", description)
        description = re.sub(ur"\[\[([^\[\]\|]*)\]\]", ur"\1", description)
        description = re.sub(ur"\'{2,3}", ur"", description)
        break
    
    #print x.title, coord, date
    s += 1
    if images_by_year.has_key(year):
        images_by_year[year].append([x.title, coord[0], coord[1], date, description])
    else:
        images_by_year[year] = [[x.title, coord[0], coord[1], date, description]]

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
    if len(images) < minpics:
        continue
    
    output = kmlini
    for title, lat, lon, date, description in images:
        imagesize = '150px'
        filename = re.sub('File:', ur'', title)
        filename = re.sub(' ', '_', filename)
        m5 = md5.new(filename.encode('utf-8')).hexdigest()
        thumburl = u'https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%s-%s' % (m5[0], m5[:2], filename, imagesize, filename)
        commonspage = u'https://commons.wikimedia.org/wiki/File:%s' % (filename)
        output += u"""  <Placemark>
    <name>%s</name>
    <description>
    <![CDATA[
    <table width=350px>
    <tr><td><b>Description:</b><br/>%s</td><td rowspan=3><a href="%s" target="_blank"><img src="%s" width=%s align=right/></a></td></tr>
    <tr><td><b>Date:</b><br/>%s</td></tr>
    <tr><td><b>Coord:</b><br/>%s, %s</td></tr>
    </table>
    ]]>
    </description>
    <Point>
        <coordinates>%s,%s</coordinates>
    </Point>
    </Placemark>""" % (cleantitle(title), description and description or '?', commonspage, thumburl, imagesize, date, lon, lat, lon, lat)
    
    output += kmlend
    f = open('/home/emijrp/public_html/commonsexplorer/kml/%s.kml' % (year), 'w')
    f.write(output.encode('utf-8'))
    f.close()


#generating index.php
years = []
for year, v in images_by_year.items():
    if len(v) >= minpics:
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
    <style>
        html,body {
            height: 98.5%%;
            width: 99.5%%;
        }
        #map {
            width: 100%%;
            height: 100%%;
        }
    </style>
    <script src='http://openlayers.org/api/OpenLayers.js'></script>
</head>
<body onload="init()">
<!-- Code adapted from OpenLayers example http://openlayers.org/dev/examples/sundials-spherical-mercator.html -->

<script type="text/javascript">
    var map, select;

    function init(){
        var options = {
            projection: new OpenLayers.Projection("EPSG:900913"),
            displayProjection: new OpenLayers.Projection("EPSG:4326"),
            units: "m",
            maxResolution: 156543.0339,
            maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
                                             20037508.34, 20037508.34),
        };
        map = new OpenLayers.Map('map', options);
        
        var mapnik = new OpenLayers.Layer.OSM("OpenStreetMap (Mapnik)");
        //var gmap = new OpenLayers.Layer.Google("Google", {sphericalMercator:true});
        mylayers = [];
        years = [%s];
        for (i=0;i<years.length;i++){
            var mylayer = new OpenLayers.Layer.Vector(years[i], {
                projection: map.displayProjection,
                strategies: [new OpenLayers.Strategy.Fixed()],
                protocol: new OpenLayers.Protocol.HTTP({
                    url: "http://toolserver.org/~emijrp/commonsexplorer/kml/"+years[i]+".kml",
                    format: new OpenLayers.Format.KML({
                        extractStyles: true,
                        extractAttributes: true
                    })
                })
            });
            if (years[i] == '1950') {
                mylayer.setVisibility(true);
            }else{
                mylayer.setVisibility(false);
            }
            mylayers = mylayers.concat([mylayer]);
        }
        
        layers = [mapnik];
        map.addLayers(layers.concat(mylayers));

        select = new OpenLayers.Control.SelectFeature(mylayers);
        
        for (i=1;i<mylayers.length;i++){
            mylayers[i].events.on({
                "featureselected": onFeatureSelect,
                "featureunselected": onFeatureUnselect
            });
        }

        map.addControl(select);
        select.activate();   

        map.addControl(new OpenLayers.Control.LayerSwitcher());

        map.zoomToExtent(
            new OpenLayers.Bounds(
                -100, -70, 100, 70
            ).transform(map.displayProjection, map.projection)
        );
    }
    function onPopupClose(evt) {
        select.unselectAll();
    }
    function onFeatureSelect(event) {
        var feature = event.feature;
        var selectedFeature = feature;
        var popup = new OpenLayers.Popup.FramedCloud("chicken", 
            feature.geometry.getBounds().getCenterLonLat(),
            new OpenLayers.Size(100,100),
            "<h4>"+feature.attributes.name + "</h4>" + feature.attributes.description,
            null, true, onPopupClose
        );
        feature.popup = popup;
        map.addPopup(popup);
    }
    function onFeatureUnselect(event) {
        var feature = event.feature;
        if(feature.popup) {
            map.removePopup(feature.popup);
            feature.popup.destroy();
            delete feature.popup;
        }
    }
</script>

<div id="map" class="smallmap"></div>

</body>
</html>
""" % (', '.join(['"%s"' % (year) for year in years]))

f = open('/home/emijrp/public_html/commonsexplorer/index.php', 'w')
f.write(output.encode('utf-8'))
f.close()
