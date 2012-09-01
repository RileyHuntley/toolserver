#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011-2012 emijrp <emijrp@gmail.com>
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

import _mysql
import md5
import os
import re

path = '/home/emijrp/public_html/wlm'
codification = 'iso-8859-1'
conn = _mysql.connect(host='sql.toolserver.org', db='p_erfgoed_p', read_default_file='~/.my.cnf')
countrynames = {
    'ad': 'Andorra', 
    'ar': 'Argentina', 
    'at': 'Austria', 
    'ch': 'Switzerland',
    'cl': 'Chile',
    'co': 'Colombia',
    'cz': 'Czech Republic',
    'ee': 'Estonia',
    'es': 'Spain',
    'fr': 'France',
    'ie': 'Ireland',
    'il': 'Israel',
    'in': 'India',
    'it': 'Italy',
    'lu': 'Luxembourg', 
    'mt': 'Malta', 
    'nl': 'Netherlands', 
    'pa': 'Panama',
    'pt': 'Portugal',
    'ro': 'Romania',
    'ru': 'Russia',
    'sk': 'Slovakia',
    'ua': 'Ukraine',
    'us': 'United States',
    'za': 'South Africa',
}
for country in countrynames.keys():
    country_ = re.sub(' ', '', countrynames[country].lower())
    if not os.path.exists('%s/%s/' % (path, country_)):
        os.makedirs('%s/%s/' % (path, country_))
    adm0 = country
    conn.query("SELECT * from monuments_all where country='%s';" % (country))
    r=conn.use_result()
    row=r.fetch_row(maxrows=1, how=1)
    monuments = {}
    while row:
        #print row[0]
        monuments[row[0]['id']] = {
            'id': unicode(row[0]['id'], codification),
            'lang': row[0]['lang'],
            'registrant_url': row[0]['registrant_url'],
            'monument_article': unicode(row[0]['monument_article'], codification),
            'name': unicode(row[0]['name'], codification),
            'municipality': unicode(row[0]['municipality'], codification),
            'adm0': row[0]['adm0'] and row[0]['adm0'].lower() or '', 
            'adm1': row[0]['adm1'] and row[0]['adm1'].lower() or '', 
            'adm2': row[0]['adm2'] and row[0]['adm2'].lower() or '', 
            'adm3': row[0]['adm3'] and row[0]['adm3'].lower() or '', 
            'adm4': row[0]['adm4'] and row[0]['adm4'].lower() or '', 
            'address': unicode(row[0]['address'], codification), 
            'lat': row[0]['lat'] and row[0]['lat'] or 0,  
            'lon': row[0]['lon'] and row[0]['lon'] or 0, 
            'image': row[0]['image'] and unicode(row[0]['image'], codification) or '', 
        }
        row=r.fetch_row(maxrows=1, how=1)
    
    adm = 0
    if len(monuments.keys()) >= 1000:
        adm = 1
    
    for admname in set([v['adm%s' % (adm)] for k, v in monuments.items()]):
        if not admname:
            admname = 'other'
        
        imageyesurl = u'http://maps.google.com/mapfiles/kml/paddle/red-stars.png'
        imagenourl = u'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
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
        
        imagesize = '150px'
        for id, props in monuments.items():
            if props['lat'] == 0 and props['lon'] == 0:
                continue
            
            if adm:
                if props['adm%s' % (adm)] != admname:
                    continue
            
            imagefilename = re.sub(' ', '_', props['image'])
            m5 = md5.new(imagefilename.encode('utf-8')).hexdigest()
            thumburl = u'http://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%s-%s' % (m5[0], m5[:2], imagefilename, imagesize, imagefilename)

            output += u"""
            <Placemark>
            <name>%s</name>
            <description>
            <![CDATA[
            <table border=0 cellspacing=3px cellpadding=3px>
            <tr><td align=right width=80px style="background-color: lightgreen;"><b>Name:</b></td><td><a href="http://%s.wikipedia.org/wiki/%s" target="_blank">%s</a></td><td rowspan=4><a href="http://commons.wikimedia.org/wiki/File:%s" target="_blank"><img src="%s" width=%s/></a></td></tr>
            <tr><td align=right style="background-color: lightblue;"><b>Location:</b></td><td>%s</td></tr>
            <tr><td align=right style="background-color: yellow;"><b>ID:</b></td><td>%s</td></tr>
            <tr><td align=center colspan=2><br/><b>This monument has %s<br/>you can upload yours. Thanks!</b><br/><br/><span style="border: 2px solid black;background-color: pink;padding: 3px;"><a href="http://commons.wikimedia.org/w/index.php?title=Special:UploadWizard&campaign=wlm-%s&id=%s&lat=%s&lon=%s&descriptionlang=%s
    #&description=%s" target="_blank"><b>Upload</b></a></span></td></tr>
            </table>
            ]]>
            </description>
            <styleUrl>#%s</styleUrl>
            <Point>
            <coordinates>%s,%s</coordinates>
            </Point>
            </Placemark>""" % (props['name'], props['lang'], props['monument_article'], props['name'], props['image'], thumburl, imagesize, props['municipality'], id, props['image'] and 'images, but' or 'no images,', country, id, props['lat'], props['lon'], props['lang'], props['name'], props['image'] and 'imageyes' or 'imageno', props['lon'], props['lat'])
        
        output += u"""
            </Document>
        </kml>"""
        
        f = open('%s/%s/wlm-%s.kml' % (path, country_, adm == 0 and country_ or admname), 'w')
        f.write(output.encode('utf-8'))
        f.close()
    
    
