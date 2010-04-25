#!/usr/bin/env python
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

""" Update a words progress template """

from __future__ import generators
import re
import urllib

import wikipedia

projects = {
'wikipedia': 
  {'es': {'prefix': "Usuario:Emijrp/MiPortal/Lemario/", 
          'footer': "<noinclude>{{documentación de plantilla}}</noinclude>"}
  },
'wiktionary':
  {'es': {'prefix': "Wikcionario:Apéndice:Lemario/",
          'footer': ""}
  }
}
             
def main():
    """ Update a words progress template """
    
    for family, langs in projects.items():
        for lang, preferences in langs.items():
            wiki = wikipedia.Site(lang, family)
            suffixes = ["a-absolver", "absorbencia-achicadura", 
                        "achicamiento-acullicar", "acullico-aeromotor", 
                        "aeromoza-agravación", "agravador-ajimezado", 
                        "ajipa-alcantarillar", "alcantarillero-alhorra", 
                        "alhorre-aloja", "alojado-ambientar", 
                        "ambiente-anatomopatológico", 
                        "anatomopatólogo-antecapilla", 
                        "antecedencia-apaleador", "apaleamiento-apresto", 
                        "apresura-argelino", "argemone-arrinconar", 
                        "arriostrar-asistimiento", "asistir-atisuado", 
                        "atizacandiles-avance", "avandicho-ábsida", 
                        "ábside-balotaje", "balotar-basilisco", 
                        "basis-besalamano", "besamanos-blandón", 
                        "blanqueación-borneadizo", "borneadura-broquelazo",
                        "broquelero-cabalgar", "cabalgata-cajo", 
                        "cajonada-camachuelo", "camada-canijo", 
                        "canil-carapachay", "carapacho-carraña", 
                        "carrañaca-catascopio", "catasta-cedrito", 
                        "cedro-ceroferario", "ceroleína-chape", 
                        "chapeado-chipojo", "chipolo-churumen", "churumo-cirio",
                        "cirolero-cochama", "cochambre-colofonita", 
                        "colofonía-compuerta", 
                        "compuestamente-congelativo", "congenial-continuidad", 
                        "continuismo-copiar", "copichuela-corruco", 
                        "corrugación-criadero", "criadilla-cuatrín", 
                        "cuatí-curtimiento", "curtir-decadente", 
                        "decadentismo-demográfico", "demoledor-desairar", 
                        "desaire-descargamiento", "descargar-desenastar", 
                        "desencabalgado-desimponer", "desimpresionar-despego", 
                        "despegue-desvergonzado", "desvergonzarse-dignificar", 
                        "digno-disyuntiva", "disyuntivamente-dubitativo", 
                        "ducado-ejemplo", "ejercer-embrisar", 
                        "embriólogo-enardecedor", "enardecer-encostradura",
                        "encostrar-engranerar", "engranujarse-enseño", 
                        "enseñoramiento-envejecido", 
                        "envejecimiento-escalfecerse", "escalfeta-escuadreo", 
                        "escuadrilla-esperteza", "esperón-estelado", 
                        "estelar-estúpidamente", 
                        "estúpido-expedienteo", "expedir-falciforme", 
                        "falcinelo-ferial", "feriante-fitográfico", 
                        "fitolacáceo-fornicar", "fornicario-frotador", 
                        "frotadura-galancete", "galanga-garrobal", 
                        "garrobilla-ginefobia", "ginesta-granadí", 
                        "granalla-guaquero", "guara-güimba", 
                        "güin-hemograma", "hemolisina-hilandería", 
                        "hilanza-hontanal", "hontanar-húmico", 
                        "húmido-impresionar", "impresionismo-incumplir", 
                        "incunable-infrasonido", 
                        "infrautilización-institucionalización", 
                        "institucionalizar-inventación", 
                        "inventador-jactancioso", "jactar-jubetería", 
                        "jubilación-lagrimeo", "lagrimoso-lebulense", 
                        "lecanomancia-lidio", "lidioso-loanda", 
                        "loanza-lúcidamente", "lúcido-malaleche", 
                        "malambo-manifestador", "manifestante-marqueta", 
                        "marquetería-mecedor", "mecedura-mercadero", 
                        "mercadería-miligramo", "mililitro-moharrache", 
                        "moharracho-morcillo", "morcillón-mundanalidad", 
                        "mundanamente-Leiden", "Leo-nefrosis", 
                        "nefrítico-nonada", "nonagenario-obsidional", 
                        "obsolescencia-onerario", "oneroso-ostrogodo", 
                        "ostrícola-pallar", "pallas-paraliticado", 
                        "paraliticarse-pastoría", "pastosidad-peindra", 
                        "peine-perforación", "perforador-petulantemente", 
                        "petunia-pira", "pirado-pleon", "pleonasmo-pontonero", 
                        "pontífice-preceder", "precelente-primate", 
                        "primavera-prosperidad", "prostaféresis-punterola",
                        "puntería-quimerino", "quimerista-ramoneo", 
                        "ramoso-rebuscar", "rebusco-redova", 
                        "redrar-rejuvenecimiento", "rejín-repodrir", 
                        "repollar-retardativo", "retardatorio-ringlero", 
                        "ringorrango-rotario", "rotativo-sacro", 
                        "sacrosantamente-sangradera", "sangrado-sedeño", 
                        "sedicente-serretazo", "serrezuela-sincronización",
                        "sincronizar-sociometría", 
                        "sociométrico-sosiega", "sosiego-sulfurado", 
                        "sulfurar-tablado", "tablaje-taraceador", 
                        "taracear-tempestear", "tempestivamente-tesón", 
                        "teta-tochedad", "tochibí-toxicogénesis", 
                        "toxicología-trasfollado", "trasfollo-trimensual", 
                        "trimestral-tuna", "tunal-unívocamente", 
                        "unívoco-varioloso", "variopinto-vergelero", 
                        "vergeta-virreino", "virrey-xi", "xifoideo-zapoyolito", 
                        "zapuyul-"]
            output = u"{{subst:ProgresoLemario/subst"
            totalred = 0
            totalblue = 0
             
            for suffix in suffixes:
                wikipedia.output("Analizando [%s]" % suffix)
                
                url = "/w/index.php?title=%s%s" % (preferences['prefix'], urllib.quote(suffix))
                raw = wiki.getUrl(url)        
                raw = raw.split("start content")[1].split("end content")[0]
                
                red = len(re.findall('class="new"', raw))
                blue = len(re.findall('"/wiki/', raw))
                totalred += red
                totalblue += blue
                percent = blue * 1.0 / (red + blue) * 100
                
                wikipedia.output("%d redlinks, %d blue links, %.2f percent \
                                  (red links)" % (red, blue, percent))
                output += u"|%.2f" % (percent)

            percent = totalblue * 1.0 / (totalred + totalblue) * 100
            output += u"|%.2f" % (percent)
            output += u"}}%s" % (preferences['footer'])
            page = wikipedia.Page(wiki, "Plantilla:ProgresoLemario")
            page.put(output, "BOT - Actualizando plantilla %.2f%%" % (percent))

if __name__ == "__main__":
    main()
