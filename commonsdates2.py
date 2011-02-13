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

#ideas:
#15junio2009, cuidado con las regexp tipo ddmmaaaa
#coger meses de todos los idiomas con el select html de las contribs, mirar que distintos meses en distintos idiomas no tengan en mismo nombre (colisión), hacer una versión simple que admita 12juin2009 y 12 juin 2009 y va que chuta
#hora delante de la fecha, invetir, 17:22 26 июня 2009
#para las fechas que coincida dd y mm, no pasa nada, el resto verficiar con exif?

## @package commonsdates
# Localisation for dates (YYYY-MM-DD) and some usual headings in images descriptions in Commons

import re, urllib, sys, time, getopt
import wikipedia, catlib, pagegenerators

def main():
    """Localisation for dates (YYYY-MM-DD) and some usual headings in images descriptions in Commons"""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error, msg:
        print msg
        print "for help use --help"
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            print main.__doc__
            sys.exit(0)
    
    total=8500000
    modif=0
    anal=0
    
    ratelimit=15
    commonssite=wikipedia.Site('commons', 'commons')
    st=u"!"
    if (len(sys.argv)>=2):
        st=sys.argv[1]
    gen=pagegenerators.AllpagesPageGenerator(start = st, namespace = 6, includeredirects = False, site = commonssite)
    pre=pagegenerators.PreloadingGenerator(gen, pageNumber=250, lookahead=250)

    inicio=ur"(?im)^(?P<inicio> *\| *Date *\= *)"
    # eliminamos . finales que no permiten hacer la conversión de fechas
    # no meter el espacio en [ \.]* al comienzo http://commons.wikimedia.org/w/index.php?title=File:18crown6.2.png&diff=prev&oldid=39395458
    fin=ur"[ \.]*(?P<fin> *[\n\r\|])" 

    #dd/mm/aaaa
    separador_ddmmaaaa=[ur" *[\-\/\,\. ] *"]  #cuidado no meter ()
    regexp_ddmmaaaa=ur"%s(?P<change>(?P<day>0?[1-9]|1[0-9]|2[0-9]|3[0-1])(?P<separator1>%s)(?P<month>0?[1-9]|1[0-9]|2[0-9]|3[0-1])(?P<separator2>%s)(?P<year>\d{4}))%s" % (inicio, "|".join(separador_ddmmaaaa), "|".join(separador_ddmmaaaa), fin)
    sub_ddmmaaaa=ur"\g<inicio>%s-%s-%s\g<fin>"

    #{{Own}}
    inicio_own=ur"(?im)^(?P<inicio> *\| *Source *\= *)"
    fin_own=ur"[ \.]*(?P<fin> *[\n\r\|])" #eliminamos . finales que no permiten hacer la conversión
    #CUIDADO con own photograph! http://commons.wikimedia.org/w/index.php?title=File:Teatro_Coccia_chandelier.jpg&diff=next&oldid=19903214
    #ideas: own photo, own photograph
    own_synonym=[ur"own[ \-]*work", ur"Own[ \-]*work by uploader", ur"Opera creata dall\'uploader \(own work by uploader\)", ur"self[ \-]*made", ur"eie[ \-]*werk", ur"Treballo de qui la cargó", ur"Trabayu propiu", ur"Уласны твор", ur"Собствена творба", ur"Vlastito djelo", ur"Treball propi", ur"Vlastní dílo", ur"Eget arbejde", ur"Eigene Arbeit", ur"Propra verko", ur"Trabajo propio", ur"self[ \-]*made *\/ *foto propia", ur"Üleslaadija oma töö", ur"Oma teos", ur"Travail personnel", ur"Traballo propio", ur"Vlastito djelo postavljača", ur"A feltöltő saját munkája", ur"Karya sendiri", ur"Opera propria", ur"Opus proprium", ur"Mano darbas", ur"Egen Wark", ur"Eigen waark", ur"Eigen werk", ur"Eget arbeide", ur"Trabalh personal", ur"Ejen Woakj", ur"Praca własna", ur"Trabalho próprio", ur"Operă proprie", ur"Vlastné dielo", ur"Lastno delo", ur"Eget arbete", ur"Sariling gawa", ur"Opera creata e caricata dall\'autore \(own work by uploader\)", ur"Own work \- Vlastné dielo"] #no meter  ()
    regexp_own=ur"%s(?P<change>\[?\[?(%s)\]?\]?)%s" % (inicio_own, "|".join(own_synonym), fin_own)
    sub_own=ur"\g<inicio>{{Own}}\g<fin>"

    #== Licensing ==
    inicio_lic=ur"" #noseusade momento
    fin_lic=ur"(?P<fin> *[\n\r])"
    lic_synonym=[ur"Licensing", ur"License", ur"\[\[Commons\:Copyright tags\|Licensing\]\]", ur"Licencia", ur"Lizenz", ur"Licence", ur"Licencja", ur"Licença", ur"ライセンス", ur"Лицензирование", ur"Licencado", ur"ترخيص", ur"\[\[Commons\:Copyright tags\|ترخيص\]\]", ur"Licenţiere", ur"Licenza", ur"Licenza d\'uso", ur"Licentie", ur"Llicència", ur"Licenc", ur"Lisenssi", ur"\[\[COM\:TOM\|Lisenssi\]\]"]  #no meter  ()
    regexp_lic=ur"(?im)^%s(?P<h1>\=\=) *(?P<change>\[?\[?(%s)\]?\]? *\:?) *(?P<h2>\=\=)%s" % (inicio_lic, "|".join(lic_synonym), fin_lic)
    sub_lic=ur"\g<h1> {{int:license-header}} \g<h2>\g<fin>"

    #== Summary ==
    inicio_sum=ur"" #noseusade momento
    fin_sum=ur"(?P<fin> *[\n\r])"
    sum_synonym=[ur"Summary", ur"Sumario", ur"Beschreibung", ur"Description", ur"Opis", ur"Descrição do ficheiro", ur"Beskrivning", ur"Dettagli", ur"ファイルの概要", ur"Beschrijving", ur"Краткое описание", ur"ملخص", ur"Resum", ur"Popis", ur"Resumo", ur"Beskrivelse", ur"Összegzés", ur"Beskrivelse", ur"Yhteenveto", ur"Descriere fişier", ur"Σύνοψη"]
    regexp_sum=ur"(?im)^%s(?P<h1>\=\=) *(?P<change>\[?\[?(%s)\]?\]? *\:?) *(?P<h2>\=\=)%s" % (inicio_sum, "|".join(sum_synonym), fin_sum)
    sub_sum=ur"\g<h1> {{int:filedesc}} \g<h2>\g<fin>"

    c=0
    t1=time.time()
    regexp_changed=ur"(?m)^ *\| *Date *\= *(?P<changed>\d{4}\-\d{2}\-\d{2})"
    regexp_changed_aaaamm=ur"(?m)^ *\| *Date *\= *(?P<changed>\d{4}\-\d{2})"
    regexp_changed_own=ur"(?m)^ *\| *Source *\= *(?P<changed>\{\{Own\}\})"
    regexp_changed_lic=ur"(?m)^\=+ *(?P<changed>\{\{int:license-header\}\}) *\=+"
    regexp_changed_sum=ur"(?m)^\=+ *(?P<changed>\{\{int:filedesc\}\}) *\=+"
    for page in pre:
        if not page.exists() or page.isRedirectPage() or page.isDisambig():
            continue
        anal+=1
        wtitle=page.title()
        wtext=newtext=page.get()
    
        if re.search(ur"(?i)\{\{ *User\:Tivedshambo\/Information", wtext) or \
           re.search(ur"(?i)\<nowiki\>", wtext): #nowiki para evitar imágenes con historiales de otras wikis
            continue
        
        change=u""
        changed=""
        metadatadate=""
        if len(re.findall(regexp_ddmmaaaa, newtext))==1: # dd mm aaaa ó mm dd aaaa genericos
            m=re.compile(regexp_ddmmaaaa).finditer(newtext)
            year=month=day=u""
            for i in m:
                change=i.group("change")
                [year, month, day]=[i.group("year"), i.group("month"), i.group("day")]
                if len(month)==1:
                    month="0"+month
                if len(day)==1: #nunca deberia entrar aqui, a menos que coincida con el numero del mes
                    day="0"+day
                break
            
            #4 casos posibles:
            #ambos > 12 imposible
            #ambos <= 12 ambiguedad (usar metadatos)
            #day > 12 y month <= 12 todo bien
            #day <= 12 y month > 12 invertir
            if int(day)>12 and int(month)>12: #error
                print "Error: ambas fechas mayores de 12"
                log = wikipedia.Page(commonssite, u"User:Emijrp/Commons dates")
                log.put(u'\n* [[:%s]] (wrong date?)' % (wtitle))
                continue
            elif int(day)<=12 and int(month)<=12: #usamos metadatos para evitar ambiguedad
                continue #revisar esta rama del if, verificar que compara los 3 metadatos posibles y coinciden 
                #metadatos
                metadata=wikipedia.query.GetData({'action':'query', 'prop':'imageinfo', 'iiprop':'metadata', 'titles':'%s' % re.sub(" ", "_", page.title())},site=wikipedia.Site('commons','commons'),useAPI=True)
                metadata=metadata['query']['pages'][metadata['query']['pages'].keys()[0]]['imageinfo'][0]['metadata']
                metadatadate=""
                metadatac=0
                if metadata!=None:
                    #http://commons.wikimedia.org/w/index.php?title=File:AlexRaphaelMeschini2.jpg&diff=prev&oldid=42074919
                    #los metadatos no coinciden
                    for metadatadict in metadata:
                        metaname=metadatadict['name']
                        metavalue=metadatadict['value']
                        
                        if metaname in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                            #print metaname, metavalue
                            if not metadatadate:
                                metadatac+=1
                                metadatadate=metavalue
                            elif metadatadate!=metavalue: # los metadatos arrojan varios valores de fechas
                                break #nos vamos, no coinciden las fechas
                            else:
                                metadatac+=1 #para mas seguridad, pedimos 3 metadatos de fechas
                #tiene el formato habitual? 2008:04:10 11:41:31
                metadatadate2=re.findall(ur"(\d{4}):(\d{2}):(\d{2}) \d{2}:\d{2}:\d{2}", metadatadate)
                #print len(metadatadate)
                #print metadatadate2
                if metadatac!=3 or len(metadatadate)!=19 or len(metadatadate2)!=1: #[(u'2008', u'12', u'07')]
                    continue #no hay 3 metadatos, o las fechas no coinciden
                
                #verificamos dd y mm, y sino intercambiamos, y sino saltamos
                if metadatadate2[0][0]==year and metadatadate2[0][1]==month and metadatadate2[0][2]==day:
                    pass #todo bien
                elif metadatadate2[0][0]==year and metadatadate2[0][1]==day and metadatadate2[0][2]==month:
                    #tenemos que intercambiarlos
                    aux=month
                    month=day
                    day=aux
                else:
                    continue
            elif int(month)>12:
                #http://commons.wikimedia.org/w/index.php?title=File:16-23_John_Hart_House_2.jpg&diff=39393632&oldid=39248969
                aux=day
                day=month
                month=aux
            elif int(day)>12:
                pass #ok
            
            newtext=re.sub(regexp_ddmmaaaa, sub_ddmmaaaa % (year, month, day), newtext, 1)
            m=re.compile(regexp_changed).finditer(newtext)
            for i in m:
                changed=i.group("changed")
                break
    
        #{{Own}}
        change_own=u""
        changed_own=u""
        if newtext!=wtext:
            if len(re.findall(regexp_own, newtext))==1:
                m=re.compile(regexp_own).finditer(newtext)
            
                for i in m:
                    change_own=i.group("change")
                    break
            
                newtext=re.sub(regexp_own, sub_own, newtext, 1)
                m=re.compile(regexp_changed_own).finditer(newtext)
                for i in m:
                    changed_own=i.group("changed")
                    break
    
        #== {{int:license-header}} ==
        change_lic=u""
        changed_lic=u""
        """if True or newtext!=wtext:
            if len(re.findall(regexp_lic, newtext))==1:
                m=re.compile(regexp_lic).finditer(newtext)
            
                for i in m:
                    change_lic=i.group("change")
                    break
            
                newtext=re.sub(regexp_lic, sub_lic, newtext, 1)
                m=re.compile(regexp_changed_lic).finditer(newtext)
                for i in m:
                    changed_lic=i.group("changed")
                    break"""
        
        #== {{int:filedesc}} ==
        change_sum=u""
        changed_sum=u""
        """if True or newtext!=wtext:
            if len(re.findall(regexp_sum, newtext))==1:
                m=re.compile(regexp_sum).finditer(newtext)
            
                for i in m:
                    change_sum=i.group("change")
                    break
            
                newtext=re.sub(regexp_sum, sub_sum, newtext, 1)
                m=re.compile(regexp_changed_sum).finditer(newtext)
                for i in m:
                    changed_sum=i.group("changed")
                    break"""
        
        if newtext!=wtext:
            wikipedia.output(wtitle)
            wikipedia.showDiff(wtext, newtext)
            #time.sleep(3)
            if c>=ratelimit:
                while time.time()-t1<60:
                    time.sleep(0.1)
                t1=time.time()
                c=0
        
            try:
                summary=u"BOT - Changes to allow localization:"
                if changed:
                    summary+=u" %s → %s;" % (change, changed)
                    if metadatadate:
                        summary+=u" verified using metadata %s" % (metadatadate)
                if changed_own:
                    summary+=u" %s → %s;" % (change_own, changed_own)
                if changed_lic:
                    summary+=u" %s → %s;" % (change_lic, changed_lic)
                if changed_sum:
                    summary+=u" %s → %s;" % (change_sum, changed_sum)
                
                wikipedia.output(summary)
                #page.put(newtext, summary)
                modif+=1
                est=total/anal*modif
                print "%d analysed, %d modified, estimated total edits: %d" % (anal, modif, est)
                c+=1
            except:
                pass

if __name__ == "__main__":
    main()

