# -*- coding: utf-8 -*-

from __future__ import generators
import sys, re
import wikipedia, pagegenerators,catlib, config,time, thread


pre=u"Usuario:Platonides/Encarta/"

salida=u"{{subst:ProgresoEncarta/subst"

tr=0
ta=0

for p in [u"M%C3%BAsica", u"Compositores_e_int%C3%A9rpretes", u"Tauromaquia", u"M%C3%BAsica._Artes_esc%C3%A9nicas._Espect%C3%A1culos/Cine%2C_Radio_y_televisi%C3%B3n", u"Teatro", u"Danza", u"Instrumentos_musicales", u"Econom%C3%ADa", u"Antropolog%C3%ADa", u"Psicolog%C3%ADa", u"Sociolog%C3%ADa", u"Organizaciones", u"Instituciones", u"Ciencia_pol%C3%ADtica", u"Ej%C3%A9rcito", u"Derecho", u"Educaci%C3%B3n", u"Calendarios_y_fiestas", u"Escritores", u"Pintura._Dibujo._Artes_gr%C3%A1ficas", u"Artistas", u"Literatura", u"Cuentos_y_leyendas", u"Literaturas_nacionales", u"Artes_nacionales_y_regionales", u"Artes_decorativas", u"Arquitectura_y_monumentos", u"Lenguaje", u"Movimientos_y_estilos", u"Fotograf%C3%ADa", u"Escultura", u"Divisiones_administrativas", u"Relieve", u"Poblaciones_del_mundo", u"Parques_y_reservas_naturales", u"Regiones_naturales_e_hist%C3%B3ricas", u"Islas_y_archipi%C3%A9lagos", u"R%C3%ADos%2C_lagos_y_canales", u"Pa%C3%ADses", u"Oc%C3%A9anos_y_mares", u"Conceptos_geogr%C3%A1ficos", u"Exploradores_y_descubridores", u"Cartograf%C3%ADa", u"Personajes_de_la_Historia", u"Europa_Contempor%C3%A1nea", u"El_mundo_desde_1945", u"Europa_Antigua", u"Europa_Moderna", u"Latinoam%C3%A9rica:_periodo_colonial", u"Europa_Medieval", u"%C3%81frica_y_Pr%C3%B3ximo_Oriente", u"Asia_y_Ocean%C3%ADa", u"Estados_Unidos_y_Canad%C3%A1", u"Arqueolog%C3%ADa_y_Prehistoria", u"Latinoam%C3%A9rica:_desde_la_Independencia", u"Latinoam%C3%A9rica:_periodo_precolombino", u"Principios_y_conceptos_biol%C3%B3gicos", u"Reptiles_y_anfibios", u"Biograf%C3%ADas:_Ciencias_de_la_vida", u"Anatom%C3%ADa._Fisiolog%C3%ADa", u"Plantas", u"Aves", u"Medicina", u"Medio_ambiente", u"Virus%2C_m%C3%B3neras_y_protistas", u"Invertebrados", u"Peces", u"Mam%C3%ADferos", u"Ciencias_de_la_Tierra", u"Agricultura%2C_alimentaci%C3%B3n_y_ganader%C3%ADa", u"Algas_y_hongos", u"Paleontolog%C3%ADa", u"Metrolog%C3%ADa", u"Tecnolog%C3%ADa_militar", u"Qu%C3%ADmica", u"Biograf%C3%ADas", u"Matem%C3%A1ticas", u"F%C3%ADsica", u"Electr%C3%B3nica._Inform%C3%A1tica", u"Ingenier%C3%ADa_y_construcci%C3%B3n", u"Astronom%C3%ADa._Ciencias_del_espacio", u"Comunicaciones", u"Transportes", u"Industria_y_recursos_naturales", u"M%C3%A1quinas_y_herramientas", u"Mitolog%C3%ADa", u"Filosof%C3%ADa", u"Figuras_religiosas", u"Ocultismo", u"Religiones._Grupos_religiosos", u"Teolog%C3%ADa", u"Textos_sagrados", u"Deportistas", u"Deportes_y_juegos", u"Animales_de_compa%C3%B1%C3%ADa", u"Aficiones"]:
        wikipedia.output(u"Analizando [%s]" % p)
        
        #page=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"%s" % p)
        
        s=wikipedia.Site("es", "wikipedia")
        url=u"/w/index.php?title=%s%s" % (pre, p)
        d=s.getUrl(url)
        
        trozos=d.split("start content")
        trozos=trozos[1].split("end content")
        c=trozos[0]
        
        m=re.compile("class=\"new\"").finditer(c)
        n=re.compile("/wiki/").finditer(c)
        rojos=0
        azules=-1
        
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
salida+=u"}}<noinclude>{{documentación de plantilla}}</noinclude>"
wi=wikipedia.Page(wikipedia.Site("es", "wikipedia"), u"Plantilla:ProgresoEncarta")
wi.put(salida, u"BOT - Actualizando plantilla %.2f%s" % (por, "%"))
