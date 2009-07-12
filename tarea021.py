# -*- coding: utf-8 -*-

import wikipedia,re,sys,os,gzip,time

def percent(c):
	if c % 100000 == 0:
		wikipedia.output(u'Llevamos %d' % c)

clasificacion={0:u'·',1:u'Destacado',2:u'Bueno',3:u'Esbozo',4:u'Miniesbozo',5:u'Desambiguación'}
#calidad={0:u'·',1:u'Bueno ([[Imagen:Artículo bueno.svg|14px|Artículo bueno]])',2:u'Destacado ([[Imagen:Cscr-featured.svg|14px|Artículo destacado]])'}
importancia={0:u'·',1:u'Clase-A',2:u'Clase-B',3:u'Clase-C',4:u'Clase-D'}
namespaces={104:u'Anexo'}
namespaces_={104:u'Anexo:'}
limitenuevos=2000
categories={}
proyects=[]
proyectsall=[]
avisotoolserver=u'<noinclude>{{aviso|Esta plantilla es actualizada automáticamente. No hagas cambios aquí. Si hay errores avisa a {{u|emijrp}}.}}</noinclude>\n'
nohay=u':No hay contenido con estas características.'

wikipedia.output(u'Cargando proyectos')
site=wikipedia.Site('es', 'wikipedia')
wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/Wikiproyectos')
if wii.exists() and not wii.isRedirectPage():
	text=wii.get()
	trozos=text.split('\n')
	for trozo in trozos:
		trozo=re.sub(ur'(?im)^ *(.*?) *$', ur'\1', trozo)
		trozo=re.sub(ur'(?i)(Wikiproyecto|Wikiproject):', ur'', trozo)
		trozo=re.sub('_', ' ', trozo)
		proyectsall.append(trozo)
		if trozo[0]=='#':
			continue
		wikipedia.output(u'PR:%s' % trozo)
		if proyects.count(trozo)==0:
			proyects.append(trozo)
	proyectsall.sort()
	salida='\n'.join(proyectsall)
	wii.put(salida, u'BOT - Ordenado lista de wikiproyectos y quitando repeticiones si las hay')

#hacer que carguen las categorias desde una pagina, que quite category: etc, y compruebe que existen
for pr in proyects:
	wikipedia.output(u'Cargando categorias de %s' % pr)
	wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Categorías' % pr)
	if wii.exists() and not wii.isRedirectPage():
		text=wii.get()
		categories[pr]={}
		trozos=text.split('\n')
		categoriesall=[]
		for trozo in trozos:
			trozo=re.sub(ur'(?im)^ *(.*?) *$', ur'\1', trozo)
			trozo=re.sub(ur'(?i)(Categoría|Category):', ur'', trozo)
			trozo=re.sub('_', ' ', trozo)
			if trozo[0]=='#':
				continue
			#wikipedia.output(u'  Categoría:%s' % trozo)
			if categoriesall.count(trozo)==0:
				categoriesall.append(trozo)
				categories[pr][trozo]=[]
		categoriesall.sort()
		salida='\n'.join(categoriesall)
		wii.put(salida, u'BOT - Ordenado lista de categorías y quitando repeticiones si las hay')

page={}
pagetitle2pageid={}

#bajamos los ultimos articulos nuevos y los metemos en un diccionario
nuevos_dic={}
nuevos_list=[]
newpagesgen=site.newpages(number=limitenuevos)

for newpage in newpagesgen:
	newpagetitle=newpage[0].title()
	newpagedate=newpage[1]
	newpageuser=re.sub(ur'( \(aún no redactado\)|(Contribuciones|Contributions)\/|\" class\=\"mw\-userlink)', ur'', newpage[4])
	if not nuevos_dic.has_key(newpagetitle):
		nuevos_dic[newpagetitle]={'date':newpagedate,'user':newpageuser}
		nuevos_list.append(newpagetitle) #para conservar orden cronologico usando el indice de la list[]

#page_id, page_title, page_length
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select page_id, page_title, page_len, page_namespace from page where (page_namespace=0 or page_namespace=104) and page_is_redirect=0;" > /home/emijrp/temporal/eswikipage.txt')
f=open('/home/emijrp/temporal/eswikipage.txt', 'r')
c=0
print 'Cargando paginas de eswiki'
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==4:
		page_id=int(trozos[0])
		page_title=trozos[1]
		page_len=int(trozos[2])
		page_nm=int(trozos[3])
		page_new=False
		if nuevos_dic.has_key(page_title):
			page_new=True
		c+=1
		percent(c)
		pagetitle2pageid[page_title]=page_id
		page[page_id]={'t':page_title, 'l':page_len, 'nm':page_nm, 'i':0, 'c':0, 'cat':0, 'iws':0, 'im':0, 'en':0, 'f':False, 'con':False, 'rel':False, 'wik':False, 'edit':False, 'ref':False, 'obras':False, 'neutral':False, 'trad':False, 'discutido':False, 'nuevo':page_new}
print 'Cargadas %d paginas en eswiki' % c
f.close()


#cargamos page_id y page_title para plantillas
templates={} #nos va a hacer falta luego para las imagenes inservibles
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select page_id, page_title from page where page_namespace=10;" > /home/emijrp/temporal/eswikitemplates.txt')
f=open('/home/emijrp/temporal/eswikitemplates.txt', 'r')
c=0
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==2:
		page_id=int(trozos[0])
		page_title=trozos[1]
		c+=1
		percent(c)
		templates[page_id]=page_title
print 'Cargadas %d templates en eswiki' % c
f.close()

#esto debe ser lo primero, elegir las paginas para los proyectos, y su numero de categorias
#bajamos tabla de categorylinks
exclusioncat_pattern=re.compile(ur'(?i)Wikipedia:')
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select cl_from, cl_to from categorylinks;" > /home/emijrp/temporal/eswikicategorylinks.txt')
f=open('/home/emijrp/temporal/eswikicategorylinks.txt', 'r')
c=0
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==2:
		cl_from=int(trozos[0])
		cl_to=trozos[1]
		for k, v in categories.items():
			if categories[k].has_key(cl_to) and categories[k][cl_to].count(cl_from)==0:
				categories[k][cl_to].append(cl_from)
				c+=1
		#sumamos 1 cat
		if page.has_key(cl_from) and not re.search(exclusioncat_pattern, cl_to):
			#print '->%s<-' % cl_from
			#print page[cl_from]
			page[cl_from]['cat']+=1
print 'Categorizados %d veces' % (c)
f.close()

#comprobamos clasificacion
miniesbozo_pattern=re.compile(ur'(?im)^mini ?esbozo')
esbozo_pattern=re.compile(ur'(?im)^esbozo')
desamb_pattern=re.compile(ur'(?im)^(Des|D[ei]sambig|Desambiguaci[oó]n)$')
destacado_pattern=re.compile(ur'(?im)^Artículo destacado$')
bueno_pattern=re.compile(ur'(?im)^Artículo bueno$')
fusionar_pattern=re.compile(ur'(?im)^Fusionar$')
contextualizar_pattern=re.compile(ur'(?im)^Contextualizar$')
sinrelevancia_pattern=re.compile(ur'(?im)^Sin ?relevancia$')
wikificar_pattern=re.compile(ur'(?im)^Wikificar$')
copyedit_pattern=re.compile(ur'(?im)^Copyedit$')
sinreferencias_pattern=re.compile(ur'(?im)^(Referencias|Artículo sin fuentes|Unreferenced)$')
enobras_pattern=re.compile(ur'(?im)^(En ?obras|En ?desarrollo)$')
noneutral_pattern=re.compile(ur'(?im)^(NN|No ?neutral|NPOV|No ?neutralidad)$')
traduccion_pattern=re.compile(ur'(?im)^Traducción$')
discutido_pattern=re.compile(ur'(?im)^Discutido$')
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select tl_from, tl_title from templatelinks;" > /home/emijrp/temporal/eswikitemplatelinks.txt')
f=open('/home/emijrp/temporal/eswikitemplatelinks.txt', 'r')
c=0
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==2:
		c+=1
		percent(c)
		tl_from=int(trozos[0])
		tl_title=trozos[1]
		if page.has_key(tl_from):
			if re.search(destacado_pattern, tl_title):
				page[tl_from]['c']=1
			elif re.search(bueno_pattern, tl_title):
				page[tl_from]['c']=2
			elif re.search(esbozo_pattern, tl_title):
				page[tl_from]['c']=3
			elif re.search(miniesbozo_pattern, tl_title):
				page[tl_from]['c']=4
			elif re.search(desamb_pattern, tl_title):
				page[tl_from]['c']=5
			#sino es ninguna de las 5 cosas, se queda el 0 que significa desconocida
			
			if re.search(fusionar_pattern, tl_title):
				page[tl_from]['f']=True
			if re.search(contextualizar_pattern, tl_title):
				page[tl_from]['con']=True
			if re.search(sinrelevancia_pattern, tl_title):
				page[tl_from]['rel']=True
			if re.search(wikificar_pattern, tl_title):
				page[tl_from]['wik']=True
			if re.search(copyedit_pattern, tl_title):
				page[tl_from]['edit']=True
			if re.search(sinreferencias_pattern, tl_title):
				page[tl_from]['ref']=True
			if re.search(enobras_pattern, tl_title):
				page[tl_from]['obras']=True
			if re.search(noneutral_pattern, tl_title):
				page[tl_from]['neutral']=True
			if re.search(traduccion_pattern, tl_title):
				page[tl_from]['trad']=True
			if re.search(discutido_pattern, tl_title):
				page[tl_from]['discutido']=True
print '%d templatelinks' % (c)
f.close()

#generamos lista de imagenes inservibles
imagenesnegras={}
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select il_from, il_to from imagelinks;" > /home/emijrp/temporal/eswikiimagelinks.txt')
f=open('/home/emijrp/temporal/eswikiimagelinks.txt', 'r')
c=0
c2=0
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	try: #a veces falla al leer nombres de imagen raros
		line=unicode(line, 'utf-8')
	except:
		continue
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==2:
		c+=1
		percent(c)
		il_from=int(trozos[0])
		il_to=trozos[1]
		if templates.has_key(il_from):
			imagenesnegras[il_to]=False #ahorrar
			c2+=1
print '%d imagelinks, %d imagenes negras' % (c, c2)
f.close()

#ahora contamos imagenes, sin contar inservibles, usamos el mismo fichero q antes
f=open('/home/emijrp/temporal/eswikiimagelinks.txt', 'r')
c=0
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	try: #a veces falla al leer nombres de imagen raros
		line=unicode(line, 'utf-8')
	except:
		continue
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==2:
		il_from=int(trozos[0])
		il_to=trozos[1]
		if page.has_key(il_from) and not imagenesnegras.has_key(il_to):
			page[il_from]['i']+=1
			c+=1
print '%d imagenes usadas' % (c)
f.close()

#contamos interwikis
os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select ll_from, ll_lang from langlinks;" > /home/emijrp/temporal/eswikilanglinks.txt')
f=open('/home/emijrp/temporal/eswikilanglinks.txt', 'r')
c=0
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==2:
		c+=1
		percent(c)
		ll_from=int(trozos[0])
		ll_lang=trozos[1]
		if page.has_key(ll_from):
			page[ll_from]['iws']+=1
print '%d langlinks' % (c)
f.close()

#contamos enlaces entrantes
#bajamos el dump, es mas eficiente
try:
	f=gzip.open('/home/emijrp/temporal/eswiki-latest-pagelinks.sql.gz', 'r')
except:
	os.system('wget http://download.wikimedia.org/eswiki/latest/eswiki-latest-pagelinks.sql.gz -O /home/emijrp/temporal/eswiki-latest-pagelinks.sql.gz') #entorno a 150MB
	f=gzip.open('/home/emijrp/temporal/eswiki-latest-pagelinks.sql.gz', 'r')
c=0
pagelinks_pattern=re.compile(ur'(?i)\((\d+)\,(0|104)\,\'([^\']*?)\'\)') #104 anexo:
for line in f:
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	m=re.findall(pagelinks_pattern, line)
	for i in m:
		c+=1
		percent(c)
		pl_from=int(i[0])
		pl_nm=int(i[1])
		pl_title=u''
		try:
			pl_title=unicode(i[2], 'utf-8')
		except:
			continue
		if page.has_key(pl_from) and pagetitle2pageid.has_key(pl_title): #si el enlace proviene del nm=0 y va hacia un nm=0
			page_id=pagetitle2pageid[pl_title]
			if page.has_key(page_id):
				page[page_id]['en']+=1 #+1 entrante, im es importancia
print '%d pagelinks' % (c)
f.close()


#empezamos el analisis propiamente dicho
limpag=500
limcabecera=50
limkblist=5
cabeceratabla=u'\n|-\n! # !! Artículo !! Disc !! Tamaño !! Clasificación !! Importancia !! Ent !! Cat !! Img !! Iw !! Otros '
for pr, cats in categories.items():
	wikipedia.output(u'%s' % pr)
	inicio=u'{{Wikipedia:Contenido por wikiproyecto/Inicio|%s}}\n\n== Índice ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Índice}}\n\n== Artículos ==\n\'\'Actualizado por última vez a las {{subst:CURRENTTIME}} ([[UTC]]) del {{subst:CURRENTDAY}} de {{subst:CURRENTMONTHNAME}} de {{subst:CURRENTYEAR}}.\'\'\n<center>\n<span style="clear:left;float:left;">{{#ifexpr:{{SUBPAGENAME}}>1|← [[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}-1}}|Anterior]]|← Esta es la primera}}</span><span style="clear:right;float:right;">{{#ifexist:Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|[[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|Siguiente]] →|Esta es la última →}}</span><span id="arriba">↓ [[#abajo|Ir al final]] ↓</span>\n{| class="wikitable sortable" style="text-align: center;"%s' % (pr, pr, pr, pr, pr, cabeceratabla)
	fin=u'\n|}\n<span style="clear:left;float:left;">{{#ifexpr:{{SUBPAGENAME}}>1|← [[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}-1}}|Anterior]]|← Esta es la primera}}</span><span style="clear:right;float:right;">{{#ifexist:Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|[[Wikipedia:Contenido por wikiproyecto/%s/{{#expr:{{SUBPAGENAME}}+1}}|Siguiente]] →|Esta es la última →}}</span><span id="abajo">↑ [[#arriba|Ir al principio]] ↑</span>\n</center>\n\n{{Wikipedia:Contenido por wikiproyecto/Fin|%s}}' % (pr, pr, pr, pr)
	salida=inicio
	c=0
	nodupes=[] #evitamos duplicados
	resumen={'desconocida':0,'bueno':0,'destacado':0,'esbozo':0,'miniesbozo':0,'desambig':0,'>10':0,'>5':0,'>2':0,'>1':0,'<1':0,'<2':0}
	artstitles=[]
	artstitles2=[]
	for cat, arts in cats.items():
		wikipedia.output(u'  Categoría:%s' % cat)
		for artid in arts:
			if page.has_key(artid) and nodupes.count(artid)==0:
				nodupes.append(artid)
				artstitles.append([page[artid]['t'], artid])
				artstitles2.append([page[artid]['en'], page[artid]['t'], artid])
	
	#ordenamos alfabeticamente
	artstitles.sort()
	#ordenamos por entrantes
	artstitles2.sort()
	artstitles2.reverse()
	
	lenartstitles=len(artstitles)
	qclasea=lenartstitles/100*2
	listqclasea=[]
	qclaseb=lenartstitles/100*5-qclasea
	listqclaseb=[]
	qclasec=lenartstitles/100*20-qclaseb
	qclased=lenartstitles-qclasec
	
	#calculamos importancias
	i=0
	for artentrantes, arttitle, artid in artstitles2:
		if i<qclasea:
			page[artid]['im']=1
			if listqclasea.count(arttitle)==0:
				listqclasea.append([artentrantes, arttitle])
		elif i<qclasea+qclaseb:
			page[artid]['im']=2
			if listqclaseb.count(arttitle)==0:
				listqclaseb.append([artentrantes, arttitle])
		elif i<qclasea+qclaseb+qclasec:
			page[artid]['im']=3
		else:
			page[artid]['im']=4
		i+=1
	
	#blanqueamos para ahorrar memoria
	artstitles2=[]
	
	#ordenamos listas de importancia
	listqclasea.sort()
	listqclasea.reverse()
	listqclaseb.sort()
	listqclaseb.reverse()
	
	#generamos salida de listas de importancia
	listqclaseaplana='\n'.join(['# [[%s]] (%d enlaces entrantes)' % (arttitle, artentrantes) for artentrantes, arttitle in listqclasea])
	listqclasebplana='\n'.join(['# [[%s]] (%d enlaces entrantes)' % (arttitle, artentrantes) for artentrantes, arttitle in listqclaseb])
	
	#recorremos los articulos del wikiproyecto
	qfusionar=0
	qcontextualizar=0
	qsinrelevancia=0
	qwikificar=0
	qcopyedit=0
	qsinreferencias=0
	qenobras=0
	qnoneutral=0
	qentraduccion=0
	qveracidaddiscutida=0
	relatedchanges=u''
	for arttitle, pageid in artstitles:
		#resumen tamanios
		if page[pageid]['l']>=10*1024:
			resumen['>10']+=1
		if page[pageid]['l']>=5*1024:
			resumen['>5']+=1
		if page[pageid]['l']>=2*1024:
			resumen['>2']+=1
		if page[pageid]['l']>=1*1024:
			resumen['>1']+=1
		if page[pageid]['l']<1*1024:
			resumen['<1']+=1
		if page[pageid]['l']<2*1024:
			resumen['<2']+=1
		
		#resumen calidad
		if page[pageid]['c']==1:
			resumen['destacado']+=1
		elif page[pageid]['c']==2:
			resumen['bueno']+=1
		elif page[pageid]['c']==3:
			resumen['esbozo']+=1
		elif page[pageid]['c']==4:
			resumen['miniesbozo']+=1
		elif page[pageid]['c']==5:
			resumen['desambig']+=1
		else:
			resumen['desconocida']+=1
		
		c+=1
		otros=u''
		if page[pageid]['f']:
			qfusionar+=1
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Fusionar|fusionar]]' % pr
		if page[pageid]['con']:
			qcontextualizar+=1
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Contextualizar|contextualizar]]' % pr
		if page[pageid]['rel']:
			qsinrelevancia+=1
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Sin relevancia|sin relevancia]]' % pr
		if page[pageid]['wik']:
			qwikificar+=1
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Wikificar|wikificar]]' % pr
		if page[pageid]['edit']:
			qcopyedit+=1
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Copyedit|copyedit]]' % pr
		if page[pageid]['ref']:
			qsinreferencias+=1
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Sin referencias|sin referencias]]' % pr
		if page[pageid]['obras']:
			qenobras+=1
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#En obras|en obras]]' % pr
		if page[pageid]['neutral']:
			qnoneutral+=1
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#No neutral|no neutral]]' % pr
		if page[pageid]['trad']:
			qentraduccion+=1
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#En traducción|en traducción]]' % pr
		if page[pageid]['discutido']:
			qveracidaddiscutida+=1
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Veracidad discutida|discutido]]' % pr
		if page[pageid]['nuevo']:
			if otros:
				otros+=u', '
			otros+=u'[[Wikipedia:Contenido por wikiproyecto/%s#Nuevos|nuevo]]' % pr
		
		clasificacionplana=u''
		if page[pageid]['c']==1: #1 destacado
			clasificacionplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Artículos destacados|Destacado]]' % pr
		elif page[pageid]['c']==2: #2 es bueno, 
			clasificacionplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Artículos buenos|Bueno]]' % pr
		else: #resto: esbozo, miniesbozo, desambig, ·
			clasificacionplana=clasificacion[page[pageid]['c']]
		
		importanciaplana=u''
		if page[pageid]['im']==1:
			importanciaplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Clase-A|Clase-A]]' % pr
		elif page[pageid]['im']==2:
			importanciaplana=u'[[Wikipedia:Contenido por wikiproyecto/%s#Clase-B|Clase-B]]' % pr
		else:
			importanciaplana=importancia[page[pageid]['im']]
		
		artnm=u''
		artnm_=u''
		if page[pageid]['nm']!=0:
			artnm=namespaces[page[pageid]['nm']]
			artnm+=u' ' # http://es.wikipedia.org/w/index.php?title=Wikipedia:Contenido_por_wikiproyecto/Aviaci%C3%B3n/4&curid=1996845&diff=21475084&oldid=21403165
			artnm_=namespaces_[page[pageid]['nm']]
		
		salida+=u'\n|-\n| %d || [[%s%s]] || [[%sDiscusión:%s|Disc]] || %d || %s || %s || %d || %d || %d || %d || %s ' % (c, artnm_, arttitle, artnm, arttitle, page[pageid]['l'], clasificacionplana, importanciaplana, page[pageid]['en'], page[pageid]['cat'], page[pageid]['i'], page[pageid]['iws'], otros)
		relatedchanges+=u'# [[%s%s]]\n' % (artnm_, arttitle) #pagina 0
		#if c % limcabecera == 0:
		#	salida+=cabeceratabla
		if c % limpag == 0:
			salida+=fin
			#guardamos
			wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/%d' % (pr, c/limpag)) #numeracion
			wii.put(salida, u'BOT - Actualizando lista para [[Wikiproyecto:%s]]' % pr)
			salida=inicio
	if salida!=inicio:
		salida+=fin
		#guardamos
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/%d' % (pr, c/limpag+1)) #numeracion
		wii.put(salida, u'BOT - Actualizando lista para [[Wikiproyecto:%s]]' % pr)
	
	#pagina 0 para hacer relatedchanges
	if len(relatedchanges)<=1024*500: #limite de KBs
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/0' % (pr))
		wii.put(relatedchanges, u'BOT - Actualizando lista para [[Wikiproyecto:%s]]' % pr)
	#fin pagina 0
	
	salida=u''
	for i in range(1, c/limpag+2):
		if salida:
			salida+=u' – [[Wikipedia:Contenido por wikiproyecto/%s/%d|Página %d]]' % (pr, i, i)
		else:
			salida+=u'[[Wikipedia:Contenido por wikiproyecto/%s|Resumen]]: [[Wikipedia:Contenido por wikiproyecto/%s/%d|Página %d]]' % (pr, pr, i, i)
	wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Índice' % pr) #index
	wii.put(salida, u'BOT - Actualizando índice')
	
	
	#resumen global
	
	#tabla de clasificacion
	tablaclasificacion=avisotoolserver
	tablaclasificacion+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
	tablaclasificacion+=u'! colspan=4 | Clasificación !! rowspan=2 | Total '
	tablaclasificacion+=u'\n|-\n! [[Wikipedia:Artículos destacados|Destacado]] [[Imagen:Cscr-featured.svg|14px|Artículo destacado]] !! [[Wikipedia:Artículos buenos|Bueno]] [[Imagen:Artículo bueno.svg|14px|Artículo bueno]] !! [[Wikipedia:Página de desambiguación|Desambiguación]] !! Desconocido'
	tablaclasificacion+=u'\n|-\n| [[Wikipedia:Contenido por wikiproyecto/%s#Artículos destacados|%d]] || [[Wikipedia:Contenido por wikiproyecto/%s#Artículos buenos|%d]] || %d || %d || %d ' % (pr, resumen['destacado'], pr, resumen['bueno'], resumen['desambig'], resumen['desconocida'], lenartstitles)
	tablaclasificacion+=u'\n|-\n| %.1f%s || %.1f%s || %.1f%s || %.1f%s || 100%s' % ((resumen['destacado']/(lenartstitles/100.0)), u'%', (resumen['bueno']/(lenartstitles/100.0)), u'%', (resumen['desambig']/(lenartstitles/100.0)), u'%', (resumen['desconocida']/(lenartstitles/100.0)), u'%', u'%')
	tablaclasificacion+=u'\n|}</onlyinclude>\n'
	
	wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Clasificación' % pr) #resumen
	wii.put(tablaclasificacion, u'BOT - Actualizando tabla de clasificación para [[Wikiproyecto:%s]]' % pr)
	
	#tabla de tamanios
	tablatamanos=avisotoolserver
	tablatamanos+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
	tablatamanos+=u'! colspan=6 | Tamaño !! rowspan=2 | Total '
	tablatamanos+=u'\n|-\n! > 10 KB !! > 5 KB !! > 2 KB !! > 1 KB !! < 1 KB !! < 2 KB '
	tablatamanos+=u'\n|-\n| %d || %d || %d || %d || %d || %d || %d ' % (resumen['>10'], resumen['>5'], resumen['>2'], resumen['>1'], resumen['<1'], resumen['<2'], lenartstitles)
	tablatamanos+=u'\n|-\n| %.1f%s || %.1f%s || %.1f%s || %.1f%s || %.1f%s || %.1f%s || 100%s' % ((resumen['>10']/(lenartstitles/100.0)), u'%', (resumen['>5']/(lenartstitles/100.0)), u'%', (resumen['>2']/(lenartstitles/100.0)), u'%', (resumen['>1']/(lenartstitles/100.0)), u'%', (resumen['<1']/(lenartstitles/100.0)), u'%', (resumen['<2']/(lenartstitles/100.0)), u'%', u'%')
	tablatamanos+=u'\n|}</onlyinclude>\n'
	
	wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Tamaños' % pr) #resumen
	wii.put(tablatamanos, u'BOT - Actualizando tabla de tamaños para [[Wikiproyecto:%s]]' % pr)
	
	#tabla de clases (importancia)
	tablaimportancia=avisotoolserver
	tablaimportancia+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
	tablaimportancia+=u'! colspan=4 | Importancia !! rowspan=2 | Total '
	tablaimportancia+=u'\n|-\n! Clase-A ↑↑ !! Clase-B ↑ !! Clase-C ↓ !! Clase-D ↓↓'
	tablaimportancia+=u'\n|-\n| [[Wikipedia:Contenido por wikiproyecto/%s#Clase-A|%d]] || [[Wikipedia:Contenido por wikiproyecto/%s#Clase-B|%d]] || %d || %d || %d ' % (pr, qclasea, pr, qclaseb, qclasec, qclased, lenartstitles)
	tablaimportancia+=u'\n|-\n| 1–2%s || 3–5%s || 6–10%s || 11–100%s || 100%s ' % (u'%', u'%', u'%', u'%', u'%')
	tablaimportancia+=u'\n|}</onlyinclude>\n'
	
	wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Importancia' % pr) #resumen
	wii.put(tablaimportancia, u'BOT - Actualizando tabla de importancia para [[Wikiproyecto:%s]]' % pr)
	
	#tabla de mantenimiento
	qmantenimiento=qfusionar+qcontextualizar+qsinrelevancia+qwikificar+qcopyedit+qsinreferencias+qenobras+qnoneutral+qentraduccion+qveracidaddiscutida
	tablamantenimiento=avisotoolserver
	tablamantenimiento+=u'<onlyinclude>{| class="wikitable" style="text-align: center;clear: {{{1|}}};float: {{{1|}}};"\n'
	tablamantenimiento+=u'! colspan=3 | Mantenimiento '
	tablamantenimiento+=u'\n|-\n! Fusionar \n| [[Wikipedia:Contenido por wikiproyecto/%s#Fusionar|%d]] \n| %.1f%s ' % (pr, qfusionar, (qfusionar/(qmantenimiento/100.0)), u'%')
	tablamantenimiento+=u'\n|-\n! Contextualizar \n| [[Wikipedia:Contenido por wikiproyecto/%s#Contextualizar|%d]] \n| %.1f%s ' % (pr, qcontextualizar, (qcontextualizar/(qmantenimiento/100.0)), u'%')
	tablamantenimiento+=u'\n|-\n! Sin relevancia \n| [[Wikipedia:Contenido por wikiproyecto/%s#Sin relevancia|%d]] \n| %.1f%s ' % (pr, qsinrelevancia, (qsinrelevancia/(qmantenimiento/100.0)), u'%')
	tablamantenimiento+=u'\n|-\n! Wikificar \n| [[Wikipedia:Contenido por wikiproyecto/%s#Wikificar|%d]] \n| %.1f%s ' % (pr, qwikificar, (qwikificar/(qmantenimiento/100.0)), u'%')
	tablamantenimiento+=u'\n|-\n! Copyedit \n| [[Wikipedia:Contenido por wikiproyecto/%s#Copyedit|%d]] \n| %.1f%s ' % (pr, qcopyedit, (qcopyedit/(qmantenimiento/100.0)), u'%')
	tablamantenimiento+=u'\n|-\n! Sin referencias \n| [[Wikipedia:Contenido por wikiproyecto/%s#Sin referencias|%d]] \n| %.1f%s ' % (pr, qsinreferencias, (qsinreferencias/(qmantenimiento/100.0)), u'%')
	tablamantenimiento+=u'\n|-\n! En obras \n| [[Wikipedia:Contenido por wikiproyecto/%s#En obras|%d]] \n| %.1f%s ' % (pr, qenobras, (qenobras/(qmantenimiento/100.0)), u'%')
	tablamantenimiento+=u'\n|-\n! No neutral \n| [[Wikipedia:Contenido por wikiproyecto/%s#No neutral|%d]] \n| %.1f%s ' % (pr, qnoneutral, (qnoneutral/(qmantenimiento/100.0)), u'%')
	tablamantenimiento+=u'\n|-\n! En traducción \n| [[Wikipedia:Contenido por wikiproyecto/%s#En traducción|%d]] \n| %.1f%s ' % (pr, qentraduccion, (qentraduccion/(qmantenimiento/100.0)), u'%')
	tablamantenimiento+=u'\n|-\n! Veracidad discutida \n| [[Wikipedia:Contenido por wikiproyecto/%s#Veracidad discutida|%d]] \n| %.1f%s ' % (pr, qveracidaddiscutida, (qveracidaddiscutida/(qmantenimiento/100.0)), u'%')
	tablamantenimiento+=u'\n|-\n| Total \n| %d \n| 100%s ' % (qmantenimiento, u'%')
	tablamantenimiento+=u'\n|}</onlyinclude>\n'
	
	wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen/Mantenimiento' % pr) #resumen
	wii.put(tablamantenimiento, u'BOT - Actualizando tabla de mantenimiento para [[Wikiproyecto:%s]]' % pr)
	
	#tabla con categorias y numero de articulos que contienen, en desuso
	categoriasanalizadas=u'{| class="wikitable sortable" style="text-align: center;"\n! #\n! Categoría\n! Artículos'
	categoriasordenadas=[]
	for cat, arts in categories[pr].items():
		categoriasordenadas.append([cat, arts])
	categoriasordenadas.sort()
	cont=1
	for cat, arts in categoriasordenadas:
		categoriasanalizadas+=u'\n|-\n| %d || [[:Categoría:%s|%s]] || %d ' %  (cont, cat, cat, len(arts))
		cont+=1
	categoriasanalizadas+=u'\n|}'

	#pagina de resumen con hijas
	resumen=u'\'\'Actualizado por última vez a las {{subst:CURRENTTIME}} ([[UTC]]) del {{subst:CURRENTDAY}} de {{subst:CURRENTMONTHNAME}} de {{subst:CURRENTYEAR}}.\'\'\n'
	resumen+=u'{| style="background-color: transparent"\n| valign=top |\n'
	resumen+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Clasificación}}\n' % pr
	resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Clasificación]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
	resumen+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Tamaños}}\n' % pr
	resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Tamaños]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
	resumen+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Importancia}}\n' % pr
	resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Importancia]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
	resumen+=u'\nEn total han sido analizadas [[Wikipedia:Contenido por wikiproyecto/%s/Categorías|%d categorías]].\n' % (pr, len(categoriasordenadas))
	resumen+=u'| valign=top |\n{{Wikipedia:Contenido por wikiproyecto/%s/Resumen/Mantenimiento}}\n' % pr
	resumen+=u'<small>\'\'Esta tabla proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Resumen/Mantenimiento]]<nowiki>}}</nowiki>\'\'.</small>\n' % pr
	resumen+=u'|}'
	
	wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Resumen' % pr) #resumen
	wii.put(resumen, u'BOT - Actualizando resumen para [[Wikiproyecto:%s]]' % pr)
	
	#seccion importancia, mantenimiento
	clasea=avisotoolserver+listqclaseaplana
	claseb=avisotoolserver+listqclasebplana
	
	buenos=avisotoolserver
	destacados=avisotoolserver
	fusionar=avisotoolserver
	contextualizar=avisotoolserver
	sinrelevancia=avisotoolserver
	wikificar=avisotoolserver
	copyedit=avisotoolserver
	sinreferencias=avisotoolserver
	enobras=avisotoolserver
	noneutral=avisotoolserver
	traduccion=avisotoolserver
	discutido=avisotoolserver
	nuevos=avisotoolserver
	nuevos_temp=[]
	
	for arttitle, pageid in artstitles:
		artnm=u''
		artnm_=u''
		if page[pageid]['nm']!=0:
			artnm=namespaces[page[pageid]['nm']]
			artnm_=namespaces_[page[pageid]['nm']]
		if page[pageid]['c']==2:
			buenos+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['c']==1:
			destacados+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['f']:
			fusionar+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['con']:
			contextualizar+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['rel']:
			sinrelevancia+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['wik']:
			wikificar+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['edit']:
			copyedit+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['ref']:
			sinreferencias+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['obras']:
			enobras+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['neutral']:
			noneutral+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['trad']:
			traduccion+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['discutido']:
			discutido+=u'# [[%s%s]]\n' % (artnm_, arttitle)
		if page[pageid]['nuevo']:
			nuevos_temp.append(arttitle) #los almacenamos para despues ordenarlos cronologicamente
	
	for arttitle in nuevos_list:
		if nuevos_temp.count(arttitle)!=0:
			nuevos+=u'# [[%s%s]] (Creado el %s por [[Usuario:%s|%s]])\n' % (artnm_, arttitle, re.sub(ur'\d\d\:\d\d ', ur'', nuevos_dic[arttitle]['date']), nuevos_dic[arttitle]['user'], nuevos_dic[arttitle]['user'])
	
	salida=u'== Calidad ==\n'
	if destacados:
		if destacados==avisotoolserver:
			destacados+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Artículos destacados' % pr)
		wii.put(destacados, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Artículos destacados [[Imagen:Cscr-featured.svg|14px|Artículo destacado]] ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Artículos destacados|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Artículos destacados]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Artículos destacados}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Artículos destacados]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if buenos:
		if buenos==avisotoolserver:
			buenos+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Artículos buenos' % pr)
		wii.put(buenos, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Artículos buenos [[Imagen:Artículo bueno.svg|14px|Artículo bueno]] ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Artículos buenos|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Artículos buenos]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Artículos buenos}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Artículos buenos]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	salida+=u'== Importancia ==\n'
	if clasea:
		if clasea==avisotoolserver:
			clasea+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Importancia Clase-A' % pr)
		wii.put(clasea, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Clase-A ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Importancia Clase-A|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Importancia Clase-A]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Importancia Clase-A}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Importancia Clase-A]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if claseb:
		if claseb==avisotoolserver:
			claseb+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Importancia Clase-B' % pr)
		wii.put(claseb, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Clase-B ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Importancia Clase-B|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Importancia Clase-B]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Importancia Clase-B}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Importancia Clase-B]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	salida+=u'== Mantenimiento ==\n'
	if fusionar:
		if fusionar==avisotoolserver:
			fusionar+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Fusionar' % pr)
		wii.put(fusionar, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Fusionar ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Fusionar|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Fusionar]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Fusionar}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Fusionar]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if contextualizar:
		if contextualizar==avisotoolserver:
			contextualizar+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Contextualizar' % pr)
		wii.put(contextualizar, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Contextualizar ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Contextualizar|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Contextualizar]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Contextualizar}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Contextualizar]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if sinrelevancia:
		if sinrelevancia==avisotoolserver:
			sinrelevancia+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Sin relevancia' % pr)
		wii.put(sinrelevancia, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Sin relevancia ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Sin relevancia|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Sin relevancia]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Sin relevancia}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Sin relevancia]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if wikificar:
		if wikificar==avisotoolserver:
			wikificar+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Wikificar' % pr)
		wii.put(wikificar, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Wikificar ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Wikificar|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Wikificar]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Wikificar}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Wikificar]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if copyedit:
		if copyedit==avisotoolserver:
			copyedit+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Copyedit' % pr)
		wii.put(copyedit, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Copyedit ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Copyedit|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Copyedit]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Copyedit}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Copyedit]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if sinreferencias:
		if sinreferencias==avisotoolserver:
			sinreferencias+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Sin referencias' % pr)
		wii.put(sinreferencias, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Sin referencias ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Sin referencias|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Sin referencias]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Sin referencias}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Sin referencias]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if enobras:
		if enobras==avisotoolserver:
			enobras+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/En obras' % pr)
		wii.put(enobras, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== En obras ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/En obras|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/En obras]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/En obras}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/En obras]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if noneutral:
		if noneutral==avisotoolserver:
			noneutral+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/No neutral' % pr)
		wii.put(noneutral, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== No neutral ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/No neutral|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/No neutral]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/No neutral}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/No neutral]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if traduccion:
		if traduccion==avisotoolserver:
			traduccion+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/En traducción' % pr)
		wii.put(traduccion, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== En traducción ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/En traducción|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/En traducción]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/En traducción}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/En traducción]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	if discutido:
		if discutido==avisotoolserver:
			discutido+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Veracidad discutida' % pr)
		wii.put(discutido, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'=== Veracidad discutida ===\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Veracidad discutida|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Veracidad discutida]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Veracidad discutida}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Veracidad discutida]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	
	if nuevos:
		if nuevos==avisotoolserver:
			nuevos+=nohay
		wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Nuevos' % pr)
		wii.put(nuevos, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
		salida+=u'== Nuevos ==\n'
		salida+=u'{{#ifexpr:{{PAGESIZE:Wikipedia:Contenido por wikiproyecto/%s/Nuevos|R}}<=%d*1024\n' % (pr, limkblist)
		salida+=u'|:\'\'Esta lista proviene de <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Nuevos]]<nowiki>}}</nowiki>\'\'.\n' % (pr)
		salida+=u'{{Wikipedia:Contenido por wikiproyecto/%s/Nuevos}}\n' % (pr)
		salida+=u'|:\'\'Esta lista excede los %d KB y no se mostrará. Se puede consultar directamente en <nowiki>{{</nowiki>[[Wikipedia:Contenido por wikiproyecto/%s/Nuevos]]<nowiki>}}</nowiki>\'\'.\n' % (limkblist, pr)
		salida+=u'}}\n\n'
	
	wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s/Detalles' % pr) #detalles
	wii.put(salida, u'BOT - Actualizando detalles para [[Wikiproyecto:%s]]' % pr)
	
	
	#pagina del pr
	#salida=u'{{Wikipedia:Contenido por wikiproyecto/Iconos|%s}}\nAnálisis del contenido en el ámbito de [[Wikiproyecto:%s]]. Para añadir páginas debes modificar la <span class="plainlinks">[http://es.wikipedia.org/w/index.php?title=Wikipedia:Contenido_por_wikiproyecto/%s/Categorías&action=edit lista de categorías]</span>.\n\n== Índice ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Índice}}\n\n== Resumen ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Resumen}}\n\n{{Wikipedia:Contenido por wikiproyecto/%s/Detalles}}\n\n[[Categoría:Wikipedia:Contenido por wikiproyecto|%s]]\n[[Categoría:Wikipedia:Contenido por wikiproyecto/%s| ]]' % (pr, pr, re.sub(u' ', u'_', pr), pr, pr, pr, pr, pr)
	salida=u'{{Wikipedia:Contenido por wikiproyecto/Iconos|%s}}\nAnálisis del contenido en el ámbito de [[Wikiproyecto:%s]]. Para añadir páginas debes modificar la <span class="plainlinks">[http://es.wikipedia.org/w/index.php?title=Wikipedia:Contenido_por_wikiproyecto/%s/Categorías&action=edit lista de categorías]</span>. {{Purgar|Actualizar esta página}}.\n\n== Índice ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Índice}}\n\n== Resumen ==\n{{Wikipedia:Contenido por wikiproyecto/%s/Resumen}}\n\n{{Wikipedia:Contenido por wikiproyecto/%s/Detalles}}\n\n[[Categoría:Wikipedia:Contenido por wikiproyecto|%s]]\n[[Categoría:Wikipedia:Contenido por wikiproyecto/%s| ]]' % (pr, pr, re.sub(u' ', u'_', pr), pr, pr, pr, pr, pr)
	wii=wikipedia.Page(site, u'Wikipedia:Contenido por wikiproyecto/%s' % pr) #principal
	wii.put(salida, u'BOT - Actualizando página de [[Wikiproyecto:%s]]' % pr)
	

