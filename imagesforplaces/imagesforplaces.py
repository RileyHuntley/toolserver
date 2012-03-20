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
    """
kmlend = u"""
    </Document>
</kml>"""

zones = {
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
        output += u"""
    <Placemark>
    <name>%s</name>
    <description>
        <![CDATA[
        <table width=350px>
        <tr><td>Article:</b><br/><a href='http://es.wikipedia.org/wiki/%s'>%s</a></td></tr>
        <tr><td><b>Coordinates:</b><br/>%s, %s</td></tr>
        </table>
        ]]>
    </description>
    <Point>
        <coordinates>%s,%s</coordinates>
    </Point>
    </Placemark>""" % (len(title_clean) > 37 and '%s...' % (title_clean[:37]) or title_clean, re.sub(' ', '_', title), title, lon, lat, lon, lat)
    
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
        zones = [%s];
        zones_label = [%s];
        for (i=0;i<zones.length;i++){
            var mylayer = new OpenLayers.Layer.Vector(zones_label[i], {
                projection: map.displayProjection,
                strategies: [new OpenLayers.Strategy.Fixed()],
                protocol: new OpenLayers.Protocol.HTTP({
                    url: "http://toolserver.org/~emijrp/imagesforplaces/kml/"+zones[i]+".kml",
                    format: new OpenLayers.Format.KML({
                        extractStyles: true,
                        extractAttributes: true
                    })
                })
            });
            if (zones[i] == 'spain') {
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
""" % (', '.join(['"%s"' % (zone) for zone in zones]), ', '.join(['"%s"' % (zone) for zone in zones]))

f = open('%s/index.php' % (path), 'w')
f.write(output.encode('utf-8'))
f.close()
