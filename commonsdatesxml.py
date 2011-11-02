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
    }
    
    dumppath = ''
    if len(sys.argv) == 2:
        dumpfilename = sys.argv[1]

    xml = xmlreader.XmlDump('%s%s' % (dumppath and '%s/' % dumppath or '', dumpfilename), allrevisions=False)
    c = 0
    
    for x in xml.parse(): #parsing the whole dump
        if not x.title.strip().startswith('File:'):
            continue
        c += 1
        
        #regexps
        regexp_r = ur"(?im)^(?P<all>\s*\|\s*Date\s*=\s*(?P<date>(?P<day>[1-9]|1[0-9]|2[0-9]|3[0-1])\s*(?P<month>January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sept?|October|Oct|November|Nov|December|Dec)\s*(?P<year>\d{4}))\s*)$"
        
        m = re.findall(regexp_r, x.text) #check dump text
        if m:
            page = wikipedia.Page(wikipedia.Site("commons", "commons"), x.title)
            wtext = page.get()
            newtext = wtext
            m = re.finditer(regexp_r, wtext) # check live text
            for i in m:
                print x.title
                
                #replacement
                regexp_rep = i.group('date')
                regexp_sub = ur"%s-%s-%02d" % (i.group('year'), month2number[i.group('month').strip().lower()], int(i.group('day')))
                
                newtext = newtext.replace(regexp_rep, regexp_sub, 1)
                
                if wtext != newtext:
                    wikipedia.showDiff(wtext, newtext)
                    page.put(newtext, u"BOT - Changes to allow localization: %s → %s" % (regexp_rep, regexp_sub))
                
if __name__ == "__main__":
    main()
