# -*- coding: utf-8  -*-

from __future__ import generators
import sys, re
import wikipedia, pagegenerators,catlib, config,time, thread
import urllib


pre=u"Usuario:Emijrp/MiPortal/Lemario/"

salida=u"{{subst:ProgresoLemario/subst"

tr=0
ta=0

for p in [u"a-absolver", u"absorbencia-achicadura", u"achicamiento-acullicar", u"acullico-aeromotor", u"aeromoza-agravaci%C3%B3n", u"agravador-ajimezado", u"ajipa-alcantarillar", u"alcantarillero-alhorra", u"alhorre-aloja", u"alojado-ambientar", u"ambiente-anatomopatol%C3%B3gico", u"anatomopat%C3%B3logo-antecapilla", u"antecedencia-apaleador", u"apaleamiento-apresto", u"apresura-argelino", u"argemone-arrinconar", u"arriostrar-asistimiento", u"asistir-atisuado", u"atizacandiles-avance", u"avandicho-%C3%A1bsida", u"%C3%A1bside-balotaje", u"balotar-basilisco", u"basis-besalamano", u"besamanos-bland%C3%B3n", u"blanqueaci%C3%B3n-borneadizo", u"borneadura-broquelazo", u"broquelero-cabalgar", u"cabalgata-cajo", u"cajonada-camachuelo", u"camada-canijo", u"canil-carapachay", u"carapacho-carra%C3%B1a", u"carra%C3%B1aca-catascopio", u"catasta-cedrito", u"cedro-ceroferario", u"cerole%C3%ADna-chape", u"chapeado-chipojo", u"chipolo-churumen", u"churumo-cirio", u"cirolero-cochama", u"cochambre-colofonita", u"colofon%C3%ADa-compuerta", u"compuestamente-congelativo", u"congenial-continuidad", u"continuismo-copiar", u"copichuela-corruco", u"corrugaci%C3%B3n-criadero", u"criadilla-cuatr%C3%ADn", u"cuat%C3%AD-curtimiento", u"curtir-decadente", u"decadentismo-demogr%C3%A1fico", u"demoledor-desairar", u"desaire-descargamiento", u"descargar-desenastar", u"desencabalgado-desimponer", u"desimpresionar-despego", u"despegue-desvergonzado", u"desvergonzarse-dignificar", u"digno-disyuntiva", u"disyuntivamente-dubitativo", u"ducado-ejemplo", u"ejercer-embrisar", u"embri%C3%B3logo-enardecedor", u"enardecer-encostradura", u"encostrar-engranerar", u"engranujarse-ense%C3%B1o", u"ense%C3%B1oramiento-envejecido", u"envejecimiento-escalfecerse", u"escalfeta-escuadreo", u"escuadrilla-esperteza", u"esper%C3%B3n-estelado", u"estelar-est%C3%BApidamente", u"est%C3%BApido-expedienteo", u"expedir-falciforme", u"falcinelo-ferial", u"feriante-fitogr%C3%A1fico", u"fitolac%C3%A1ceo-fornicar", u"fornicario-frotador", u"frotadura-galancete", u"galanga-garrobal", u"garrobilla-ginefobia", u"ginesta-granad%C3%AD", u"granalla-guaquero", u"guara-g%C3%BCimba", u"g%C3%BCin-hemograma", u"hemolisina-hilander%C3%ADa", u"hilanza-hontanal", u"hontanar-h%C3%BAmico", u"h%C3%BAmido-impresionar", u"impresionismo-incumplir", u"incunable-infrasonido", u"infrautilizaci%C3%B3n-institucionalizaci%C3%B3n", u"institucionalizar-inventaci%C3%B3n", u"inventador-jactancioso", u"jactar-jubeter%C3%ADa", u"jubilaci%C3%B3n-lagrimeo", u"lagrimoso-lebulense", u"lecanomancia-lidio", u"lidioso-loanda", u"loanza-l%C3%BAcidamente", u"l%C3%BAcido-malaleche", u"malambo-manifestador", u"manifestante-marqueta", u"marqueter%C3%ADa-mecedor", u"mecedura-mercadero", u"mercader%C3%ADa-miligramo", u"mililitro-moharrache", u"moharracho-morcillo", u"morcill%C3%B3n-mundanalidad", u"mundanamente-Leiden", u"Leo-nefrosis", u"nefr%C3%ADtico-nonada", u"nonagenario-obsidional", u"obsolescencia-onerario", u"oneroso-ostrogodo", u"ostr%C3%ADcola-pallar", u"pallas-paraliticado", u"paraliticarse-pastor%C3%ADa", u"pastosidad-peindra", u"peine-perforaci%C3%B3n", u"perforador-petulantemente", u"petunia-pira", u"pirado-pleon", u"pleonasmo-pontonero", u"pont%C3%ADfice-preceder", u"precelente-primate", u"primavera-prosperidad", u"prostaf%C3%A9resis-punterola", u"punter%C3%ADa-quimerino", u"quimerista-ramoneo", u"ramoso-rebuscar", u"rebusco-redova", u"redrar-rejuvenecimiento", u"rej%C3%ADn-repodrir", u"repollar-retardativo", u"retardatorio-ringlero", u"ringorrango-rotario", u"rotativo-sacro", u"sacrosantamente-sangradera", u"sangrado-sede%C3%B1o", u"sedicente-serretazo", u"serrezuela-sincronizaci%C3%B3n", u"sincronizar-sociometr%C3%ADa", u"sociom%C3%A9trico-sosiega", u"sosiego-sulfurado", u"sulfurar-tablado", u"tablaje-taraceador", u"taracear-tempestear", u"tempestivamente-tes%C3%B3n", u"teta-tochedad", u"tochib%C3%AD-toxicog%C3%A9nesis", u"toxicolog%C3%ADa-trasfollado", u"trasfollo-trimensual", u"trimestral-tuna", u"tunal-un%C3%ADvocamente", u"un%C3%ADvoco-varioloso", u"variopinto-vergelero", u"vergeta-virreino", u"virrey-xi", u"xifoideo-zapoyolito", u"zapuyul-"]:
		wikipedia.output(u"Analizando [%s]" % p)
		
		#page=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"%s" % p)
		
		s=wikipedia.Site("es", "wikipedia")
		url=u"/w/index.php?title=%s%s" % (pre, p)
		d=s.getUrl(url)
		
		trozos=d.split("start content")
		trozos=trozos[1].split("end content")
		c=trozos[0]
		
		m=re.compile("class=\"new\"").finditer(c)
		n=re.compile("\"/wiki/").finditer(c)
		rojos=0
		azules=0
		
		for i in m:
				rojos+=1
		tr+=rojos
		
		for i in n:
				azules+=1
		ta+=azules
		
		por=azules*1.0/(rojos+azules)*100
		
		wikipedia.output(u"rojos=%d azules=%d por=%.2f" % (rojos, azules, por))
		
		salida+=u"|%.2f" % (por)

por=ta*1.0/(tr+ta)*100
salida+=u"|%.2f" % (por)
salida+=u"}}"
wi=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Plantilla:ProgresoLemario")
wi.put(salida, u"BOT - Actualizando plantilla %.2f%s" % (por, "%"))
