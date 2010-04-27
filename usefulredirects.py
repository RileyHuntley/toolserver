# -*- coding: utf-8  -*-

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

import wikipedia, pagegenerators
import re, sys, os
import tareas

def percent(c):
    if c % 10000 == 0:
        wikipedia.output(u'Llevamos %d' % c)

langorig='en'
st='A'
langdest='es'
if len(sys.argv)>=2:
    langdest=sys.argv[1]
if len(sys.argv)>=3:
    st=sys.argv[1]

redirects=tareas.getRedirectsAndTargets(langorig, targetStartsWith=st)
localpages=tareas.getPageTitle(langdest, redirects=True)

wikipediadestino=wikipedia.Site(langdest, 'wikipedia')
gen=pagegenerators.AllpagesPageGenerator(start=st, namespace=0, includeredirects=False, site=wikipediadestino)
preloadingGen=pagegenerators.PreloadingGenerator(gen, pageNumber=100, lookahead=100)
 
for page in preloadingGen:
    if page.exists() and page.isRedirectPage() or page.isDisambig():
        pass
    else:
        wtitle=page.title()
        
        if wtitle[0]!=st[0]:
            st=wtitle[0]
            redirects=tareas.getRedirectsAndTargets(langorig, targetStartsWith=st[0])
        
        iws=page.interwiki()
        for iw in iws:
            if iw.site().lang==langorig:
                wtext=page.get()
                m=re.compile(ur'\'{3,}(?P<bold>[^\']{3,})\'{3,}').finditer(wtext)
                bolds=[]
                for i in m:
                    if bolds.count(i.group('bold'))==0:
                        bolds.append(i.group('bold'))
                
                for bold in bolds:
                    if bold!=wtitle and redirects.has_key(bold) and redirects[bold]==iw.title() and not localpages.has_key(bold):
                        wikipedia.output(u'%s: #REDIRECT [[%s]]' % (bold, wtitle))
                        #comprobar si existe antes de crear redireccion
                        red=wikipedia.Page(wikipediadestino, bold)
                        if not red.exists():
                            red.put(u'#REDIRECT [[%s]]' % wtitle, u'BOT - #REDIRECT [[%s]]' % wtitle)
                break
        
        
