# -*- coding: utf-8 -*-

# Copyright (C) 2011-2012 emijrp
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
    """Localisation for dates (YYYY-MM-DD)"""
    
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
    
    #regexps
    spliter1 = ur'[\s\-\,\.\/\\]*' #spliter for months in words
    spliter2 = ur'' #todo, spliter for dates with month in numbers
    suffix1 = ur'[\s\.]*(st|nd|rd|th)?[\s\.]*' # March 1st, ..., not mandatory
    regexp_r = {
        'en1': re.compile(ur"(?im)^(?P<all>(?P<ini>\s*\|\s*Date\s*=\s*)(?P<date>(?P<day>[1-9]|1[0-9]|2[0-9]|3[0-1])%s%s(?P<month>January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sept?|October|Oct|November|Nov|December|Dec)%s(?P<year>\d{4}))(?P<end>\s*))$" % (suffix1, spliter1, spliter1)),
        'en2': re.compile(ur"(?im)^(?P<all>(?P<ini>\s*\|\s*Date\s*=\s*)(?P<month>January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sept?|October|Oct|November|Nov|December|Dec)%s(?P<date>(?P<day>[1-9]|1[0-9]|2[0-9]|3[0-1])%s%s(?P<year>\d{4}))(?P<end>\s*))$" % (spliter1, suffix1, spliter1)),
        'es1': re.compile(ur"(?im)^(?P<all>(?P<ini>\s*\|\s*Date\s*=\s*)(?P<date>(?P<day>[1-9]|1[0-9]|2[0-9]|3[0-1])\s+de\s+(?P<month>Enero|Ene|Febrero|Feb|Marzo|Mar|Abril|Abr|Mayo|May|Junio|Jun|Julio|Jul|Agosto|Ago|Septiembre|Sept?|Octubre|Oct|Noviembre|Nov|Diciembre|Dic)\s+de\s+(?P<year>\d{4}))(?P<end>\s*))$"),
    }
    
    dumpfilename = ''
    modes = []
    skip = u'' #'File:Lagothrix lagotricha.jpg'
    if len(sys.argv) >= 2:
        dumpfilename = sys.argv[1]
    else:
        print 'python script.py dumpfilename [mode] [skipuntilthispage]'
        sys.exit()
    if len(sys.argv) >= 3: #en1, fr1, etc, regexps
        modes = [sys.argv[2]]
    if not modes:
        modes = regexp_r.keys()
    if len(sys.argv) >= 4:
        skip = sys.argv[3]
    
    xml = xmlreader.XmlDump(dumpfilename, allrevisions=False)
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
        
        for mode in modes:
            m = re.findall(regexp_r[mode], x.text) # check dump text
            if m:
                print c, 'Candidate found in dump: ', x.title
                
                page = wikipedia.Page(wikipedia.Site("commons", "commons"), x.title)
                if not page.exists() or page.isRedirectPage() or page.isDisambig():
                    print 'Page not found, deleted or redirect?'
                    continue #next page in dump
                if not page.canBeEdited():
                    print 'Page cannot be edited, protected?'
                    continue #next page in dump
                
                wtext = page.get()
                newtext = wtext
                
                if re.findall(regexp_r[mode], wtext):
                    m = re.finditer(regexp_r[mode], wtext) # check live text to verify that the date is still in Commons page
                    for i in m:
                        print '  Commons page has a date to translate:', x.title
                        
                        #text to remove
                        regexp_rep = {
                            'en1': i.group('all'),
                            'en2': i.group('all'),
                            'es1': i.group('all'),
                        }
                        #text to insert
                        regexp_sub = { 
                            'en1': ur"%s%s-%s-%02d%s" % (i.group('ini'), i.group('year'), month2number[i.group('month').strip().lower()], int(i.group('day')), i.group('end')),
                            'en2': ur"%s%s-%s-%02d%s" % (i.group('ini'), i.group('year'), month2number[i.group('month').strip().lower()], int(i.group('day')), i.group('end')),
                            'es1': ur"%s%s-%s-%02d%s" % (i.group('ini'), i.group('year'), month2number[i.group('month').strip().lower()], int(i.group('day')), i.group('end')),
                        }
                        
                        newtext = newtext.replace(regexp_rep[mode], regexp_sub[mode], 1) #only the first occurence
                        if wtext != newtext:
                            wikipedia.showDiff(wtext, newtext)
                            page.put(newtext, u"BOT - Changes to allow localization: %s → %s" % (regexp_rep[mode], regexp_sub[mode]))
                        
                        break #only one replacement and break
                else:
                    print '  Text in Commons page does not contain a data to be localised'
                break #only one mode, then skip to the following page
                    
if __name__ == "__main__":
    main()
