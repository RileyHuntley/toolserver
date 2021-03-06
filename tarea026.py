#!/usr/bin/env python2.5
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

import wikipedia, re
 
ensite = wikipedia.Site('en', 'wikipedia')
essite = wikipedia.Site('es', 'wikipedia')
entool = wikipedia.Page(ensite, u'Template:Toolserver')
estool = wikipedia.Page(essite, u'Template:Toolserver')

enwtext=entool.get()
update=enwtext.split("<!--update-->")[1]
update=update.replace("January", "de enero de")
update=update.replace("February", "de febrero de")
update=update.replace("March", "de marzo de")
update=update.replace("April", "de abril de")
update=update.replace("May", "de mayo de")
update=update.replace("June", "de junio de")
update=update.replace("July", "de julio de")
update=update.replace("August", "de agosto de")
update=update.replace("September", "de septiembre de")
update=update.replace("October", "de octubre de")
update=update.replace("November", "de noviembre de")
update=update.replace("December", "de diciembre de")
rosemary=enwtext.split("<!--rosemary-->")[1]
daphne=enwtext.split("<!--daphne-->")[1]
yarrow=enwtext.split("<!--yarrow-->")[1]
s1=enwtext.split("<!--s1-->")[1]
s2=enwtext.split("<!--s2-->")[1]
s3=enwtext.split("<!--s3-->")[1]
s4=enwtext.split("<!--s4-->")[1]
s5=enwtext.split("<!--s5-->")[1]

dic={u'up':u'En línea',u'down':u'Fuera de línea'}

salida=u'''{| class="infobox" style="width: {{{width|auto}}}; float: {{{float|right}}}; clear: {{{clear|right}}};"
|-
! colspan="2" | Estado de [[m:Toolserver|Toolserver]]
|-
! Última actualización
| <!--update-->%s<!--update-->
|-
!MySQL rosemary
| <!--rosemary-->%s<!--rosemary-->
|-
!MySQL daphne
| <!--daphne-->%s<!--daphne--> 
|-
!MySQL yarrow
| <!--yarrow-->%s<!--yarrow-->
|-
!Lag en s1
| <!--s1-->%s<!--s1-->
|-
!Lag en s2
| <!--s2-->%s<!--s2-->
|-
!Lag en s3
| <!--s3-->%s<!--s3-->
|-
!Lag en s4
| <!--s4-->%s<!--s4-->
|-
!Lag en s5
| <!--s5-->%s<!--s5-->
|}<noinclude>{{documentación}}</noinclude>''' % (update, dic[rosemary], dic[daphne], dic[yarrow], s1, s2, s3, s4, s5)

estool.put(salida, u'BOT - Estado: rosemary: %s; daphne %s; yarrow %s; Replag: s1 %s; s2 %s; s3 %s; s4 %s; s5 %s' % (dic[rosemary], dic[daphne], dic[yarrow], s1, s2, s3, s4, s5))


