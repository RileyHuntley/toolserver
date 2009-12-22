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

import wikipedia,re,sys,os,gzip,time, datetime
import time, urllib

url='http://s23.org/wikistats/wikipedias_wiki.php'
f=urllib.urlopen(url, 'r')
text=f.read()
text=re.sub(ur'(?im)[\n\r]*</?pre>[\n\r]*', ur'', text)
text=u'Lista de Wikipedias extraida de %s\n\n%s' % (url, text)
p=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'User:Emijrp/Lista de Wikipedias')
p.put(text, u'BOT - Updating from %s' % url)

