#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 emijrp
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

""" Update a Britannica progress template """

from __future__ import generators
import re

import wikipedia
import pagegenerators
 
def main():
    """ Update a Britannica progress template """
    
    wikien = wikipedia.Site("en", "wikipedia")
    wikies = wikipedia.Site("es", "wikipedia")
    pagetitles = []
    suffixes = ['A', 'A2', 'A3', 'A4', 'A5', 'B', 'B2', 'B3', 'C', 'C2', 
              'C3', 'C4', 'D', 'D2', 'E', 'E2', 'F', 'F2', 'F3', 'G', 'G2', 
              'G3', 'H', 'H2', 'H3', 'I', 'J', 'J2', 'J3', 'J4', 'J5', 'K', 
              'K2', 'L', 'L2', 'M', 'M2', 'M3', 'N', 'O', 'P', 'P2', 'P3', 
              'Q', 'R', 'R2', 'S', 'S2', 'S3', 'T', 'T2','U', 'V', 'W', 
              'W2', 'X-Z']
    for i in suffixes:
        pagetitles.append(u"Wikipedia:WikiProject Missing encyclopedic articles/1911 verification/%s" % i)
     
    pages = [wikipedia.Page(wikien, pagetitle) for pagetitle in pagetitles]
    gen = iter(pages)
    preloadingGen = pagegenerators.PreloadingGenerator(gen, pageNumber = 5)
     
    contt1 = 0
    contt2 = 0
    progress = u"{{subst:Progreso1911/subst"
    for page in preloadingGen:
        wtitle = page.title()
        wtext = page.get()
        
        m = re.compile(ur"(?im)^\# *(\[\[ *(Image|File) *\:[^\]]+?\]\])?[^\[]*?\[\[(?P<page>[^|\]]+?)[\|\]]").finditer(wtext)
        
        articleslist = []
        for i in m:
            articleslist.append(i.group("page"))
        
        pp = [wikipedia.Page(wikien, pagetitle) for pagetitle in articleslist]
        g = iter(pp)
        preloadingGen2 = pagegenerators.PreloadingGenerator(g, pageNumber = 250)
        
        output = u"{{Wikiproyecto:Enciclopedia Británica 1911/Header}}\n\n"
        cont1 = 0
        cont2 = 0
        articleslist = []
        # Changing redirects to their target articles
        for page2 in preloadingGen2:
            if page2.exists():
                if page2.isRedirectPage():
                    articleslist.append(page2.getRedirectTarget().title())
                else:
                    articleslist.append(page2.title())
        
        pp = [wikipedia.Page(wikien, pagetitle) for pagetitle in articleslist]
        g = iter(pp)
        preloadingGen2 = pagegenerators.PreloadingGenerator(g, pageNumber = 250)
        for page2 in preloadingGen2:
            if page2.exists() and not page2.isRedirectPage() and not page2.isDisambig():
                wtitle2 = page2.title()
                wtext2 = page2.get()
                iws2 = page2.interwiki()
                es = u""
                tt = u""
                for iw in iws2:
                    if not es and iw.site().lang=='es':
                        es = iw.title()
                
                iwstext = u""
                for iw in iws2:
                    if iw.site().lang in ['de', 'fr', 'pt', 'it']:
                        iwstext += u" - [[:%s:%s|%s]]" % (iw.site().lang, iw.title(), iw.site().lang)
                
                if re.search(ur"(?i)\{\{ *(template\:)? *taxobox", wtext2):
                    tt += "T"
                
                if es:
                    cont1 += 1
                    output += u"\n# [[%s]] - [[:en:%s|en]]%s" % (es, wtitle2, iwstext)
                    if tt:
                        output += u" (%s)" % (tt)
                else:
                    cont2 += 1
                    output += u"\n# [[%s]] - [[:en:%s|en]]%s" % (wtitle2, wtitle2, iwstext)
                    if tt:
                        output += u" (%s)" % (tt)
        
        contt1 += cont1
        contt2 += cont2
        
        percent = cont1 * 1.0 / (cont1 + cont2) * 100
        progress += u"|%.2f" % percent
            
        wiii = wikipedia.Page(wikies, u"Wikiproyecto:Enciclopedia Británica 1911/%s" % (wtitle.split("/")[2]))
        wiii.put(output, u"BOT - Generando lista")
     
    percent = contt1 * 1.0/ (contt1 + contt2) * 100
    progress += u"|%.2f" % percent
    progress += u"}}<noinclude>{{documentación}}</noinclude>"
    wiii = wikipedia.Page(wikies, u"Plantilla:Progreso1911")
    wiii.put(progress, u"BOT - Actualizando plantilla")

if __name__ == "__main__":
    main()
