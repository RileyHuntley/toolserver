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

""" Update a Encarta progress template """

from __future__ import generators
import re
import urllib

import wikipedia

def main():
    """ Update a Encarta progress template """
    
    wikies = wikipedia.Site("es", "wikipedia")
    prefix = "Usuario:Platonides/Encarta/"
    suffixes = ["Música", "Compositores_e_intérpretes", "Tauromaquia", 
                "Música._Artes_escénicas._Espectáculos/Cine,_Radio_y_\
                televisión", "Teatro", "Danza", 
                "Instrumentos_musicales", "Economía",
                "Antropología", "Psicología", "Sociología", 
                "Organizaciones", "Instituciones", "Ciencia_política", 
                "Ejército", "Derecho", "Educación", 
                "Calendarios_y_fiestas", "Escritores", 
                "Pintura._Dibujo._Artes_gráficas", "Artistas", 
                "Literatura", "Cuentos_y_leyendas", 
                "Literaturas_nacionales", 
                "Artes_nacionales_y_regionales", "Artes_decorativas", 
                "Arquitectura_y_monumentos", 
                "Lenguaje", "Movimientos_y_estilos", "Fotografía", 
                "Escultura", "Divisiones_administrativas", "Relieve", 
                "Poblaciones_del_mundo", "Parques_y_reservas_naturales",
                "Regiones_naturales_e_históricas", 
                "Islas_y_archipiélagos", "Ríos,_lagos_y_canales", 
                "Países", "Océanos_y_mares", "Conceptos_geográficos", 
                "Exploradores_y_descubridores", "Cartografía", 
                "Personajes_de_la_Historia", "Europa_Contemporánea", 
                "El_mundo_desde_1945", "Europa_Antigua", 
                "Europa_Moderna", "Latinoamérica:_periodo_colonial", 
                "Europa_Medieval", "África_y_Próximo_Oriente", 
                "Asia_y_Oceanía", "Estados_Unidos_y_Canadá", 
                "Arqueología_y_Prehistoria", 
                "Latinoamérica:_desde_la_Independencia", 
                "Latinoamérica:_periodo_precolombino", 
                "Principios_y_conceptos_biológicos", 
                "Reptiles_y_anfibios", 
                "Biografías:_Ciencias_de_la_vida", 
                "Anatomía._Fisiología", "Plantas", "Aves", "Medicina", 
                "Medio_ambiente", "Virus,_móneras_y_protistas", 
                "Invertebrados", "Peces", "Mamíferos", 
                "Ciencias_de_la_Tierra", 
                "Agricultura,_alimentación_y_ganadería", 
                "Algas_y_hongos", "Paleontología", "Metrología", 
                "Tecnología_militar", "Química", "Biografías", 
                "Matemáticas", "Física", "Electrónica._Informática", 
                "Ingeniería_y_construcción",
                "Astronomía._Ciencias_del_espacio", "Comunicaciones", 
                "Transportes", "Industria_y_recursos_naturales", 
                "Máquinas_y_herramientas", "Mitología", "Filosofía", 
                "Figuras_religiosas", "Ocultismo", 
                "Religiones._Grupos_religiosos", "Teología", 
                "Textos_sagrados", "Deportistas", "Deportes_y_juegos", 
                "Animales_de_compañía", "Aficiones"]
    output = u"{{subst:ProgresoEncarta/subst"
    totalred = 0
    totalblue = 0

    for suffix in suffixes:
        wikipedia.output("Analizando [%s]" % suffix)
        
        url = "/w/index.php?title=%s%s" % (prefix, urllib.quote(suffix))
        raw = wikies.getUrl(url)
        raw = raw.split("start content")[1].split("end content")[0]
        
        red = len(re.findall('class="new"', raw))
        blue = len(re.findall('/wiki/', raw))-1
        
        totalred += red
        totalblue += blue
        percent = blue * 1.0 / (red + blue) * 100
        
        wikipedia.output("%d redlinks, %d blue links, %.2f percent \
                          (red links)" % (red, blue, percent))
        output += u"|%.2f" % (percent)

    percent = totalblue * 1.0 / (totalred + totalblue) * 100
    output += u"|%.2f" % (percent)
    output += u"}}<noinclude>{{documentación de plantilla}}</noinclude>"
    page = wikipedia.Page(wikies, "Plantilla:ProgresoEncarta")
    page.put(output, "BOT - Actualizando plantilla %.2f%%" % (percent))

if __name__ == "__main__":
    main()
