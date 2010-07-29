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

import os, datetime, re, urllib

inactivas=['aa',]
nointeresa=['en',]

langs=['ab', 'af', 'ak', 'als', 'am', 'an', 'ang', 'ar', 'arc', 'arz', 'as', 'ast', 'av', 'ay', 'az', 'ba', 'bar', 'bat-smg', 'bcl', 'be', 'be-x-old', 'bg', 'bh', 'bi', 'bm', 'bn', 'bo', 'bpy', 'br', 'bs', 'bug', 'bxr', 'ca', 'cbk-zam', 'cdo', 'ce', 'ceb', 'ch', 'cho', 'chr', 'chy', 'closed-zh-tw', 'co', 'cr', 'crh', 'cs', 'csb', 'cu', 'cv', 'cy', 'cz', 'da', 'de', 'diq', 'dk', 'dsb', 'dv', 'dz', 'ee', 'el', 'eml', 'en', 'eo', 'epo', 'es', 'et', 'eu', 'ext', 'fa', 'ff', 'fi', 'fiu-vro', 'fj', 'fo', 'fr', 'frp', 'fur', 'fy', 'ga', 'gan', 'gd', 'gl', 'glk', 'gn', 'got', 'gu', 'gv', 'ha', 'hak', 'haw', 'he', 'hi', 'hif', 'ho', 'hr', 'hsb', 'ht', 'hu', 'hy', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'ilo', 'io', 'is', 'it', 'iu', 'ja', 'jbo', 'jp', 'jv', 'ka', 'kaa', 'kab', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'ksh', 'ku', 'kv', 'kw', 'ky', 'la', 'lad', 'lb', 'lbe', 'lg', 'li', 'lij', 'lmo', 'ln', 'lo', 'lt', 'lv', 'map-bms', 'mdf', 'mg', 'mh', 'mi', 'minnan', 'mk', 'ml', 'mn', 'mo', 'mr', 'ms', 'mt', 'mus', 'my', 'myv', 'mzn', 'na', 'nah', 'nan', 'nap', 'nb', 'nds', 'nds-nl', 'ne', 'new', 'ng', 'nl', 'nn', 'no', 'nomcom', 'nov', 'nrm', 'nv', 'ny', 'oc', 'om', 'or', 'os', 'pa', 'pag', 'pam', 'pap', 'pdc', 'pi', 'pih', 'pl', 'pms', 'ps', 'pt', 'qu', 'rm', 'rmy', 'rn', 'ro', 'roa-rup', 'roa-tara', 'ru', 'rw', 'sa', 'sah', 'sc', 'scn', 'sco', 'sd', 'se', 'sg', 'sh', 'si', 'simple', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'srn', 'ss', 'st', 'stq', 'su', 'sv', 'sw', 'szl', 'ta', 'te', 'tet', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tokipona', 'tp', 'tpi', 'tr', 'ts', 'tt', 'tum', 'tw', 'ty', 'udm', 'ug', 'uk', 'ur', 'uz', 've', 'vec', 'vi', 'vls', 'vo', 'wa', 'war', 'wo', 'wuu', 'xal', 'xh', 'yi', 'yo', 'za', 'zea', 'zh', 'zh-cfr', 'zh-classical', 'zh-min-nan', 'zh-yue', 'zu']

#langs=['ii', 'ik', 'ilo', 'io', 'is', 'it', 'iu', 'ja', 'jbo', 'jp', 'jv', 'ka', 'kaa', 'kab', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'ksh', 'ku', 'kv', 'kw', 'ky', 'la', 'lad', 'lb', 'lbe', 'lg', 'li', 'lij', 'lmo', 'ln', 'lo', 'lt', 'lv', 'map-bms', 'mdf', 'mg', 'mh', 'mi', 'minnan', 'mk', 'ml', 'mn', 'mo', 'mr', 'ms', 'mt', 'mus', 'my', 'myv', 'mzn', 'na', 'nah', 'nan', 'nap', 'nb', 'nds', 'nds-nl', 'ne', 'new', 'ng', 'nl', 'nn', 'no', 'nomcom', 'nov', 'nrm', 'nv', 'ny', 'oc', 'om', 'or', 'os', 'pa', 'pag', 'pam', 'pap', 'pdc', 'pi', 'pih', 'pl', 'pms', 'ps', 'pt', 'qu', 'rm', 'rmy', 'rn', 'ro', 'roa-rup', 'roa-tara', 'ru', 'rw', 'sa', 'sah', 'sc', 'scn', 'sco', 'sd', 'se', 'sg', 'sh', 'si', 'simple', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'srn', 'ss', 'st', 'stq', 'su', 'sv', 'sw', 'szl', 'ta', 'te', 'tet', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tokipona', 'tp', 'tpi', 'tr', 'ts', 'tt', 'tum', 'tw', 'ty', 'udm', 'ug', 'uk', 'ur', 'uz', 've', 'vec', 'vi', 'vls', 'vo', 'wa', 'war', 'wo', 'wuu', 'xal', 'xh', 'yi', 'yo', 'za', 'zea', 'zh', 'zh-cfr', 'zh-classical', 'zh-min-nan', 'zh-yue', 'zu']

#langs=[u'es', u'de', u'fr', u'pl', u'ja', u'it', u'nl', u'pt', u'ru', u'sv', u'zh', u'no', u'fi', u'ca', u'uk', u'tr', u'ro', u'vo', u'cs', u'hu', u'eo', u'sk', u'da', u'id', u'he', u'ar', u'ko', u'lt', u'sr', u'vi', u'sl', u'bg', u'et', u'fa', u'hr', u'ht', u'new', u'nn', u'te', u'gl', u'simple', u'th', u'el', u'ceb', u'ms', u'eu', u'ka', u'bs', u'lb', u'la', u'hi', u'is', u'bpy', u'br', u'mk', u'sq', u'mr', u'az', u'sh', u'cy', u'tl', u'bn', u'pms', u'lv', u'oc', u'io', u'ta', u'jv', u'su', u'be', u'nds', u'scn', u'nap', u'ku', u'ast', u'an', u'af', u'wa']

#de menos a mas articulos, 10k-100k
#langs=['war', 'cv', 'ml', 'ur', 'qu', 'bat-smg', 'wa', 'zh-yue', 'sw', 'ast', 'fy', 'af', 'ku', 'nap', 'scn', 'su', 'nds', 'an', 'be', 'io', 'ta', 'oc', 'bn', 'jv', 'be-x-old', 'pms', 'lv', 'tl', 'sh', 'bpy', 'mr', 'sq', 'cy', 'az', 'is', 'bs', 'lb', 'br', 'la', 'ka', 'mk', 'hi', 'ceb', 'eu', 'ms', 'el', 'te', 'th', 'gl', 'ht', 'simple', 'new', 'hr', 'fa', 'et', 'bg', 'sl', 'sr', 'lt', 'vi', 'he']
#+100k
#langs=['ar', 'ko', 'id', 'sk', 'da', 'eo', 'vo', 'ro', 'hu', 'cs', 'tr', 'uk', 'fi', 'no', 'zh', 'sv', 'ru', 'pt', 'es', 'nl', 'it', 'ja', 'pl', 'fr', 'de']

"""f=urllib.urlopen('http://noc.wikimedia.org/conf/all.dblist', 'r')
raw=f.read()
l=raw.splitlines()
langs=[]
for t in l:
    if t[-4:]=='wiki':
        lang=t.split("wiki")[0]
        if not lang in ["en"]+inactivas:
            langs.append(lang)
f.close()"""

try:
    os.remove("/mnt/user-store/enwiki-latest-imagelinks.sql.gz")
    os.remove("/mnt/user-store/enwiki-latest-categorylinks.sql.gz")
except:
    print "Error: no se pudieron borrar los archivos enwiki-latest-imagelinks.sql.gz y enwiki-latest-categorylinks.sql.gz"

print "Se van a analizar", len(langs), "idiomas"

for lang in langs:
    if lang in inactivas or lang in nointeresa:
        continue
    os.system('python /home/emijrp/python/tareas/missingimages.py %s' % lang)
    os.system('mysql -h sql -e "use u_emijrp_yarrow;delete from imagesforbio where language=\'%s\';"' % lang)
    os.system('mysql -h sql u_emijrp_yarrow < /home/emijrp/temporal/candidatas-%s.sql' % lang)
