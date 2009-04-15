#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
 
import wikipedia, re
 
ensite = wikipedia.Site('en', 'wikipedia')
essite = wikipedia.Site('es', 'wikipedia')
entool = wikipedia.Page(ensite, u'Template:Toolserver')
estool = wikipedia.Page(essite, u'Template:Toolserver')

enwtext=entool.get()
update=enwtext.split("<!--update-->")[1]
update=update.replace("January", "de enero de")
update=update.replace("April", "de abril de")
rosemary=enwtext.split("<!--rosemary-->")[1]
zedler=enwtext.split("<!--zedler-->")[1]
yarrow=enwtext.split("<!--yarrow-->")[1]
s1=enwtext.split("<!--s1-->")[1]
s2=enwtext.split("<!--s2-->")[1]
s3=enwtext.split("<!--s3-->")[1]

dic={u'up':u'En línea',u'down':u'Fuera de línea'}

salida=u'''
{| class="infobox" style="width: {{{width|auto}}}; float: {{{float|right}}}; clear: {{{clear|right}}};"
|-
! colspan="2" | Estado de [[m:Toolserver|Toolserver]]
|-
! Última actualización
| <!--update-->%s<!--update-->
|-
!MySQL rosemary
| <!--rosemary-->%s<!--rosemary-->
|-
!MySQL zedler
| <!--zedler-->%s<!--zedler--> 
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
| colspan="2" style="text-align:center;" |''[[tools:~leon/stats/replag/all/replag-daily.png|Gráfica diaria de lag]]'' 
|}<noinclude>{{uso de plantilla}}</noinclude>''' % (update, dic[rosemary], dic[zedler], dic[yarrow], s1, s2, s3)

estool.put(salida, u'Estado: rosemary: %s; zedler %s; yarrow %s; Replag: s1 %s; s2 %s; s3 %s;' % (dic[rosemary], dic[zedler], dic[yarrow], s1, s2, s3))


