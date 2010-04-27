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

import os
import wikipedia
import re
import datetime

commonssite=wikipedia.Site("en", "wikipedia")
username="enwikipotd"
password=""
f=open("/home/emijrp/.my.cnf2", "r")
raw=f.read()
f.close()
m=re.findall(ur'%s = *"(.*)"' % username, raw)
password=m[0]

today=datetime.date.today()
page=wikipedia.Page(commonssite, u"Template:POTD protected/%s" % today.isoformat())
m=re.findall(ur'(?i)\[\[ *file *: *([^\|]*?) *\|', page.get())
imagename=m[0]
m=re.findall(ur'(?i)\[\[ *file *: *%s *\| *[^\|]+? *\| *(.*?) *\{\{ *\# *if *:' % imagename, page.get())
imagedesc=m[0]
imagedesc=re.sub(ur'(?i)\[\[([^\|]*?)\|(?P<label>[^\]]*?)\]\]', ur'\g<label>', imagedesc)
imagedesc=re.sub(ur'(?i)[\[\]]', ur'', imagedesc)
if len(imagedesc)>40:
    imagedesc=u'%s...' % (imagedesc[:40])
imagename_=re.sub(" ", "_", imagename)
msg=u'%s → http://en.wikipedia.org/wiki/File:%s #wikipedia #photos' % (imagedesc, imagename_)

orden='curl -u %s:%s -d status="%s" http://twitter.com/statuses/update.json' % (username, password, msg.encode("utf-8"))
os.system(orden)

