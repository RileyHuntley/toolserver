# -*- coding: utf-8 -*-

import wikipedia,re,sys,os,gzip,time, datetime
import time, urllib

url='http://s23.org/wikistats/wikipedias_wiki.php'
f=urllib.urlopen(url, 'r')
text=f.read()
text=re.sub(ur'(?im)[\n\r]*</?pre>[\n\r]*', ur'', text)
text=u'Lista de Wikipedias extraida de %s\n\n%s' % (url, text)
p=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'User:Emijrp/Lista de Wikipedias')
p.put(text, u'BOT - Updating from %s' % url)

