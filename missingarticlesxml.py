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

import family
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

nation = {
    'American': 'United States',
    'Argentine': 'Argentina',
    'Bolivian': 'Bolivia',
    'Brazilian': 'Brazil',
    'Chilean': 'Chile',
    'Cuban': 'Cuba',
    'Ecuadorian': 'Ecuador',
    'French': 'France',
    'Hungarian': 'Hungry',
    'Italian': 'Italy',
    'Mexican': 'Mexico',
    'Paraguayan': 'Paraguay',
    'Peruvian': 'Peru',
    'Spanish': 'Spain',
    'Uruguayan': 'Uruguay',
    'Venezuelan': 'Venezuela',
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
    dates_r = re.compile(ur"(?im)\(\s*[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)\s*de\s*(?P<birthmonth>%s)\]?\]?\s*de)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,5}\s*[^\(\)\d]*?\s*(\[?\[?(?P<deathday>\d+)\s*de\s*(?P<deathmonth>%s)\]?\]?\s*de)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?\s*\)" % ('|'.join(months['es']), '|'.join(months['es'])))
    defaultsort_r = re.compile(ur"(?im)\{\{\s*("
                               ur"DEFAULTSORT|" #en
                               ur"ORDENAR" #es
                               ur")\s*:\s*(?P<defaultsort>[^\{\}]+?)\s*\}\}")
    for x in xml.parse(): #parsing the whole dump
        if re.search(title_ex_r, x.title) or \
           re.search(red_r, x.text) or \
           re.search(dis_r, x.text) or \
           len(x.text.splitlines()) < 3 or len(x.text) < 1024*2:
            continue
        #nombre con dos palabras largas al menos
        trozos = [] # no hacer la asignacion del bucle for directamente, sino almacena True y False en vez de los trozos
        [len(trozo) >= 3 and trozos.append(trozo) for trozo in x.title.split(' ')]
        if not len(trozos) >= 2:
            continue
        #metemos variantes sin acentos
        [(trozo != quitaracentos(trozo) and trozo not in trozos) and trozos.append(quitaracentos(trozo)) for trozo in trozos]
        
        if not re.search(birth_r, x.text) or not re.search(death_r, x.text): #ha fallecido
            continue
        if re.search(iws_r, x.text): #no tiene iws
            continue
        c += 1
        images = re.findall(ur"(?im)[\s\/\:\|\=]+([^\/\:\|\=]+\.jpe?g)[\s\|]", x.text)
        image_cand = ''
        if images:
            continue #temp
            for image in images:
                if len(re.findall(ur"(%s)" % ('|'.join(trozos)), image)) >= 2:
                    image_cand = image
                    break
        #temp
        #if not image_cand:
        #    continue
        
        #description
        desc = re.findall(ur"(?im)^(\'{3}\s*%s[^\n\r\<]+)[\n\r]"  % (x.title), x.text)
        if not desc:
            continue
        desc = desc[0]
        #print desc
        
        #birth and death dates
        m = dates_r.finditer(desc)
        birthdate = ''
        deathdate = ''
        for dates in m:
            birthmonth = ''
            if dates.group('birthday') and dates.group('birthmonth'):
                if monthstoen.has_key(dates.group('birthmonth').lower()):
                    birthmonth = monthstoen[dates.group('birthmonth').lower()]
            deathmonth = ''
            if dates.group('deathday') and dates.group('deathmonth'):
                if monthstoen.has_key(dates.group('deathmonth').lower()):
                    deathmonth = monthstoen[dates.group('deathmonth').lower()]
            if birthmonth:
                #continue #temp
                birthdate = u'%s %s, %s' % (birthmonth, dates.group('birthday'), dates.group('birthyear'))
            else:
                birthdate = u'%s' % (dates.group('birthyear'))
            if deathmonth:
                #continue #temp
                deathdate = u'%s %s, %s' % (deathmonth, dates.group('deathday'), dates.group('deathyear'))
            else:
                deathdate = u'%s' % (dates.group('deathyear'))
            break
        
        #defaultsort
        m = defaultsort_r.finditer(x.text)
        defaultsort = ''
        for d in m:
            defaultsort = d.group("defaultsort")
            break
        if not defaultsort: #create myself
            defaultsort = u'%s, %s' % (' '.join(x.title.split(' ')[1:]), x.title.split(' ')[0])
        
        if desc and len(desc) < 1000 and birthdate and deathdate:
            #cats, esto es lo más costoso en tiempo, entonces lo dejamos para este último if justo antes de generar el output
            m = cats_r.finditer(x.text)
            cats = []
            [translatecat(cat.group('catname'), lang) and cats.append(translatecat(cat.group('catname'), lang)) for cat in m]
            
            #nationality
            nationality = ''
            if cats:
                n = [cat.split(' ')[0] for cat in cats]
                for nn in n:
                    if nn in nation.keys():
                        if nationality:
                            if nn != nationality: #conflict, several nationalities for this bio, blank nationality and exit
                                nationality = ''
                                break
                        else:
                            nationality = nn                        
            
            #occupations
            occupations = []
            if nationality:
                for cat in cats:
                    t = cat.split(' ')
                    if (t[0] == nationality or t[0].split('-')[0] == nationality) and len(t) == 2: # [[Category:Spanish writers]] [[Category:Spanish-language writers]]
                        if t[1][-1] == 's':
                            occupations.append(t[1].rstrip('s')) #remove final s
                        elif t[1] == 'businesspeople':
                            occupations.append('businessman')
                
            #la salida para esta bio
            output  = u"""\n<br clear="all"/>\n==== [[%s]] ([[:%s:%s|%s]]) ====""" % (x.title, lang, x.title, lang)
            #temp output += u"""\n[[File:%s|thumb|right|120px|%s]]""" % (image_cand, x.title)
            output += u"""\n<small>%s</small>""" % (linkstoiws(desc, lang).strip())
            output += u"""\n<pre>"""
            output += u"""\n{{Expand Spanish|%s}}""" % (x.title)
            #temp output += u"""\n[[File:%s|thumb|right|%s]]""" % (image_cand, x.title)
            output += u"""\n\'\'\'%s\'\'\' (%s - %s) was %s %s %s.""" % (x.title, birthdate, deathdate, nationality and nation[nationality][0] in ['A', 'E', 'I', 'O', 'U'] and 'an' or 'a', nationality and '[[%s|%s]]' % (nation[nationality], nationality), occupations and (len(occupations) > 1 and '%s and %s' % (', '.join(occupations[:-1]), occupations[-1:][0]) or occupations[0]) or '...')
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
