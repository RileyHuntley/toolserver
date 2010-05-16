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

import wikipedia
import re
import os
import datetime

def main():
    date=datetime.date.today().isoformat()

    commonssite=wikipedia.Site("commons", "commons")
    eswikisite=wikipedia.Site("es", "wikipedia")

    page=wikipedia.Page(commonssite, u"Template:Potd/%s" % date)
    file=u"Example.jpg"
    if page.exists() and not page.isRedirectPage() and not page.isDisambig():
        file=page.get()
    file=file.split("|")[1].split("|")[0]

    description=u""
    for lang in ['es', 'en']:
        page=wikipedia.Page(commonssite, u"Template:Potd/%s (%s)" % (date, lang))
        if page.exists() and not page.isRedirectPage() and not page.isDisambig():
            description=page.get()
            if re.search(ur"(?i)(\{\{ *Potd description *\|1=)", description):
                description=description.split("|1=")[1].split("|2=")[0]
            elif re.search(ur"(?i)(\{\{ *Potd description *\|[^ \d])", description):
                description=description.split("|")[1].split("|")[0]
            elif not re.search(ur"(?i)\{\{", description):
                pass
            else:
                print "Error al parsear", description
                description=u""

    page=wikipedia.Page(eswikisite, u"Template:IDDC/Imagen")
    page.put(file, u"BOT - Actualizando imagen del día de Commons")

    page=wikipedia.Page(eswikisite, u"Template:IDDC/Descripción")
    page.put(description, u"BOT - Actualizando descripción de la imagen del día de Commons")

if __name__ == "__main__":
    main()
