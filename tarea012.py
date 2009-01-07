import wikipedia,re 

site=wikipedia.Site("es", "wikipedia")

page=wikipedia.Page(site, u"Wikipedia:Candidaturas a bibliotecario/Tabla")
#{{CandidaturaBibliotecario|Racso|Tomatejc|18/01/2008|03/04/2007|4402|color=#FFFFCC}}
m=re.compile(ur"\{\{CandidaturaBibliotecario\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|color=#FFFFCC\}\}").finditer(page.get())

s=u"{| class='wikitable' width='300px' style='font-size: 90%s;text-align: center;'\n|+ <big><big>'''Candidaturas a bibliotecario'''</big></big>\n! #\n! Usuario\n! Candidatura\n! A favor\n! En contra\n! %s" % ("%", "%")
c=0
send=False
for i in m:
	cafavor=0
	cencontra=0
	candidatura=u"Wikipedia:Candidaturas a bibliotecario/%s" % i.group(1)
	usuario=i.group(1)
	wikipedia.output(u"Analizando: %s" % candidatura)
	p=wikipedia.Page(site, candidatura)
	t=""
	if p.exists() and not p.isRedirectPage():
		t=site.getUrl(site.get_address(p.urlname()))
		#t=site.getUrl("/w/index.php?title=%s" % re.sub(" ", "_", candidatura))
	else:
		continue
	c+=1
	trozos=t.split('<span class="mw-headline">Votos a favor</span>')
	trozos=trozos[1]
	trozos=trozos.split('<span class="mw-headline">Votos en contra</span>')
	afavor=trozos[0]
	trozos=trozos[1]
	trozos=trozos.split('<span class="mw-headline">Comentarios</span>')
	encontra=trozos[0]
	
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
		s+="\n|-\n| %s || [[Usuario:%s|%s]] || [[%s|Ver]] || %s || %s || style='background-color:#D0F0C0;' | %.0f%s " % (c, usuario, usuario, candidatura, cafavor, cencontra, porcentaje, "%")
	else:
		s+="\n|-\n| %s || [[Usuario:%s|%s]] || [[%s|Ver]] || %s || %s || style='background-color:#FFC0CB;' | %.0f%s " % (c, usuario, usuario, candidatura, cafavor, cencontra, porcentaje, "%")
	
	send=True

s+="\n|-\n| colspan=6 | Actualizado a las {{subst:CURRENTTIME}} (UTC) del {{subst:CURRENTDAY}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}}\n|}<noinclude>{{uso de plantilla}}</noinclude>"

if send:
	wikipedia.output(s)
	page=wikipedia.Page(site, u"Template:ResumenCandidaturasBibliotecario")
	page.put(s, u"BOT - Actualizando plantilla")
