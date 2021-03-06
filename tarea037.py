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

""" Update popular articles lists """

# TODO: poner una columna para ediciones, otra con el ratio visitas/ediciones
# marcar las protegidas y semiprotegidas con otro color (dorado y gris?)
# hacer que no ocupa mas de 30 caracteres?
#que no cuente las talks
#y las totales a wikimedia?
# poner icono para los current events

import datetime
import gzip
import os
import re
import sys
import time
import urllib
import sets
import random
import codecs

import wikipedia
import pagegenerators

import tareas
import tarea000

#spliter = "\t;;;\t" #tab;tab hay títulos con ; y cosas con tabs individualmente
#spliter = " " #originalmente trae un spliter de espacio, porque no va a funcionar?
limite = 100
langs = []
#las listas de langs deben ser mutuamente excluyentes
#ja: da error de codificación al compactar
test = False
testlangs = ['it', 'pl']
hourly = False
hourlylangs = ['es', 'en', 'de', 'fr', 'pt', 'da', 'eo', 'hu', 'hr', 'it', 
               'pt', 'ro', 'sl', 'th', 'tr', 'ar'] #donde tenga flag
daily = False
dailylangs = ['pl', 'nl', 'ru', 'sv', 'zh', 'no', 
              'ca', 'fi', 'uk', 'cs', 'ko', 'gl', 'mi'] 
              #ir metiendo de mas articulos a menos http://meta.wikimedia.org/wiki/List_of_Wikipedias
#no filtrar paginas con pocas visitas
#con la optimización del código no es necesario
#aunque si filtrar la salida de la tabla y no poner páginas con menos de X visitas
minimum = 100 #aunque de momento no lo uso

if len(sys.argv)>1:
    if sys.argv[1].startswith('--daily'):
        langs += dailylangs
        daily = True
    elif sys.argv[1].startswith('--hourly'):
        langs += hourlylangs
        hourly = True
    elif sys.argv[1].startswith('--test'):
        langs += testlangs
        test = True
    else:
        langs+=[sys.argv[1]]
alllangs = dailylangs + hourlylangs
alllangs.sort()
if len(sys.argv)>2:
    limite = int(sys.argv[2])

exitpages = {
'es': u'Plantilla:Artículos populares',
'default': u'User:Emijrp/Popular articles',
}

f = urllib.urlopen('http://dammit.lt/wikistats/')
raw = f.read()
f.close()
gzs = re.findall(ur'(?i)\"(?P<filename>pagecounts\-\d{8}\-\d{6}\.gz)\"', raw)
#gzs = re.findall(ur'(?i)\"(?P<filename>pagecounts\-20081201\-\d{6}\.gz)\"', raw)
gzs.sort()
if hourly:
    gzs = [gzs[-1]] #nos quedamos con el ultimo que es el mas reciente
elif test:
    gzs = gzs[-2:] #dos ultimos
elif daily:
    gzs = gzs[-24:] #las ultimas 24 horas para las que haya datos
print gzs    
wikipedia.output("Elegidos %d fichero(s)..." % len(gzs))

pagesdic = {}

def unquote(line):
    #strip() para evitar espacios y paginas sin titulo
    #May 29 at 9:27
    #http://stackoverflow.com/questions/2934303/having-encoded-a-unicode-string-in-javascript-how-can-i-decode-it-in-python
    try:
        line=re.sub("%20", "_", line)
        line=urllib.unquote(line.encode("ascii")).decode("utf-8").strip()
    except:
        #mientras encuentro la forma de decodificarlas... false
        return False
        #sys.exit()
    return line

def loadPageTitles(lang):
    try:
        #las redirecciones también nos interesa cogerlas
        #ordeno por touched porque es la fecha en la que el caché se renovó por última vez
        #se supone que las más vistas quedarán en el top de esta query
        #con las pruebas que he hecho, así parece
        print "Metiendo los pagetitles en un fichero... esto puede tardar un poco..."
        os.system(""" mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title from page where page_namespace=0 order by page_touched desc;" > /home/emijrp/temporal/tarea037-%s-pagetitles.txt """ % (lang, lang, lang))
    except:
        print "Error al cargar de la bbdd los pagetitles"
        sys.exit()

def getSoftwareRedirect(lang, page):
    wtitle=page.title()
    filepagetitles="/home/emijrp/temporal/tarea037-%s-pagetitles.txt" % lang
    if not os.path.exists(filepagetitles):
        loadPageTitles(lang)
    try:
        f=codecs.open(filepagetitles, mode="r", encoding="utf-8")
    except:
        print "Error al cargar pagetitles"
        sys.exit()
    l=f.readline()
    if not l: #0 bytes en el fichero?
        f.close()
        loadPageTitles(lang)
        try:
            f=codecs.open(filepagetitles, mode="r", encoding="utf-8")
        except:
            print "Error al cargar pagetitles"
            sys.exit()
    c=0
    while l:
        l=l[:-1]
        c+=1
        if c % 250000 == 0:
            print "lower", c
        if wtitle.strip().lower()==l.strip().lower():
            #sería raro que hubiera dos artículos distintos con diferencia de mayúsculas/minúsculas solo
            #y que uno de ellos fuera muy visitado
            #en el caso que estemos devolviendo una redirección, ya se controla luego que coja el target
            f.close()
            return wikipedia.Page(wikipedia.Site(lang, "wikipedia"), l)
        l=f.readline()
    f.close()
    return page

def compactar():
    for lang in langs:
        f=codecs.open("/home/emijrp/temporal/tarea037-%s-sorted-page.txt" % lang, mode="r", encoding="utf-8")
        g=codecs.open("/home/emijrp/temporal/tarea037-%s-compacted.txt" % lang, mode="w", encoding="utf-8")
        print "Compactando", lang
        pagelang=""
        page=""
        oldpage=None
        times=0
        timessum=0
        other=0
        othersum=0
        for line in f:
            line=line[:-1]
            try:
                pagelang, page, times, other = line.split(" ")
            except:
                print "Error compactando:", line
                sys.exit()
            times = int(times)
            other = int(other)
            if oldpage == None:
                oldpage = page
            if oldpage != page: #hemos cambiado ya de pagina, compactamos la anterior
                output="%s\n" % (" ".join([str(timessum), pagelang, oldpage]))
                g.write(output)
                oldpage = page
                timessum = 0
                othersum = 0
            timessum += times
            othersum += other
        output="%s\n" % (" ".join([str(timessum), pagelang, oldpage]))
        g.write(output)
        f.close();g.close()

def analizarPageViewsLogs():
    totalvisits = {}
    for lang in langs:
        totalvisits[lang]=0
        txtfile='/home/emijrp/temporal/tarea037-%s.txt' % lang
        if os.path.exists(txtfile):
            os.remove(txtfile)
    for gz in gzs:
        print '-'*50, '\n', gz, '\n', '-'*50
        gzpath='/mnt/user-store/stats/%s' % gz
        if not os.path.exists(gzpath):
            #os.system('wget http://dammit.lt/wikistats/%s -O /mnt/user-store/stats/%s' % (gz, gz))
            print "No existe el fichero", gzpath
            sys.exit()
        
        for lang in langs:
            print "Sacando las entradas para %s:" % lang
            #tiene que ser >> para acumular si es un análisis de varias horas (varios gzips)
            #pero antes hay que haberlo borrado para que no se acumule en sucesivas ejecuciones
            os.system('gunzip -c %s | egrep "^%s " >> /home/emijrp/temporal/tarea037-%s.txt' % (gzpath, lang, lang))
    
    for lang in langs:
        descartadas=0
        c=0
        max=0
        max2=""
        print "Haciendo unquote() para", lang
        f=codecs.open("/home/emijrp/temporal/tarea037-%s.txt" % lang, mode="r", encoding="utf-8")
        g=codecs.open("/home/emijrp/temporal/tarea037-%s-capitalized.txt" % lang, mode="w", encoding="utf-8")
        for l in f:
            t=l[:-1].split(" ")
            totalvisits[lang]+=int(t[2])
            if unquote(t[1]):
                tt=[t[0], unquote(t[1]).strip().capitalize(), t[2], t[3]]
                g.write("%s\n" % " ".join(tt))
                c+=1
                if c % 100000 == 0:
                    print "Llevamos", c
            else:
                descartadas+=1
                if max<int(t[2]):
                    max=int(t[2])
                    max2=t[1]
        f.close()
        g.close()
        print "Descartadas", lang, descartadas, "la maxima con", max, "visitas", max2
    return totalvisits

def sortFiles():
    #formato: pagelang pagetitle times other
    for lang in langs:
        os.system("sort /home/emijrp/temporal/tarea037-%s-capitalized.txt > /home/emijrp/temporal/tarea037-%s-sorted-page.txt" % (lang, lang))

def sortByPageViews():
    for lang in langs:
        #no ordena bien si tiene titulos con %D6 y similares?
        print "Ordenando", lang
        os.system("sort -rn /home/emijrp/temporal/tarea037-%s-compacted.txt > /home/emijrp/temporal/tarea037-%s-sorted-times.txt" % (lang, lang))

def main():
    """ Update popular articles lists """
    
    #excluded namespaces and stuff
    exclusions=['http://', 'Special\:', 'sort[_ ]down\.gif', 'sort[_ ]up\.gif', 'sort[_ ]none\.gif', '\&limit\=']
    for lang in langs:
        for nm in wikipedia.Site(lang, "wikipedia").namespaces():
            exclusions+=[re.sub(" ", "_", "%s\:" % nm),
                         re.sub("_", " ", "%s\:" % nm), #meter urllib.quote?
                        ]
    exclusions_r=re.compile(r'(?im)(%s)' % ("|".join(sets.Set(exclusions))))
    
    wikipedia.output("Se van a analizar los idiomas: %s" % ', '.join(langs))
    totalvisits = analizarPageViewsLogs();#print totalvisits
    sortFiles() #gnu sort
    compactar()
    sortByPageViews() #ordenamos de mas visitas a menos, cada idioma
    
    if test:
        print "Fin de la prueba, chequea los archivos"
        sys.exit()
    
    #leemos las primeras y actualizamos el ranking
    for lang in langs:
        if tarea000.isExcluded('tarea037', 'wikipedia', lang):
                continue
        print '-'*50, '\n', lang.upper(), '\n', '-'*50
        f=codecs.open("/home/emijrp/temporal/tarea037-%s-sorted-times.txt" % lang, mode="r", encoding="utf-8")
        pageselection=[]
        pagesiter=[]
        
        for line in f:
            line = line[:-1]
            times, pagelang, page=line.split(" ")
            if len(pagesiter)<limite*5: #margen de error, pueden no existir las paginas, aunque seria raro
                if page=='' or re.search(exclusions_r, page):
                    continue
                else:
                    pageselection.append([page, times])
                    pagesiter.append(page)
            else:
                break
        f.close()
        print "Elegidas", len(pageselection), "candidatas"
        if len(pagesiter)<limite:
            print "Hay menos de %d, que ha pasado? Siguiente wikipedia" % len(pagesiter)
            continue
        
        exitpage=u""
        if exitpages.has_key(lang):
            exitpage=exitpages[lang]
        else:
            exitpage=exitpages["default"]
        salida=u""
        
        projsite=wikipedia.Site(lang, 'wikipedia')
        watch=u'<div style="float: right;"><small>&#91;[[Special:RecentChangesLinked/{{FULLPAGENAME}}|watch popular articles]]&#93;</small></div>'
        intro=u"This page was generated at '''{{subst:#time:Y-m-d H:i}} (UTC)'''.\n\nTotal hits to [{{subst:SERVER}} {{subst:SERVERNAME}}] (including all pages): {{formatnum:%d}}.\n\n[[File:Padlock.svg|20px|Full protected]] = Full protected, [[File:Padlock-silver.svg|20px|Semi-protected]] = Semi-protected.\n\nSource: [http://dammit.lt/wikistats dammit.lt/wikistats]. More page views statistics: [http://stats.wikimedia.org/EN/TablesPageViewsMonthly.htm stats.wikimedia.org] and [http://stats.grok.se stats.grok.se].\n\n" % (totalvisits[lang])
        table=u"{| class=\"wikitable sortable\" style=\"text-align: center;\" \n! # !! Article !! Hits "
        if lang=='es':
            salida=u"<noinclude>{{%s/begin|{{subst:CURRENTHOUR}}}}</noinclude>\n{| class=\"wikitable sortable\" style=\"text-align: center;\" width=350px \n|+ [[Plantilla:Artículos populares|Artículos populares]] en la última hora \n! # !! Artículo !! Visitas " % exitpage
        else:
            if hourly:
                #decir que hora es analizada
                gzhour=gzs[0][20:22]
                hour=(datetime.datetime(year=2000, month=1, day=1, hour=int(gzhour))-datetime.timedelta(hours=1)).hour #calcular la hora anterior, la ant a 0 es 23
                hour_=str(hour)
                if hour<10:
                    hour_='0'+hour_
                map=u'[[File:Daylight_Map,_nonscientific_(%s00_UTC).jpg|thumb|Daylight map, %s:00 (UTC)]]' % (hour_, hour_)
                salida+=watch+"\n"+map+"\n"
                salida+=u"Last hour '''popular articles''' (Period: '''%s:00–%s:59 (UTC)'''). %s%s" % (hour_, hour_, intro, table)
            else:
                #decir a que periodo de 24 horas se refiere el análisis
                gzhour1=gzs[0][20:22]
                hour1=(datetime.datetime(year=2000, month=1, day=1, hour=int(gzhour1))-datetime.timedelta(hours=1)).hour
                hour1_=str(hour1)
                if hour1<10:
                    hour1_='0'+hour1_
                gzhour2=gzs[-1][20:22]
                hour2=(datetime.datetime(year=2000, month=1, day=1, hour=int(gzhour2))-datetime.timedelta(hours=1)).hour
                hour2_=str(hour2)
                if hour2<10:
                    hour2_='0'+hour2_
                salida+=watch+"\n"
                salida+=u"Last 24 hours '''popular articles''' (Period: '''%s:00–%s:59 (UTC)'''). %s%s" % (hour1_, hour2_, intro, table)

        #for p in pagesiter: #para ver que pagina fallaba con la codificación
        #    print p
        #    pp=wikipedia.Page(projsite, p)
            
        try:
            gen=pagegenerators.PagesFromTitlesGenerator(pagesiter, projsite)
        except:
            print "Error en la codificacion seguramente", lang
            continue
        pre=pagegenerators.PreloadingGenerator(gen, pageNumber=limite*2, lookahead=100)
        c=d=ind=0
        sum=0
        for page in pre:
            detalles=u''
            if not page.exists():
                #si la página no existe es porque es una redirección por software (mediawiki)
                #o porque la han borrado o nunca existió... algún DDoS loco...
                #algunos ejemplos...
                #Recovery (Eminem album)
                #Glee (TV series)
                #PubMed Identifier
                try:
                    wikipedia.output(u"No existe? %s" % page.title())
                except:
                    print "No existe"
                page=getSoftwareRedirect(lang, page)
                r=0
                while page.exists() and page.isRedirectPage():
                    r+=1
                    page=page.getRedirectTarget()
                    if r>5: #what?
                        break
                if not page.exists():
                    #sayonara baby, ddos, loco?
                    continue
            if page.exists() and page.namespace()==0:
                c+=1
                sum+=int(pageselection[ind][1])
                if c>limite:
                    break
                
                #debe ser lo primero que se añada a detalles, para que el candado salga junto al título
                locks=page.getRestrictions()
                #formato de locks
                #{u'edit': None, 'move': None}
                #{u'edit': [u'autoconfirmed', u'2010-09-10T20:08:39Z']}
                #{u'edit': [u'autoconfirmed', u'infinity'], u'move': [u'autoconfirmed', u'infinity']}
                if locks.has_key("edit") and locks["edit"]:
                    if locks["edit"][0]=="autoconfirmed":
                        detalles+=u'[[File:Padlock-silver.svg|15px|Semi-protected]] '
                    elif locks["edit"][0]=="sysop":
                        detalles+=u'[[File:Padlock.svg|15px|Full-protected]] '
                
                wtitle=page.title()
                page2=page #para coger el redirecttarget si es redirect, se usa más abajo también para los interwikis
                if page.isRedirectPage():
                    page2=page.getRedirectTarget()
                    detalles+=u' (#REDIRECT [[%s]]) ' % (page2.title())
                elif page.isDisambig():
                    #detalles+=u'(Desambiguación) '
                    pass #para evitar no ponerlo en el idioma loal
                else:
                    pass
                    #tmpget=page.get()
                    #if re.search(ur'(?i)\{\{ *Artículo bueno', tmpget):
                    #    detalles+='[[Image:Artículo bueno.svg|14px|Artículo bueno]]'
                    #if re.search(ur'(?i)\{\{ *(Artículo destacado|Zvezdica)', tmpget):
                    #    detalles+='[[Image:Cscr-featured.svg|14px|Featured article]]'
                    #if re.search(ur'(?i)\{\{ *(Semiprotegida2?|Semiprotegido|Pp-semi-template)', tmpget):
                    #    detalles+='[[Image:Padlock-silver-medium.svg|20px|Semiprotegida]]'
                    #if re.search(ur'(?i)\{\{ *(Protegida|Protegido|Pp-template)', tmpget):
                    #    detalles+='[[Image:Padlock.svg|20px|Protegida]]'
                #wikipedia.output('%s - %d - %s' % (wtitle, visits, detalles))
                #continue
                
                #quitamos enlaces a #secciones y nos quedamos con la primera parte
                wtitle=wtitle.split("#")[0]
                
                if page.namespace() in [6, 14]:
                    wtitle=u':%s' % wtitle
                
                if lang=='es':
                    if c-1 in [3,5,10,15,20]:
                        salida+=u"\n{{#ifexpr:{{{top|15}}} > %d|" % (c-1)
                        d+=1
                    salida+=u"\n{{!}}-\n{{!}} %d {{!}}{{!}} [[%s]]%s{{#if:{{{novistas|}}}||{{!}}{{!}} {{formatnum:%s}}}} " % (c, wtitle, detalles, pageselection[ind][1])
                else:
                    #english interwiki <sup>
                    iwlink=""
                    if lang!="en":
                        #a veces falla al cargar iws vacios de portadas del tipo [[cs:]]
                        # puede haber una excepción SectionError, entre otras
                        try: 
                            iws=page2.interwiki()
                            for iw in iws:
                                if iwlink=='' and iw.site().lang=="en":
                                    iwlink=" <sup>([[:en:%s|en]])</sup>" % (iw.title())
                        except:
                            pass
                    salida+=u"\n|-\n| %d || [[%s]]%s%s || {{formatnum:%s}} " % (c, wtitle, detalles, iwlink, pageselection[ind][1])
                
                #except:
                #    wikipedia.output(u'Error al generar item en lista de %s:' % lang)
            ind+=1 #se incrementa siempre, para que no se desplace la columna de visitas, no ponerlo al principio, empieza en 0
        
        iws=u''
        for iw in alllangs:
            if iw!=lang:
                if exitpages.has_key(iw):
                    iws+=u'[[%s:%s]]\n' % (iw, exitpages[iw])
                else:
                    iws+=u'[[%s:%s]]\n' % (iw, exitpages["default"])
        #salida+="\n{{/end}}\n%s" % (iws)
        if lang=='es':
            salida+=u"\n%s\n{{%s/end|%d|%d|top={{{top|15}}}|fecha={{subst:CURRENTTIME}} ([[UTC]]) del {{subst:CURRENTDAY2}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}}}}\n|}\n<noinclude>{{documentación}}\n%s</noinclude>" % ("}} "*d, exitpage, sum, totalvisits[lang], iws)
        else:
            salida+=u"\n|-\n| &nbsp; || '''Top %d hit sum''' || '''{{formatnum:%d}}''' \n|}\n\n%s" % (limite, sum, iws)
        #wikipedia.output(re.sub(ur"\n", ur" ", salida))
        if len(salida)>3000:
            wiii=wikipedia.Page(projsite, exitpage)
            #wiii.put(salida, u'BOT - Updating list')
        else:
            print "Error pagina menor de 3KB, fallo algo"
        os.system("rm /home/emijrp/temporal/tarea037-%s.txt" % lang)
        os.system("rm /home/emijrp/temporal/tarea037-%s-compacted.txt" % lang)
        os.system("rm /home/emijrp/temporal/tarea037-%s-sorted-page.txt" % lang)
        #os.system("rm /home/emijrp/temporal/tarea037-%s-sorted-times.txt" % lang)
        if not random.randint(0,9) or daily:
            #lo renovamos cada 10 ejecuciones más o menos si es el ranking por horas y siempre si es el diario
            filepagetitles="/home/emijrp/temporal/tarea037-%s-pagetitles.txt" % lang
            #a lo mejor no se creó porque no hizo falta
            if os.path.exists(filepagetitles):
                os.remove(filepagetitles)

if __name__ == "__main__":
    main()
    
