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

#w, wikt, b, q, s, n, v
family='wikipedia'
langswiki=['ab', 'af', 'ak', 'als', 'am', 'an', 'ang', 'ar', 'arc', 'arz', 'as', 'ast', 'av', 'ay', 'az', 'ba', 'bar', 'bat-smg', 'bcl', 'be', 'be-x-old', 'bg', 'bh', 'bi', 'bm', 'bn', 'bo', 'bpy', 'br', 'bs', 'bug', 'bxr', 'ca', 'cbk-zam', 'cdo', 'ce', 'ceb', 'ch', 'cho', 'chr', 'chy', 'closed-zh-tw', 'co', 'cr', 'crh', 'cs', 'csb', 'cu', 'cv', 'cy', 'cz', 'da', 'de', 'diq', 'dk', 'dsb', 'dv', 'dz', 'ee', 'el', 'eml', 'eo', 'epo', 'es', 'et', 'eu', 'ext', 'fa', 'ff', 'fi', 'fiu-vro', 'fj', 'fo', 'fr', 'frp', 'fur', 'fy', 'ga', 'gan', 'gd', 'gl', 'glk', 'gn', 'got', 'gu', 'gv', 'ha', 'hak', 'haw', 'he', 'hi', 'hif', 'ho', 'hr', 'hsb', 'ht', 'hu', 'hy', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'ilo', 'io', 'is', 'it', 'iu', 'ja', 'jbo', 'jp', 'jv', 'ka', 'kaa', 'kab', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'ksh', 'ku', 'kv', 'kw', 'ky', 'la', 'lad', 'lb', 'lbe', 'lg', 'li', 'lij', 'lmo', 'ln', 'lo', 'lt', 'lv', 'map-bms', 'mdf', 'mg', 'mh', 'mi', 'minnan', 'mk', 'ml', 'mn', 'mo', 'mr', 'ms', 'mt', 'mus', 'my', 'myv', 'mzn', 'na', 'nah', 'nan', 'nap', 'nb', 'nds', 'nds-nl', 'ne', 'new', 'ng', 'nl', 'nn', 'no', 'nomcom', 'nov', 'nrm', 'nv', 'ny', 'oc', 'om', 'or', 'os', 'pa', 'pag', 'pam', 'pap', 'pdc', 'pi', 'pih', 'pl', 'pms', 'ps', 'pt', 'qu', 'rm', 'rmy', 'rn', 'ro', 'roa-rup', 'roa-tara', 'ru', 'rw', 'sa', 'sah', 'sc', 'scn', 'sco', 'sd', 'se', 'sg', 'sh', 'si', 'simple', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'srn', 'ss', 'st', 'stq', 'su', 'sv', 'sw', 'szl', 'ta', 'te', 'tet', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tokipona', 'tp', 'tpi', 'tr', 'ts', 'tt', 'tum', 'tw', 'ty', 'udm', 'ug', 'uk', 'ur', 'uz', 've', 'vec', 'vi', 'vls', 'vo', 'wa', 'war', 'wo', 'wuu', 'xal', 'xh', 'yi', 'yo', 'za', 'zea', 'zh', 'zh-cfr', 'zh-classical', 'zh-min-nan', 'zh-yue', 'zu', ]

for lang in langswiki:
    try:
        tem=u"[[Image:Redirectltr.png|#REDIRECT ]]<span class=\"redirectText\" id=\"softredirect\">[[{{{1}}}]]</span><br /><span style=\"font-size:85%; padding-left:52px;\">This page is a [[:w:Wikipedia:Soft redirect|soft redirect]].</span>"
        tempage=wikipedia.Page(wikipedia.Site(lang, family), u'Template:Softredirect')
        if not tempage.exists():
            tempage.put(tem, u"From [[:w:en:Template:Softredirect]]")
        
        msg=u"{{Softredirect|w:es:User:Emijrp}}"
        msgold=u"{{Babel|es|en-2|fr-1}}\nHi. I'm a Spanish user. You can see my userpage in [[:es:User:Emijrp]]. Comments to [[:es:User talk:Emijrp]]. Thanks."
        userpage=wikipedia.Page(wikipedia.Site(lang, family), u'User:Emijrp')
        talkpage=wikipedia.Page(wikipedia.Site(lang, family), u'User talk:Emijrp')
        if not userpage.exists() or len(msgold)==len(userpage.get()):
            userpage.put(msg, msg)
        if not talkpage.exists() or len(msgold)==len(talkpage.get()):
            talkpage.put(msg, msg)
    except:
        pass
    
