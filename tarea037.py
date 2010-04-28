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

import datetime
import gzip
import os
import re
import sys
import time
import urllib

import wikipedia
import pagegenerators

import tareas
import tarea000

#TODO
#que no cuente las talks
#y las totales a wikimedia?

limite = 100
langs = []
hourly = False
hourlylangs = ['es', 'en', 'de', 'fr', 'pt', 'da', 'eo', 'hu', 'hr', 
               'ro', 'sl', 'th', 'tr'] #donde tenga flag
daily = False
dailylangs = ['it', 'ja', 'pl', 'nl', 'ru', 'sv', 'zh', 'no', 
              'ca', 'fi', 'uk', 'cs', 'ko', 'da', 'id', 'vi', 
              'sk', 'sr', 'lt', 'he',
              'gl'] #volapuk no mientras no tenga flag, tienen pocas ediciones al dia
              #ir metiendo de mas articulos a menos http://meta.wikimedia.org/wiki/List_of_Wikipedias
                      
minimum = 5 #visitas minimas para ser contabilizada la pagina, para rankings de la última hora
if len(sys.argv)>1:
    if sys.argv[1].startswith('--daily'):
        langs += dailylangs
        daily = True
    elif sys.argv[1].startswith('--hourly'):
        langs += hourlylangs
        hourly = True
    else:
        langs+=[sys.argv[1]]
alllangs = dailylangs + hourlylangs
alllangs.sort()
if len(sys.argv)>2:
    limite = int(sys.argv[2])

commonexitpage = u'User:Emijrp/Popular articles'
exitpages = {
'es': u'Plantilla:Artículos populares',
}

f = urllib.urlopen('http://dammit.lt/wikistats/')
raw = f.read()
f.close()
gzs = re.findall(ur'(?i)\"(?P<filename>pagecounts\-\d{8}\-\d{6}\.gz)\"', raw)
#gzs = re.findall(ur'(?i)\"(?P<filename>pagecounts\-20081201\-\d{6}\.gz)\"', raw)
gzs.sort()
if hourly:
    gzs = [gzs[-1]] #nos quedamos con el ultimo que es el mas reciente
    #gzs = gzs[-2:] #los dos ultimos, para pruebas
elif daily:
    gzs = gzs[-24:] #las ultimas 24 horas para las que haya datos
print gzs    
wikipedia.output("Elegidos %d fichero(s)..." % len(gzs))

pagesdic = {}
namespaceslists = {}
exceptions = {}

def main():
    spliter = "\t" #tab
    fs={}
    for lang in langs:
        lang = lang.lower()
        namespaceslists[lang] = tareas.getNamespacesList(wikipedia.Site(lang, 'wikipedia'))
        exceptions[lang] = {}
        exceptions[lang]['regexp'] = ur'(?i)(%s)\:' % ('|'.join(namespaceslists[lang]))
        exceptions[lang]['compiled'] = re.compile(exceptions[lang]['regexp'])
        fs[lang]=open("/home/emijrp/temporal/tarea037-%s.txt" % lang, "w")
        
    wikipedia.output("Se van a analizar los idiomas: %s" % ', '.join(langs))
    for lang in langs:
        wikipedia.output("Excepciones de %s: %s" % (lang, exceptions[lang]['regexp']))
    
    totalvisits = {}
    for gz in gzs:
        print '-'*50, '\n', gz, '\n', '-'*50
        try:
            f = gzip.open('/mnt/user-store/stats/%s' % gz, 'r')
        except:
            #os.system('wget http://dammit.lt/wikistats/%s -O /mnt/user-store/stats/%s' % (gz, gz))
            #f=gzip.open('/mnt/user-store/stats/%s' % gz, 'r')
            sys.exit()
        
        #regex=re.compile(ur'(?im)^([a-z]{2}) (.*?) (\d{1,}) (\d{1,})$') #evitamos aa.b
        regexp = re.compile(r'(?im)^(?P<pagelang>%s) (?P<page>.+) (?P<times>\d{1,}) (?P<other>\d{1,})$' % '|'.join(langs)) #evitamos aa.b
        
        c = 0
        analized = 0
        errores = 0
        for line in f:
            line = line[:len(line)-1]
            try:
                line = line.encode('utf-8')
                line = urllib.unquote(line)
            except:
                try:
                    line = urllib.unquote(line)
                except:
                    print "Error", wikipedia.output(line)
                    errores += 1
                    continue
            c+=1
            if c % 100000 == 0:
                print "Leidas %d lineas (%d analizadas, %d fallos)" % (c, analized, errores)
                
            m = regexp.finditer(line)
            for i in m:
                pagelang = i.group('pagelang').lower()
                page = re.sub('_', ' ', i.group('page')).strip()
                if not page:
                    continue
                times = int(i.group('times'))
                other = int(i.group('other'))
                
                if not totalvisits.has_key(pagelang): #debe ir antes la exclusión, para contarlas todas
                    totalvisits[pagelang] = times
                else:
                    totalvisits[pagelang] += times
                
                if re.search(exceptions[pagelang]['compiled'], page):
                    continue
                
                if hourly and times < minimum: #si hago el diario, no descartar nada...
                    continue
                
                #guardamos
                fs[pagelang].write("%s\t%s\t%s\n" % (pagelang, page, times))
                analized += 1
        f.close()
    
    for lang, f, in fs.items(): #cerramos
        f.close()
    
    #ordenamos con GNU sort
    for lang in langs:
        os.system("sort /home/emijrp/temporal/tarea037-%s.txt > /home/emijrp/temporal/tarea037-%s-sorted-page.txt" % (lang, lang))
        #os.system("rm /home/emijrp/temporal/tarea037-%s.txt" % lang)
    
    #compactamos
    for lang in langs:
        f=open("/home/emijrp/temporal/tarea037-%s-sorted-page.txt" % lang, "r")
        g=open("/home/emijrp/temporal/tarea037-%s-compacted.txt" % lang, "w")
        print "Compactando", lang
        pagelang=""
        page=""
        oldpage=""
        timessum=0
        for line in f:
            #line=unicode(line, "utf-8")
            [pagelang, page, times] = line[:-1].split(spliter)
            times = int(times)
            if not oldpage:
                oldpage = page
            if oldpage != page: #hemos cambiado ya de pagina, compactamos la anterior
                g.write("%s\t%s\t%s\n" % (timessum, pagelang, oldpage))
                oldpage = page
                timessum = 0
            timessum += times
        g.write("%s\t%s\t%s\n" % (timessum, pagelang, page))
        f.close()
        g.close()
        #os.system("rm /home/emijrp/temporal/tarea037-%s-sorted-page.txt" % lang)
    
    #ordenamos de mas visitas a menos, cada idioma
    for lang in langs:
        print "Ordenando", lang
        os.system("sort -rg /home/emijrp/temporal/tarea037-%s-compacted.txt > /home/emijrp/temporal/tarea037-%s-sorted-times.txt" % (lang, lang))
    
    #leemos las primeras y actualizamos el ranking
    for lang in langs:
        if tarea000.isExcluded('tarea037', 'wikipedia', lang):
                continue
        print '-'*50, '\n', lang.upper(), '\n', '-'*50
        f=open("/home/emijrp/temporal/tarea037-%s-sorted-times.txt" % lang, "r")
        pageselection=[]
        pagesiter=[]
        
        c=0
        errores=0
        for line in f:
            line = line[:len(line)-1]
            [times, pagelang, page]=line.split(spliter)
            if re.search(ur'(?im)(http://|Special\:|sort_down\.gif|sort_up\.gif|sort_none\.gif|\&limit\=)', page):
                #ampliar con otros idiomas
                continue
            c+=1
            if c<=limite*2: #margen de error, pueden no existir las paginas, aunque seria raro
                page=re.sub("%20", " ", urllib.quote(page))
                pageselection.append([page, times])
                pagesiter.append(page)
            else:
                break
        f.close()
        print "Elegidas", len(pageselection), "candidatas, hubo", errores, "errores"
        
        exitpage=u""
        if exitpages.has_key(lang):
            exitpage=exitpages[lang]
        else:
            exitpage=commonexitpage
        salida=u""
        
        projsite=wikipedia.Site(lang, 'wikipedia')
        watch=u'<div style="float: right;"><small>&#91;[[Special:RecentChangesLinked/{{FULLPAGENAME}}|watch popular articles]]&#93;</small></div>'
        map=u'[[File:Daylight_Map,_nonscientific_({{subst:CURRENTHOUR}}00_UTC).jpg|thumb|Daylight map, {{subst:CURRENTHOUR}}:00 UTC]]'
        if lang=='es':
            salida=u"<noinclude>{{%s/begin|{{subst:CURRENTHOUR}}}}</noinclude>\n{| class=\"wikitable sortable\" style=\"text-align: center;\" width=350px \n|+ [[Plantilla:Artículos populares|Artículos populares]] en la última hora \n! # !! Artículo !! Visitas " % exitpage
        else:
            if hourly:
                salida+=watch+"\n"+map+"\n"
                salida+=u"Last hour popular articles. This page was last updated at '''{{subst:CURRENTYEAR}}-{{subst:CURRENTMONTH}}-{{subst:CURRENTDAY2}} {{subst:CURRENTTIME}} (UTC)'''.\n\nTotal hits to {{subst:SERVER}} (including all pages): {{formatnum:%d}}.\n\nSource: http://dammit.lt/wikistats\n\n{| class=\"wikitable sortable\" style=\"text-align: center;\" \n! # !! Article !! Hits " % (totalvisits[lang])
            else:
                salida+=watch+"\n"
                salida+=u"Last 24 hours popular articles. This page was last updated at '''{{subst:CURRENTYEAR}}-{{subst:CURRENTMONTH}}-{{subst:CURRENTDAY2}} {{subst:CURRENTTIME}} (UTC)'''.\n\nTotal hits to {{subst:SERVER}} (including all pages): {{formatnum:%d}}.\n\nSource: http://dammit.lt/wikistats\n\n{| class=\"wikitable sortable\" style=\"text-align: center;\" \n! # !! Article !! Hits " % (totalvisits[lang])

        #for p in pagesiter: #para ver que pagina fallaba con la codificación
        #    print p
        #    pp=wikipedia.Page(projsite, p)
            
        try:
            gen=pagegenerators.PagesFromTitlesGenerator(pagesiter, projsite)
        except:
            print "Error en la codificacion seguramente", lang
            continue
        pre=pagegenerators.PreloadingGenerator(gen, pageNumber=limite, lookahead=100)
        c=d=0
        sum=0
        ind=-1
        for page in pre:
            detalles=u''
            ind+=1
            if page.exists():
                wtitle=page.title()
                
                if page.isRedirectPage():
                    detalles+=u' (#REDIRECT [[%s]]) ' % (page.getRedirectTarget().title())
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
                
                if page.namespace() in [6, 14]:
                    wtitle=u':%s' % wtitle
                c+=1
                if lang=='es':
                    if c-1 in [3,5,10,15,20]:
                        salida+=u"\n{{#ifexpr:{{{top|15}}} > %d|" % (c-1)
                        d+=1
                    salida+=u"\n{{!}}-\n{{!}} %d {{!}}{{!}} [[%s]]%s{{#if:{{{novistas|}}}||{{!}}{{!}} {{formatnum:%s}}}} " % (c, wtitle, detalles, pageselection[ind][1])
                else:
                    salida+=u"\n|-\n| %d || [[%s]]%s || {{formatnum:%s}} " % (c, wtitle, detalles, pageselection[ind][1])
                sum+=int(pageselection[ind][1])
                
                if c>=limite:
                    break
                #except:
                #    wikipedia.output(u'Error al generar item en lista de %s:' % lang)
        
        iws=u''
        for iw in alllangs:
            if iw!=lang:
                if exitpages.has_key(iw):
                    iws+=u'[[%s:%s]]\n' % (iw, exitpages[iw])
                else:
                    iws+=u'[[%s:%s]]\n' % (iw, commonexitpage)
        #salida+="\n{{/end}}\n%s" % (iws)
        if lang=='es':
            salida+=u"\n%s\n{{%s/end|%d|%d|top={{{top|15}}}|fecha={{subst:CURRENTTIME}} ([[UTC]]) del {{subst:CURRENTDAY2}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}}}}\n|}\n<noinclude>{{documentación de plantilla}}\n%s</noinclude>" % ("}} "*d, exitpage, sum, totalvisits[lang], iws)
        else:
            salida+=u"\n|-\n| colspan=3 align=right | ''Top %d hit sum: '''{{formatnum:%d}}'''''&nbsp;&nbsp; \n|}\n\n%s" % (limite, sum, iws)
        wikipedia.output(re.sub(ur"\n", ur" ", salida))
        wiii=wikipedia.Page(projsite, exitpage)
        wiii.put(salida, u'BOT - Updating list')
        
        os.system("rm /home/emijrp/temporal/tarea037-%s*" % lang)

if __name__ == "__main__":
    main()
    
