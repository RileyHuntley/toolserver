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

import wikipedia,re,os

os.system('date +"%Y-%m-%d" > /home/emijrp/temporal/tarea009.data')

f=open('/home/emijrp/temporal/tarea009.data', 'r')
sql=unicode(f.read(), 'utf-8')
f.close()
m=re.compile(ur"(\d{4}-\d{2}-\d{2})").finditer(sql)

for i in m:
	date=i.group(1)

page=wikipedia.Page(wikipedia.Site("commons", "commons"), u"Template:Potd/%s" % date)
file=u"Example.jpg"
if page.exists() and not page.isRedirectPage() and not page.isDisambig():
	file=page.get()
file=file.split("|")[1].split("|")[0]

page=wikipedia.Page(wikipedia.Site("commons", "commons"), u"Template:Potd/%s (es)" % date)
description=u"Error. No hay imagen del día."
if page.exists() and not page.isRedirectPage() and not page.isDisambig():
	description=page.get()
description=description.split("=")[1].split("\n")[0]

page=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Template:IDDC/Imagen")
page.put(file, u"BOT - Actualizando imagen del día de Commons")

page=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Template:IDDC/Descripción")
page.put(description, u"BOT - Actualizando descripción de la imagen del día de Commons")

