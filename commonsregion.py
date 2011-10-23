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

import wikipedia
import pagegenerators
import re
import urllib
import time
import sys

geonamesusername = sys.argv[1]

commonssite = wikipedia.Site("commons", "commons")
locationdecpage = wikipedia.Page(commonssite, u"Template:Location dec")

gen = pagegenerators.ReferringPageGenerator(locationdecpage, onlyTemplateInclusion=True)
pre = pagegenerators.PreloadingGenerator(gen, pageNumber=100)

#http://api.geonames.org/countrySubdivision?lat=52.0893&lng=5.1102&username=demo
"""
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<geonames>
<countrySubdivision>
<countryCode>NL</countryCode>
<countryName>Netherlands</countryName>
<adminCode1>09</adminCode1>
<adminName1>Utrecht</adminName1>
<code type="FIPS10-4">09</code>
<code type="ISO3166-2">UT</code>
<distance>0.0</distance>

</countrySubdivision>
</geonames>
"""
#https://commons.wikimedia.org/w/index.php?title=File:BordUtrecht.jpg&diff=prev&oldid=61461464

archive = {}

for page in pre:
    time.sleep(0.1)
    if not page.exists() or page.isRedirectPage() or page.isDisambig():
        continue
    if page.namespace() != 6:
        continue
    
    wtitle = page.title()
    wtext = page.get()
    newtext = wtext
    
    print '\n', wtitle, 'https://commons.wikimedia.org/wiki/%s' % (wtitle)
    #solo plantillas que tengan 2 parámetros (lat y lon) y el tercero esté vacío
    m = re.finditer(ur"(?im)((?P<template>\{\{\s*(Location dec|Object location dec)\s*\|\s*(?P<lat>[\d\.\-\+]+)\s*\|\s*(?P<lon>[\d\.\-\+]+))\s*\|?\s*\}\})", wtext)
    if not m:
        print 'Skiping...'
        continue
    
    summary = []
    for i in m:
        lat, lon = i.group('lat'), i.group('lon')
        countrycode, iso = '', ''
        
        if lat and lon:
            latlon = '%s,%s' % (lat, lon)
            print 'Calculating region for %s' % (latlon)
        else:
            break
        
        if archive.has_key(latlon):
            print 'Region for %s was calculated before...' % (latlon)
            countrycode, iso = archive[latlon]
        else:
            f = urllib.urlopen("http://api.geonames.org/countrySubdivision?lat=%s&lng=%s&username=%s" % (lat, lon, geonamesusername))
            raw = f.read()
            countrycode = re.findall(ur"<countryCode>([A-Z]{2})</countryCode>", raw)[0]
            iso = re.findall(ur'<code type="ISO3166-2">([A-Z]{2,3})</code>', raw)[0]
            if countrycode and iso:
                archive[latlon] = [countrycode, iso]
        
        if countrycode and iso:
            region = '%s-%s' % (countrycode, iso)
            newtext = newtext.replace(i.group('template'), u"%s|region:%s" % (i.group('template'), region), 1)
            summary.append(u'region ([[:en:ISO 3166-2:%s|%s]]-[[:en:ISO 3166-2:%s|%s]]) to coordinates (%s,%s)' % (countrycode, countrycode, region, iso, lat, lon))
    
    if newtext != wtext:
        wikipedia.showDiff(wtext, newtext)
        page.put(newtext, u"BOT - Adding %s using http://www.geonames.org webservices" % (', '.join(summary)))
    
