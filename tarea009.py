# -*- coding: utf-8 -*-

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

page=wikipedia.Page(wikipedia.Site("commons", "commons"), u"Template:Potd/%s (es)" % date)
description=u"Error. No hay imagen del día."
if page.exists() and not page.isRedirectPage() and not page.isDisambig():
	description=page.get()

page=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Template:IDDC/Imagen")
page.put(file, u"BOT - Actualizando imagen del día de Commons")

page=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Template:IDDC/Descripción")
page.put(description, u"BOT - Actualizando descripción de la imagen del día de Commons")

