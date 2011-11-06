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

def main():
    """Localisation for dates (YYYY-MM-DD) and some usual headings in images descriptions in Commons"""
    
    month2number={
        #English
        u"january":u"01", u"jan":u"01", 
        u"february":u"02", u"feb":u"02", 
        u"march":u"03", u"mar":u"03", 
        u"april":u"04", u"apr":u"04", 
        u"may":u"05", 
        u"june":u"06", u"jun":u"06", 
        u"july":u"07", u"jul":u"07", 
        u"august":u"08", u"aug":u"08", 
        u"september":u"09", u"sep":u"09", u"sept":u"09", 
        u"october":u"10", u"oct":u"10", 
        u"november":u"11", u"nov":u"11", 
        u"december":u"12", u"dec":u"12",
        
        #Spanish
        u"enero":u"01", u"ene":u"01", 
        u"febrero":u"02", 
        u"marzo":u"03",
        u"abril":u"04", u"abr":u"04", 
        u"mayo":u"05",
        u"junio":u"06", 
        u"julio":u"07", 
        u"agosto":u"08", u"ago":u"08", u"agos":u"08", 
        u"setiembre":u"09", u"septiembre":u"09",
        u"octubre":u"10",
        u"noviembre":u"11",
        u"diciembre":u"12", u"dic":u"12",
        
        #french
        
        #german
    }
    
    dumppath = ''
    dumpfilename = ''
    mode = ''
    skip = 'File:Itanos R03.jpg' #'File:Lagothrix lagotricha.jpg'
    if len(sys.argv) >= 2:
        dumpfilename = sys.argv[1]
    if len(sys.argv) >= 3: #en1, fr1, etc, regexps
        mode = sys.argv[2]
    if not mode:
        mode = 'en1'
    if len(sys.argv) >= 4:
        skip = sys.argv[3]
    
    xml = xmlreader.XmlDump('%s%s' % (dumppath and '%s/' % dumppath or '', dumpfilename), allrevisions=False)
    c = 0
    
    if skip:
        print 'Skiping to...', skip
    for x in xml.parse(): #parsing the whole dump
        if not x.title.strip().startswith('File:'):
            continue
        c += 1
        if skip:
            if x.title.strip() != skip:
                continue
            else:
                skip = ''
        
        #regexps
        regexp_r = {
            'en1': ur"(?im)^(?P<all>(?P<ini>\s*\|\s*Date\s*=\s*)(?P<date>(?P<day>[1-9]|1[0-9]|2[0-9]|3[0-1])\s*(?P<month>January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sept?|October|Oct|November|Nov|December|Dec)\s*(?P<year>\d{4}))(?P<end>\s*))$",
            'es1': ur"(?im)^(?P<all>(?P<ini>\s*\|\s*Date\s*=\s*)(?P<date>(?P<day>[1-9]|1[0-9]|2[0-9]|3[0-1])\s+de\s+(?P<month>Enero|Ene|Febrero|Feb|Marzo|Mar|Abril|Abr|Mayo|May|Junio|Jun|Julio|Jul|Agosto|Ago|Septiembre|Sept?|Octubre|Oct|Noviembre|Nov|Diciembre|Dic)\s+de\s+(?P<year>\d{4}))(?P<end>\s*))$",
            
        }
        
        m = re.findall(regexp_r[mode], x.text) # check dump text
        if m:
            print c, 'DUMP SAYS: ', x.title
            
            page = wikipedia.Page(wikipedia.Site("commons", "commons"), x.title)
            if not page.exists() or page.isRedirectPage() or page.isDisambig():
                continue #next page in dump
            if not page.canBeEdited():
                continue
            
            wtext = page.get()
            newtext = wtext
            
            m = re.finditer(regexp_r[mode], wtext) # check live text
            for i in m:
                print '   LIVE TEXT NEED TRANSLATION:', x.title
                
                #replacement
                regexp_rep = {
                    'en1': i.group('all'),
                    'es1': i.group('all'),
                    
                }
                #sub
                regexp_sub = { 
                    'en1': ur"%s%s-%s-%02d%s" % (i.group('ini'), i.group('year'), month2number[i.group('month').strip().lower()], int(i.group('day')), i.group('end')),
                    'es1': ur"%s%s-%s-%02d%s" % (i.group('ini'), i.group('year'), month2number[i.group('month').strip().lower()], int(i.group('day')), i.group('end')),
                    
                }
                
                newtext = newtext.replace(regexp_rep[mode], regexp_sub[mode], 1)
                
                if wtext != newtext:
                    wikipedia.showDiff(wtext, newtext)
                    page.put(newtext, u"BOT - Changes to allow localization: %s → %s" % (regexp_rep[mode], regexp_sub[mode]))
                
                break #only one replacement and break
                
if __name__ == "__main__":
    main()
