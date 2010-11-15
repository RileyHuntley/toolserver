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

import wikipedia, time

import tarea000

#w, wikt, b, q, s, n, v

botijoinfo = wikipedia.Page(wikipedia.Site("en", "wikipedia"), u"User:Emijrp/BOTijoInfo.css").get()

for family in ['wikipedia', 'wiktionary']: #añadir al user-config.py los credenciales
    langswiki = []
    
    for lang in tarea000.getLangsByFamily(family):
        if lang=='en-simple':
            langswiki.append('simple')
        else:
            langswiki.append(lang)
    
    for lang in langswiki:
        time.sleep(0.1)
        print lang, family
        try:
            site=wikipedia.Site(lang, family)
            #emijrp
            tem=u"[[File:Redirectltr.png|#REDIRECT ]]<span class=\"redirectText\" id=\"softredirect\">[[{{{1}}}]]</span><br /><span style=\"font-size:85%; padding-left:52px;\">This page is a [[:w:Wikipedia:Soft redirect|soft redirect]].</span>"
            tempage=wikipedia.Page(site, u'Template:Softredirect')
            if not tempage.exists():
                tempage.put(tem, u"From [[:w:en:Template:Softredirect]]")
            
            msg=u"{{Softredirect|w:en:User:Emijrp}}"
            msgold=u"{{Babel|es|en-2|fr-1}}\nHi. You can see my userpage in [[:en:User:Emijrp]]. Comments to [[:en:User talk:Emijrp]]. Thanks."
            userpage=wikipedia.Page(site, u'User:Emijrp')
            talkpage=wikipedia.Page(site, u'User talk:Emijrp')
            if not userpage.exists() or (userpage.exists() and len(userpage.get())<=len(msg) and userpage.get()!=msg):
                userpage.put(msg, msg)
                print 'Creating or Updating'
            else:
                print 'Not necesary'
            if not talkpage.exists() or (talkpage.exists() and len(talkpage.get())<=len(msg) and talkpage.get()!=msg):
                talkpage.put(msg, msg)
                print 'Creating or Updating'
            else:
                print 'Not necesary'
            
            #botijo
            if family=="wikipedia":
                userpage=wikipedia.Page(site, u'User:BOTijo')
                talkpage=wikipedia.Page(site, u'User talk:BOTijo')
                infopage=wikipedia.Page(site, u'User:BOTijo/info')
                if infopage.exists():
                    if infopage.get()!=botijoinfo:
                        infopage.put(botijoinfo, botijoinfo)
                else:
                    infopage.put(botijoinfo, botijoinfo)
                if not userpage.exists():
                    userpage.put('{{/info}}', 'Creating...')
                if not talkpage.exists():
                    talkpage.put('#REDIRECT [[User:BOTijo]]', 'Creating...')
                
        except:
            print 'Error, this project probably does not exist'
            pass
