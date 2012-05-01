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
import unicodedata

import family
import wikipedia
import xmlreader

#TODO ranking de categorías sacadas de artículos que no tienen ningún interwiki

targetlang = 'en' #no cambiar a menos que quiera crear bios para otras wikipedias distintas a la inglesa
lang = 'es'
minimumiws = 2 #minimum interwikis to create this stub (avoiding non-notable bios)
dumppath = ''
dumpfilename = ''
skip = '' #page to skip to
if len(sys.argv) >= 2:
    dumpfilename = sys.argv[1]
    lang = dumpfilename.split('wiki')[0]
if len(sys.argv) >= 3:
    skip = re.sub('_', ' ', unicode(sys.argv[2], 'utf-8'))

cattranslations = {}

langisotolang = {
    'de': 'German',
    'es': 'Spanish',
    'fr': 'French',
    'it': 'Italian',
    'nl': 'Dutch',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'sv': 'Swedish',
    'vi': 'Vietnamese',
}

months = {
    'de': ['januar', 'februar', u'm[äa]rz', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'dezember'],
    'es': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
    'fr': ['janvier', u'f[ée]vrier', 'mars', 'avril', 'may', 'juin', 'juillet', u'ao[ûu]t', 'septembre', 'octobre', 'novembre', u'décembre'],
    'it': ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'],
    'nl': ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december'],
    'pl': ['stycznia', u'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', u'sierpnia', u'wrze[śs]nia', u'pa[źz]dziernika', 'listopada', u'grudnia'],
    'pt': ['janeiro', 'fevereiro', u'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'],
    'sv': ['januari', 'februari', 'mars', 'april', 'maj', 'juni', 'juli', 'augusti', 'september', 'oktober', 'november', 'december'],
    'vi': [u'tháng 1', u'tháng 2', u'tháng 3', u'tháng 4', u'tháng 5', u'tháng 6', u'tháng 7', u'tháng 8', u'tháng 9', u'tháng 10', u'tháng 11', u'tháng 12'],
    }

monthstoen = {
    #de
    'januar': 'January',
    'februar': 'February',
    u'märz': 'March',
    'marz': 'March',
    'april': 'April',
    'mai': 'May',
    'juni': 'June',
    'juli': 'July',
    'august': 'August',
    'september': 'September',
    'oktober': 'October',
    'november': 'November',
    'dezember': 'December',
    
    #es
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
    
    #fr
    'janvier': 'January',
    u'février': 'February',
    'fevrier': 'February',
    'mars': 'March',
    'avril': 'April',
    'may': 'May',
    'juin': 'June',
    'juillet': 'July',
    u'août': 'August',
    'aout': 'August',
    'septembre': 'September',
    'octobre': 'October',
    'novembre': 'November',
    u'décembre': 'December',
    
    #it
    'gennaio': 'January',
    'febbraio': 'February',
    'marzo': 'March',
    'aprile': 'April',
    'maggio': 'May',
    'giugno': 'June',
    'luglio': 'July',
    'agosto': 'August',
    'settembre': 'September',
    'ottobre': 'October',
    'novembre': 'November',
    'dicembre': 'December',
    
    #nl
    'januari': 'January',
    'februari': 'February',
    'maart': 'March',
    'april': 'April',
    'mei': 'May',
    'juni': 'June',
    'juli': 'July',
    'augustus': 'August',
    'september': 'September',
    'oktober': 'October',
    'november': 'November',
    'december': 'December',
    
    #pl
    'stycznia': 'January',
    'lutego': 'February',
    'marca': 'March',
    'kwietnia': 'April',
    'maja': 'May',
    'czerwca': 'June',
    'lipca': 'July',
    'sierpnia': 'August',
    u'września': 'September',
    'wrzesnia': 'September',
    u'października': 'October',
    'pazdziernika': 'October',
    'listopada': 'November',
    'grudnia': 'December',
    
    #pt
    'janeiro': 'January',
    'fevereiro': 'February',
    u'março': 'March',
    'abril': 'April',
    'maio': 'May',
    'junho': 'June',
    'julho': 'July',
    'agosto': 'August',
    'setembro': 'September',
    'outubro': 'October',
    'novembro': 'November',
    'dezembro': 'December',
    
    #sv
    'januari': 'January',
    'februari': 'February',
    'mars': 'March',
    'april': 'April',
    'maj': 'May',
    'juni': 'June',
    'juli': 'July',
    'augusti': 'August',
    'september': 'September',
    'oktober': 'October',
    'november': 'November',
    'december': 'December',
    
    #vi
    u'tháng 1': 'January',
    u'tháng 2': 'February',
    u'tháng 3': 'March',
    u'tháng 4': 'April',
    u'tháng 5': 'May',
    u'tháng 6': 'June',
    u'tháng 7': 'July',
    u'tháng 8': 'August',
    u'tháng 9': 'September',
    u'tháng 10': 'October',
    u'tháng 11': 'November',
    u'tháng 12': 'December',
    }

nationalitytonation = {
    'Albanian': 'Albania',
    'Algerian': 'Algeria',
    'American': 'United States',
    'Argentine': 'Argentina',
    'Austrian': 'Austria',
    'Belgian': 'Belgium',
    'Bolivian': 'Bolivia',
    'Brazilian': 'Brazil',
    'Bulgarian': 'Bulgaria',
    'Canadian': 'Canada',
    'Chilean': 'Chile',
    'Chinese': 'China',
    'Colombian': 'Colombia',
    'Cuban': 'Cuba',
    'Czech': 'Czech Republic',
    'Danish': 'Denmark',
    'Dutch': 'Netherlands',
    'Ecuadorian': 'Ecuador',
    'Egyptian': 'Egypt',
    'Estonian': 'Estonia',
    'Finnish': 'Finland',
    'French': 'France',
    'German': 'Germany',
    'Greek': 'Greece',
    'Guatemalan': 'Guatemala',
    'Honduran': 'Honduras',
    'Hungarian': 'Hungary',
    'Icelandic': 'Iceland',
    'Israeli': 'Israel',
    'Italian': 'Italy',
    'Japanese': 'Japan',
    'Lebanese': 'Lebanon',
    'Lithuanian': 'Lithuania',
    'Luxembourgian': 'Luxembourg',
    'Madeiran': 'Madeira',
    'Malian': 'Mali',
    'Mexican': 'Mexico',
    'Nicaraguan': 'Nicaragua',
    'Norwegian': 'Norway',
    'Panamanian': 'Panama',
    'Paraguayan': 'Paraguay',
    'Peruvian': 'Peru',
    'Polish': 'Poland',
    'Portuguese': 'Portugal',
    'Russian': 'Russia',
    'Spanish': 'Spain',
    'Swedish': 'Sweden',
    'Swiss': 'Switzerland',
    'Tanzanian': 'Tanzania',
    'Turkish': 'Turkey',
    'Ukrainian': 'Ukraine',
    'Uruguayan': 'Uruguay',
    'Venezuelan': 'Venezuela',
    'Vietnamese': 'Vietnam',
}

title_ex_r = re.compile(ur"(?im)[\:\(\)\,]") # : to exclude other namespaces, ( to disambiguation
red_r = re.compile(ur"(?im)^\#\s*redirec")
iws_r = re.compile(ur"(?im)\[\[\s*(?P<iwlang>[a-z]{2,3}(\-[a-z]{2,5})?)\s*:\s*(?P<iwtitle>[^\]\|]+)\s*\]\]")
iws_target_r = re.compile(ur"(?im)\[\[\s*%s\s*:\s*[^\]\|]+\s*\]\]" % (targetlang))
dis_r = re.compile(ur"(?im)\{\{\s*(disambiguation|disambig|desambiguaci[oó]n|desambig|desamb|homonymie|dp|disambigua|desambiguação|desambig-ini|förgrening|betydelselista|gaffel|gren|grensida|förgreningssida|flertydig|ortnamn|trang[ _]định[ _]hướng|Định[ _]hướng|TLAdisambig|hndis|dab|dis)\s*[\|\}]") #pl: DisambigR, nl: D[Pp], 
birth_r = re.compile(ur"(?im)\:\s*("
                     ur"Geboren[_ ]|" #de
                     ur"Nacidos[_ ]en|" #es
                     ur"Naissance[_ ]en|" #fr
                     ur"Nati[_ ]nel|" #it
                     ur"Urodzeni[_ ]w|" #pl
                     ur"Nascidos[_ ]em|" #pt
                     ur"Födda" #sv
                     ur")[_ ](?P<birthyear>\d{4})") #nl, vi no tienen o es indirecta con plantillas
death_r = re.compile(ur"(?im)\:\s*("
                     ur"Gestorben[_ ]|" #de
                     ur"Fallecidos[_ ]en|" #es
                     ur"Décès[_ ]en|" #fr
                     ur"Morti[_ ]nel|" #it
                     ur"Zmarli[_ ]w|" #pl
                     ur"Mortos[_ ]em|" #pt
                     ur"Avlidna" #sv
                     ur")[_ ](?P<deathyear>\d{4})") #nl, vi no tienen o es indirecta con plantillas
bdtemplate_r = {
    'es': re.compile(ur"(?im)\{\{\s*(BD|NF)\s*\|\s*(?P<birthyear>\d{4})\s*\|\s*(?P<deathyear>\d{4})\s*(\s*\|\s*(?P<defaultsort>[^\}]{4,},[^\}]{4,})\s*)?\s*\}\}"),
    'pt': re.compile(ur"(?im)\{\{\s*(falecimento|morte|Falecimento[ _]e[ _]idade|Morte[ _]e[ _]idade|Data[ _]da[ _]morte[ _]e[ _]idade|Data[ _]de[ _]falecimento|dmi|Data[ _]de[ _]morte|Data[ _]morte)\s*\|\s*\d*\s*\|\s*\d*\s*\|\s*(?P<birthyear>\d{4})\s*\|\s*\d*\s*\|\s*\d*\s*\|\s*(?P<deathyear>\d{4})\s*[\|\}](?P<defaultsort>)"), #defaultsort is NULL here, because this template doesn't include it
    'vi': re.compile(ur"(?im)\{\{\s*(Lifetime|Ngày[ _]tháng[ _]sống|Ngày[ _]tháng[ _]đang[ _]sống|Thời[ _]gian[ _]sống|Thời[ _]sống)\s*\|\s*(sinh\s*=\s*)?(?P<birthyear>\d{4})\s*\|\s*(mất\s*=\s*)?(?P<deathyear>\d{4})\s*(\s*\|\s*(tên\s*=\s*)?(?P<defaultsort>[^\}]{4,},[^\}]{4,})\s*)?\s*\}\}"),
}

catsnm = { #lo uso en translatecat() también
    'de': 'Kategorie',
    'en': 'Category',
    'es': u'Categoría',
    'fr': u'Catégorie',
    'it': 'Categoria',
    'nl': 'Categorie',
    'pl': 'Kategoria',
    'pt': 'Categoria',
    'sv': 'Kategori',
    'vi': u'Thể loại',
    }
cats_r = re.compile(ur"(?im)\[\[\s*(%s)\s*:\s*(?P<catname>[^\]\|]+)\s*[\]\|]" % ('|'.join(catsnm.values())))
dates_r = { #fix, most intros are not well parsed, birthday de birthmonth
    'de': re.compile(ur"^.*?\[\[(?P<birthyear>\d{4})\]\].*?\[\[(?P<deathyear>\d{4})\]\]"),
    'es': re.compile(ur"^.*?\[\[(?P<birthyear>\d{4})\]\].*?\[\[(?P<deathyear>\d{4})\]\]"),
    'fr': re.compile(ur"^.*?\[\[(?P<birthyear>\d{4})\]\].*?\[\[(?P<deathyear>\d{4})\]\]"),
    'it': re.compile(ur"^.*?\[\[(?P<birthyear>\d{4})\]\].*?\[\[(?P<deathyear>\d{4})\]\]"),
    'nl': re.compile(ur"^.*?\[\[(?P<birthyear>\d{4})\]\].*?\[\[(?P<deathyear>\d{4})\]\]"),
    'pl': re.compile(ur"^.*?\[\[(?P<birthyear>\d{4})\]\].*?\[\[(?P<deathyear>\d{4})\]\]"),
    'pt': re.compile(ur"^.*?\[\[(?P<birthyear>\d{4})\]\].*?\[\[(?P<deathyear>\d{4})\]\]"),
    'sv': re.compile(ur"^.*?\[\[(?P<birthyear>\d{4})\]\].*?\[\[(?P<deathyear>\d{4})\]\]"),
    'vi': re.compile(ur"^.*?\[\[(?P<birthyear>\d{4})\]\].*?\[\[(?P<deathyear>\d{4})\]\]"),
}
"""
'de': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
'es': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)\s*de\s*(?P<birthmonth>%s)\]?\]?\s*de)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*[^\(\)\d]*?\s*(\[?\[?(?P<deathday>\d+)\s*de\s*(?P<deathmonth>%s)\]?\]?\s*de)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
'fr': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
'it': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
'nl': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
'pl': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
'pt': re.compile(ur"(?im)(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
'sv': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
'vi': re.compile(ur"(?im)[^\(\)\d]*?\s*(\[?\[?(?P<birthday>\d+)[\s\|]*(?P<birthmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<birthyear>\d{4})\]?\]?\s*[^\n\r\d\)\[]{,15}\s*(\[?\[?(?P<deathday>\d+)[\s\|]*(?P<deathmonth>%s)\]?\]?[\s\|]*)?\s*\[?\[?(?P<deathyear>\d{4})\]?\]?" % ('|'.join(months[lang]), '|'.join(months[lang]))),
"""
defaultsort_r = re.compile(ur"(?im)\{\{\s*("
                           ur"SORTIERUNG|" #de
                           ur"DEFAULTSORT|" #en, fr, pl, nl, pt, vi
                           ur"ORDENAR|" #es
                           ur"STANDARDSORTERING" #sv
                           ur")\s*:\s*(?P<defaultsort>[^\{\}]+?)\s*\}\}")

def quitaracentos(s):
    #http://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
    return ''.join((c for c in unicodedata.normalize('NFD', u'%s' % s) if unicodedata.category(c) != 'Mn'))
    """
    t = re.sub(ur'[ÁÀÄ]', ur'A', t)
    t = re.sub(ur'[ÉÈË]', ur'E', t)
    t = re.sub(ur'[ÍÌÏ]', ur'I', t)
    t = re.sub(ur'[ÓÒÖ]', ur'O', t)
    t = re.sub(ur'[ÚÙÜ]', ur'U', t)
    t = re.sub(ur'[áàä]', ur'a', t)
    t = re.sub(ur'[éèë]', ur'e', t)
    t = re.sub(ur'[íìï]', ur'i', t)
    t = re.sub(ur'[óòö]', ur'o', t)
    t = re.sub(ur'[úùü]', ur'u', t)
    return t"""

def linkstoiws(t, lang):
    t = re.sub(ur"\[\[([^\[\]\|]+)\|([^\[\]\|]+)\]\]", ur"[[:%s:\1|\2]]" % (lang), t)
    t = re.sub(ur"\[\[([^\[\]\|]+)\]\]", ur"[[:%s:\1|\1]]" % (lang), t)
    return t

def translatecat(cat, lang):
    global cattranslations
    
    if cattranslations.has_key(cat):
        return cattranslations[cat]
    else:
        catpage = wikipedia.Page(wikipedia.Site(lang, 'wikipedia'), "Category:%s" % (cat))
        if catpage.exists() and not catpage.isRedirectPage():
            cattext = catpage.get()
            m = re.compile(ur"(?im)\[\[\s*%s\s*:\s*(%s)\s*:\s*(?P<catiw>[^\[\]]+?)\s*\]\]" % (targetlang, '|'.join(catsnm.values()))).finditer(cattext)
            for i in m:
                cattranslations[cat] = i.group('catiw')
                return i.group('catiw')
    return ''

def main():
    """Missing articles"""
    xml = xmlreader.XmlDump('%s%s' % (dumppath and '%s/' % dumppath or '', dumpfilename), allrevisions=False)
    c = 0
    bios = 0
    global skip
    for x in xml.parse(): #parsing the whole dump, one page a time
        c+=1
        if c % 10000 == 0:
            print c
        if skip:
            if x.title == skip:
                skip = ''
            continue
        
        #filtering unuseful pages
        if re.search(title_ex_r, x.title) or \
           re.search(red_r, x.text) or \
           re.search(dis_r, x.text) or \
           len(x.text.splitlines()) < 3 or len(x.text) < 1024*2:
            continue
        
        #si tiene iws hacia targetlang, no nos interesa, ya existe la bio
        if re.search(iws_target_r, x.text):
            continue
        
        #nombre con dos palabras largas al menos
        trozos = [] # no hacer la asignacion del bucle for directamente, sino almacena True y False en vez de los trozos
        [len(trozo) >= 3 and trozos.append(trozo) for trozo in x.title.split(' ')]
        if not len(trozos) >= 2:
            continue
        #metemos variantes sin acentos
        [(trozo != quitaracentos(trozo) and trozo not in trozos) and trozos.append(quitaracentos(trozo)) for trozo in trozos]
        
        #descartamos algunas bios
        if not re.search(birth_r, x.text) or not re.search(death_r, x.text): #si es BLP, fuera
            continue
        #sino podemos sacar su año de nacimiento ni fallecimiento, fuera
        if not re.search(birth_r, x.text) and not re.search(death_r, x.text) and bdtemplate_r.has_key(lang) and not re.search(bdtemplate_r[lang], x.text):
            continue
        
        print 'Analysing http://%s.wikipedia.org/wiki/%s' % (lang, re.sub(' ', '_', x.title))
        
        #buscando imágenes útiles para la bio
        images = re.findall(ur"(?im)[\s\/\:\|\=]+([^\/\:\|\=]+\.jpe?g)[\s\|]", x.text)
        image_cand = ''
        if images:
            for image in images:
                if len(re.findall(ur"(%s)" % ('|'.join(trozos)), image)) >= 1:
                    image_cand = image
                    break
        if image_cand:
            print 'We have image_cand'
        else:
            print 'No image_cand'
            #continue
        
        #description
        desc = re.findall(ur"(?im)^(\'{2,5}\s*.{,25}\s*%s[^\n\r]+)[\n\r]"  % (x.title.split(' ')[0]), x.text)
        if not desc:
            print 'No description'
            continue
        else:
            print 'We have description'
            desc = desc[0]
        
        #birth and death dates
        birthdate = ''
        deathdate = ''
        #first try with birth/death categories
        m = birth_r.finditer(x.text)
        for i in m:
            birthdate = i.group('birthyear')
            break
        m = death_r.finditer(x.text)
        for i in m:
            deathdate = i.group('deathyear')
            break
        
        #second attempt uses bio first paragraph
        if not birthdate and not deathdate:
            m = dates_r[lang].finditer(desc)
            for i in m:
                """birthmonth = ''
                if i.group('birthday') and i.group('birthmonth'):
                    if monthstoen.has_key(quitaracentos(i.group('birthmonth').lower())):
                        birthmonth = monthstoen[i.group('birthmonth').lower()]
                deathmonth = ''
                if i.group('deathday') and i.group('deathmonth'):
                    if monthstoen.has_key(quitaracentos(i.group('deathmonth').lower())):
                        deathmonth = monthstoen[i.group('deathmonth').lower()]
                if birthmonth:
                    #continue #temp
                    birthdate = u'%s %s, %s' % (birthmonth, i.group('birthday'), i.group('birthyear'))
                else:
                    birthdate = u'%s' % (i.group('birthyear'))
                if deathmonth:
                    #continue #temp
                    deathdate = u'%s %s, %s' % (deathmonth, i.group('deathday'), i.group('deathyear'))
                else:
                    deathdate = u'%s' % (i.group('deathyear'))"""
                birthdate = i.group('birthyear')
                deathdate = i.group('deathyear')
                break
        
        #third case uses special templates
        #special cases for es: {{BD|XXXX|YYYY|DEFAULTSORT}}, or vi:, or others
        if not birthdate and not deathdate and bdtemplate_r.has_key(lang):
            m = bdtemplate_r[lang].finditer(x.text)
            for i in m:
                birthdate = u'%s' % (i.group('birthyear'))
                deathdate = u'%s' % (i.group('deathyear'))
                break
        
        if birthdate and deathdate:
            print 'We have birthdate and deathdate'
            if (int(deathdate[-4:]) - int(birthdate[-4:])) < 20: #weird, child prodigy?
                print 'But dates are weird'
                continue #skiping bio
        else:
            print 'No birthdate or deathdate'
        #end birth and death dates
        
        #defaultsort
        m = defaultsort_r.finditer(x.text)
        defaultsort = ''
        for d in m:
            defaultsort = d.group("defaultsort")
            break
        if not defaultsort and bdtemplate_r.has_key(lang):
            m = bdtemplate_r[lang].finditer(x.text)
            for i in m:
                defaultsort = u'%s' % (i.group('defaultsort'))
                break
        if not defaultsort: #create myself
            defaultsort = u'%s, %s' % (' '.join(quitaracentos(x.title).split(' ')[1:]), quitaracentos(x.title).split(' ')[0])
        
        #iws
        m = iws_r.finditer(x.text)
        iws = []
        for iw in m:
            if not iw.group('iwlang') in [targetlang, lang]:
                iws.append([iw.group('iwlang'), iw.group('iwtitle')])
        iws.append([lang, x.title])
        if len(iws) < minimumiws:
            print 'No minimum interwikis'
            continue # this language and other wiki at least
        print 'We have %d interwikis' % len(iws)
        iws.sort()
        iws_plain = ''
        for iwlang, iwtitle in iws:
            iws_plain += u'[[%s:%s]]\n' % (iwlang, iwtitle)
        
        if desc and len(desc) < 2500 and birthdate and deathdate:
            #check if live version has interwiki or not
            sourcebio = wikipedia.Page(wikipedia.Site(lang, 'wikipedia'), x.title)
            if not sourcebio.exists() or sourcebio.isRedirectPage() or sourcebio.isDisambig() or len(re.findall(iws_target_r, sourcebio.get())) != 0:
                continue
            #cats, esto es lo más costoso en tiempo, entonces lo dejamos para este último if justo antes de generar el output
            m = cats_r.finditer(x.text)
            cats = []
            [translatecat(cat.group('catname'), lang) and translatecat(cat.group('catname'), lang) not in cats and cats.append(translatecat(cat.group('catname'), lang)) for cat in m]
            cats.sort()
            
            #nationality
            nationality = ''
            if cats:
                n = [cat.split(' ')[0] for cat in cats]
                for nn in n:
                    if nn in nationalitytonation.keys():
                        if nationality:
                            if nn != nationality: #conflict, several nationalities for this bio, blank nationality and exit
                                nationality = ''
                                break
                        else:
                            nationality = nn         
                    else:
                        f = open('missingarticlesxml.output.errors', 'a')
                        f.write((u'missing nationality = %s\n' % (nn)).encode('utf-8'))
                        f.close()
            
            #occupations (usando cats)
            occupations = []
            if nationality:
                for cat in cats:
                    t = cat.split(' ')
                    if (t[0] == nationality or t[0].split('-')[0] == nationality) and len(t) == 2: # [[Category:Spanish writers]] [[Category:Spanish-language writers]]
                        if t[1][-3:] == 'ies':
                            if not '%sy' % t[1].rstrip('ies') in occupations:
                                occupations.append('%sy' % t[1].rstrip('ies')) #remove final ies and add y
                        elif t[1][-1] == 's':
                            if not t[1].rstrip('s') in occupations:
                                occupations.append(t[1].rstrip('s')) #remove final s
                        elif t[1] == 'businesspeople':
                            if not 'businessman' in occupations:
                                occupations.append('businessman')
            
            if not occupations or not nationality:
                continue
            
            #la salida para esta bio
            output  = u"""\n<br clear="all"/>\n==== [[%s]] ([[:%s:%s|%s]]) ====""" % (x.title, lang, x.title, lang)
            if image_cand:
                output += u"""\n[[File:%s|thumb|right|120px|%s]]""" % (image_cand, x.title)
            output += u"""\n<small><nowiki>%s</nowiki></small>""" % (linkstoiws(desc, lang).strip())
            output += u"""\n<pre>"""
            output += u"""\n{{Expand %s|%s}}""" % (langisotolang[lang], x.title)
            if image_cand:
                output += u"""\n[[File:%s|thumb|right|%s]]""" % (image_cand, x.title)
            output += u"""\n\'\'\'%s\'\'\' (%s - %s) was %s %s %s.""" % (x.title, birthdate, deathdate, nationality and nationalitytonation[nationality][0] in ['A', 'E', 'I', 'O', 'U'] and 'an' or 'a', nationality and '[[%s|%s]]' % (nationalitytonation[nationality], nationality), occupations and (len(occupations) > 1 and '%s and %s' % (', '.join(occupations[:-1]), occupations[-1:][0]) or occupations[0]) or '...')
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
                    if not cat in ['Men', 'Women', 'Fascists']:
                        output += u"""\n[[Category:%s]]""" % (cat)
            output += u"""\n\n%s""" % (iws_plain)
            output += u"""\n%s""" % (nationality and nationalitytonation[nationality] and '{{%s-bio-stub}}' % (nationalitytonation[nationality]) or '{{bio-stub}}')
            output += u"""\n</pre>"""
            
            #last replacements...
            output = re.sub(ur"{{United States-bio-stub}}", ur"{{US-bio-stub}}", output)
            output = re.sub(ur"{{Czech Republic-bio-stub}}", ur"{{Czech-bio-stub}}", output)
            #end last
            
            print '#'*70
            print x.title, 'https://%s.wikipedia.org/wiki/%s' % (lang, x.title.replace(' ', '_'))
            print output
            bios += 1
            print 'Total pages analysed =', c, '| Bios =', bios
            f = open('missingarticlesxml.output.%s' % (lang), 'a')
            f.write(output.encode('utf-8'))
            f.close()

if __name__ == "__main__":
    main()
