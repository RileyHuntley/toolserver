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

import wikipedia,re 

site=wikipedia.Site("es", "wikipedia")

page=wikipedia.Page(site, u"Wikipedia:Candidaturas a bibliotecario/Tabla")
#{{CandidaturaBibliotecario|Racso|Tomatejc|18/01/2008|03/04/2007|4402|color=#FFFFCC}}
m=re.compile(ur"\{\{CandidaturaBibliotecario\|(?P<candidato>[^\|]+)\|(?P<propuesto>[^\|]+)\|").finditer(page.get())

s=u"{| class='wikitable' width='500px' style='font-size: 90%s;text-align: center;'\n! colspan=7 | Candidaturas a bibliotecario \n|-\n! # !! Usuario !! Propuesto por !! A favor !! En contra !! %s !! Estado" % ("%", "%")
raw=u""
c=0
send=False
limite=0
for i in m:
    limite+=1
    if limite>3:
        break
    cafavor=0
    cencontra=0
    estado=u"Abierta"
    candidato=i.group("candidato")
    propuesto=i.group("propuesto")
    candidatura=u"Wikipedia:Candidaturas a bibliotecario/%s" % candidato
    wikipedia.output(u"Analizando: %s" % candidatura)
    p=wikipedia.Page(site, candidatura)
    t=""
    if p.exists() and not p.isRedirectPage():
        t=site.getUrl(site.get_address(p.urlname()))
        #t=site.getUrl("/w/index.php?title=%s" % re.sub(" ", "_", candidatura))
    else:
        continue
    c+=1
    trozos=t.split('<span class="mw-headline" id="Votos_a_favor">Votos a favor</span>')
    trozos=trozos[1]
    trozos=trozos.split('<span class="mw-headline" id="Votos_en_contra">Votos en contra</span>')
    afavor=trozos[0]
    trozos=trozos[1]
    trozos=trozos.split('<span class="mw-headline" id="Comentarios">Comentarios</span>')
    encontra=trozos[0]
    
    if re.search(ur"(?i)(\{\{ *Archivo votar bibliotecario|No debe hacerse ya ningún cambio en esta página)", p.get()):
        estado=u"Cerrada"
    
    regex=ur"(?mi)^<li>"
    n=re.compile(regex).finditer(afavor)
    
    for j in n:
        cafavor+=1
    
    n=re.compile(regex).finditer(encontra)
    for j in n:
        cencontra+=1
    
    porcentaje=0
    if cafavor+cencontra>0:
        porcentaje=(100.0/(cafavor+cencontra))*cafavor
    if porcentaje>=75:
        s+="\n|-\n| %s || [[Usuario:%s|%s]] || %s || %s || %s || style='background-color:#D0F0C0;' | %.0f%% || [[%s|%s]]" % (c, candidato, candidato, propuesto, cafavor, cencontra, porcentaje, candidatura, estado)
    else:
        s+="\n|-\n| %s || [[Usuario:%s|%s]] || %s || %s || %s || style='background-color:#FFC0CB;' | %.0f%% || [[%s|%s]]" % (c, candidato, candidato, propuesto, cafavor, cencontra, porcentaje, candidatura, estado)
    
    raw+=u"%s;;;%s;;;%s;;;%s;;;%.0f;;;%s;;;%s;;;\n" % (candidato, propuesto, cafavor, cencontra, porcentaje, candidatura, estado)
    send=True

#s+="\n|-\n| colspan=6 | Actualizado a las {{subst:CURRENTTIME}} (UTC) del {{subst:CURRENTDAY}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}}"
s+="\n|}<!-- RAW --><!--\n%s--><!-- RAW --><noinclude>{{documentación}}</noinclude>" % raw

if send:
    wikipedia.output(s)
    page=wikipedia.Page(site, u"Template:ResumenCandidaturasBibliotecario")
    if page.get()!=s:
        page.put(s, u"BOT - Actualizando plantilla")
