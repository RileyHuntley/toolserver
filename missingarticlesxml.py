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

#TODO ranking de categorías sacadas de artículos que no tienen ningún interwiki

def quitaracentos(t):
    t = t.replace(u'Á', 'A')
    t = t.replace(u'É', 'E')
    t = t.replace(u'Í', 'I')
    t = t.replace(u'Ó', 'O')
    t = t.replace(u'Ú', 'U')
    t = t.replace(u'á', 'a')
    t = t.replace(u'é', 'e')
    t = t.replace(u'í', 'i')
    t = t.replace(u'ó', 'o')
    t = t.replace(u'ú', 'u')
    return t

def linkstoiws(t, lang):
    t = re.sub(ur"\[\[([^\[\]\|]+)\|([^\[\]\|]+)\]\]", ur"[[:%s:\1|\2]]" % (lang), t)
    t = re.sub(ur"\[\[([^\[\]\|]+)\]\]", ur"[[:%s:\1|\1]]" % (lang), t)
    return t

def translatecat(cat, lang):
    catpage = wikipedia.Page(wikipedia.Site(lang, 'wikipedia'), "Category:%s" % (cat))
    if catpage.exists() and not catpage.isRedirectPage():
        cattext = catpage.get()
        m = re.compile(ur"(?im)\[\[\s*en\s*:\s*Category\s*:\s*(?P<catiw>[^\[\]]+?)\s*\]\]").finditer(cattext)
        for i in m:
            return i.group('catiw')
    return ''

months = {
    'es': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
    }

monthstoen = {
    'enero': 'January',
    'febrero': 'February',
    'marzo': 'March',
    'abril': 'April',
    'mayo': 'May',
    'junio': 'June',
    'julio': 'July',
    'agosto': 'August',
    'septiembre': 'September',
    'octubre': 'October',
    'noviembre': 'November',
    'diciembre': 'December',
    }

def main():
    """Missing articles"""
    
    lang = 'es'
    dumppath = ''
    dumpfilename = ''
    if len(sys.argv) >= 2:
        dumpfilename = sys.argv[1]
    
    xml = xmlreader.XmlDump('%s%s' % (dumppath and '%s/' % dumppath or '', dumpfilename), allrevisions=False)
    c = 0
    
    title_ex_r = re.compile(ur"(?im)[\:\(\)]") # : to exclude other namespaces, ( to disambiguation
    red_r = re.compile(ur"(?im)^\#\s*redirect")
    iws_r = re.compile(ur"(?im)\[\[\s*[a-z]{2,3}(\-[a-z]{2,5})?\s*:")
    dis_r = re.compile(ur"(?im)\{\{\s*(disambiguation|disambig|desambiguaci[oó]n|desambig|desamb)\s*[\|\}]")
    birth_r = re.compile(ur"(?im)\:\s*("
                         ur"Nacidos[_ ]en" #es
                         ur")")
    death_r = re.compile(ur"(?im)\:\s*("
                         ur"Fallecidos[_ ]en" #es
                         ur")")
    cats_r = re.compile(ur"(?im)\[\[\s*("
                        ur"Category|" #en
                        ur"Categoría" #es
                        ur")\s*:\s*(?P<catname>[^\]\|]+)\s*[\]\|]")
    dates_r = re.compile(ur"(?im)\(\s*[^\(\)\d]*?\s*\[?\[?(?P<birthday>\d+)\s+de\s+(?P<birthmonth>%s)\]?\]?\s+de\s+\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,5}\s*[^\(\)\d]*?\s*\[?\[?(?P<deathday>\d+)\s+de\s+(?P<deathmonth>%s)\]?\]?\s+de\s+\[?\[?(?P<deathyear>\d{4})\]?\]?\s*\)" % ('|'.join(months['es']), '|'.join(months['es'])))
    defaultsort_r = re.compile(ur"(?im)\{\{\s*(DEFAULTSORT|ORDENAR)\s*:\s*(?P<defaultsort>[^\{\}]+?)\s*\}\}")
    for x in xml.parse(): #parsing the whole dump
        if re.search(title_ex_r, x.title) or \
           re.search(red_r, x.text) or \
           re.search(dis_r, x.text) or \
           len(x.text.splitlines()) < 3 or len(x.text) < 1024*2:
            continue
        #nombre con dos palabras largas al menos
        trozos = x.title.split(' ')
        trozos2 = []
        for trozo in trozos: 
            if len(trozo) >= 3:
                trozos2.append(trozo)
        trozos = trozos2
        if not len(trozos) >= 2:
            continue
        #metemos variantes sin acentos
        for trozo in trozos2:
            if trozo != quitaracentos(trozo):
                trozos.append(quitaracentos(trozo))
        
        if not re.search(birth_r, x.text) or not re.search(death_r, x.text): #ha fallecido
            continue
        if re.search(iws_r, x.text): #no tiene iws
            continue
        c += 1
        images = re.findall(ur"(?im)[\s\/\:\|\=]+([^\/\:\|\=]+\.jpe?g)[\s\|]", x.text)
        image_cand = ''
        if images:
            for image in images:
                if len(re.findall(ur"(%s)" % ('|'.join(trozos)), image)) >= 2:
                    image_cand = image
                    break
        if not image_cand:
            continue
        
        #description
        desc = re.findall(ur"(?im)^(\'{3}\s*%s[^\n\r\<]+)[\n\r]"  % (x.title), x.text)
        if not desc:
            continue
        desc = desc[0]
        print desc
        
        #birth and death dates
        m = dates_r.finditer(desc)
        birthdate = ''
        deathdate = ''
        for dates in m:
            birthmonth = ''
            if monthstoen.has_key(dates.group('birthmonth').lower()):
                birthmonth = monthstoen[dates.group('birthmonth').lower()]
            deathmonth = ''
            if monthstoen.has_key(dates.group('deathmonth').lower()):
                deathmonth = monthstoen[dates.group('deathmonth').lower()]
            birthdate = u'%s %s, %s' % (birthmonth, dates.group('birthday'), dates.group('birthyear'))
            deathdate = u'%s %s, %s' % (deathmonth, dates.group('deathday'), dates.group('deathyear'))
            break
        
        #defaultsort
        m = defaultsort_r.finditer(x.text)
        defaultsort = ''
        for d in m:
            defaultsort = d.group("defaultsort")
            break
        
        if desc and len(desc) < 1000 and birthdate and deathdate:
            #cats, esto es lo más costoso en tiempo, entonces lo dejamos para este último if justo antes de generar el output
            m = cats_r.finditer(x.text)
            cats = []
            for cat in m:
                #print cat.group('catname')
                transcat = translatecat(cat.group('catname'), lang)
                if transcat:
                    cats.append(transcat)
            #print cats
            
            output  = u"""\n<br clear="all"/>\n==== [[%s]] ([[:%s:%s|%s]]) ====""" % (x.title, lang, x.title, lang)
            output += u"""\n[[File:%s|thumb|right|120px|%s]]""" % (image_cand, x.title)
            output += u"""\n<small>%s</small>""" % (linkstoiws(desc, lang).strip())
            output += u"""\n<pre>"""
            output += u"""\n{{Expand Spanish|%s}}""" % (x.title)
            output += u"""\n[[File:%s|thumb|right|%s]]""" % (image_cand, x.title)
            output += u"""\n\'\'\'%s\'\'\' (%s - %s) was a .""" % (x.title, birthdate, deathdate)
            output += u"""\n\n{{Persondata <!-- Metadata: see [[Wikipedia:Persondata]]. -->"""
            output += u"""\n| NAME              = %s """ % (defaultsort)
            output += u"""\n| ALTERNATIVE NAMES = """
            output += u"""\n| SHORT DESCRIPTION = """
            output += u"""\n| DATE OF BIRTH     = %s """ % (birthdate)
            output += u"""\n| PLACE OF BIRTH    = """
            output += u"""\n| DATE OF DEATH     = %s """ % (deathdate)
            output += u"""\n| PLACE OF DEATH    = """
            output += u"""\n}}"""
            output += u"""\n{{DEFAULTSORT:%s}}""" % (defaultsort)
            if cats:
                output += u"""\n"""
                for cat in cats:
                    output += u"""\n[[Category:%s]]""" % (cat)
            output += u"""\n\n[[%s:%s]]""" % (lang, x.title)
            output += u"""\n\n{{bio-stub}}"""
            output += u"""\n</pre>"""
            
            print '#'*70
            print x.title, 'https://%s.wikipedia.org/wiki/%s' % (lang, x.title.replace(' ', '_'))
            print output
            f = open('missingarticlesxml.output', 'a')
            f.write(output.encode('utf-8'))
            f.close()

if __name__ == "__main__":
    main()
