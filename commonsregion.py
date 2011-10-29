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

#pre = [wikipedia.Page(commonssite, u"User:Emijrp/Sandbox")]
for page in pre:
    time.sleep(0.001)
    if not page.exists() or page.isRedirectPage() or page.isDisambig():
        continue
    if page.namespace() != 6:
        continue
    
    wtitle = page.title()
    wtext = page.get()
    newtext = wtext
    
    print wtitle, 'https://commons.wikimedia.org/wiki/%s' % (wtitle)
    
    m = re.finditer(ur"(?im)(?P<all>(?P<templatebegin>\{\{\s*(Location dec|Object location dec)\s*\|\s*(?P<lat>[\d\.\-\+]+)\s*\|\s*(?P<lon>[\d\.\-\+]+)\s*)\|?(?P<otherparams>\s*(_?scala:_?\d+_?|_?heading:_?[\dNSEW]+_?){0,2}\s*)(?P<templateend>\}\}))", wtext)
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
            if archive[latlon]:
                countrycode, iso = archive[latlon]
            else:
                print '...and failed'
                pass #countrycode and iso are blank so, the next if must fail, there is no replace, and exit
        else:
            f = urllib.urlopen("http://api.geonames.org/countrySubdivision?lat=%s&lng=%s&username=%s" % (lat, lon, geonamesusername))
            raw = f.read()
            try:
                countrycode = re.findall(ur"<countryCode>([A-Z]{2})</countryCode>", raw)[0]
                #ISO3166-2 puede ser números también (https://en.wikipedia.org/wiki/ISO_3166-2#Format), como en Austria AT-7 http://api.geonames.org/countrySubdivision?lat=47.46125&lng=10.8343&username=demo o una única letra como en Francia FR-P http://api.geonames.org/countrySubdivision?lat=49.1836302&lng=-0.361433&username=demo
                iso = re.findall(ur'<code type="ISO3166-2">([A-Z\d]{1,3})</code>', raw)[0]
            except:
                pass
            if countrycode:
                archive[latlon] = [countrycode, iso] #iso may be blank
            else:
                archive[latlon] = []
        
        if countrycode:
            if iso:
                region = '%s-%s' % (countrycode, iso)
            else:
                region = countrycode
            print "Region: %s" % (region)
            rep = i.group('all')
            sub = u"%s|region:%s%s%s" % (i.group('templatebegin'), region, i.group('otherparams') and '_%s' % (i.group('otherparams')) or '', i.group('templateend'))
            #print rep, '\n', sub
            newtext = newtext.replace(rep, sub) #replace all occurences for this exact templatebegin and templateend, it doesn't touch templates with more parameters (see 'abc' here  https://commons.wikimedia.org/w/index.php?title=User%3AEmijrp%2FSandbox&action=historysubmit&diff=61477235&oldid=61477216)
            summary.append(u'region ([[:en:ISO 3166-2:%s|%s]]%s) to coordinates (%s,%s)' % (countrycode, countrycode, iso and '-[[:en:ISO 3166-2:%s|%s]]' % (region, iso) or '', lat, lon))
    
    if newtext != wtext:
        wikipedia.showDiff(wtext, newtext)
        page.put(newtext, u"BOT - Adding %s using http://www.geonames.org webservices" % (', '.join(summary)))
    
