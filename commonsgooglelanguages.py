# -*- coding: utf-8 -*-

import re
import wikipedia
import sys
import pagegenerators
import urllib
import os
import subprocess
import time

"""errors: 
http://commons.wikimedia.org/w/index.php?title=File:Backi_petrovac_map.png&diff=35687668&oldid=31253617

"""

def checkLanguage(desc):
    desc_=desc
    desc_=desc_.lower()
    desc_=re.sub(ur"[\'\"]", ur" ", desc_)
    desc_=re.sub(ur"\[\[(?P<link>[^\]\|]+?)\]\]", ur"\g<link>", desc_)
    desc_=re.sub(ur"\[\[(?P<link>[^\]\|]+?)\|(?P<label>[^\]\|]+?)\]\]", ur"\g<label>", desc_)
    desc_=re.sub(ur" ", ur"%20", desc_)
    
    url="http://ajax.googleapis.com/ajax/services/language/detect?v=1.0&q="
    url+=desc_.encode("utf-8")
    os.system('curl -e http://es.wikipedia.org/wiki/User:Emijrp "%s" > a.txt 2> /dev/null' % url)
    print "Description:", desc
    print "Description sent to Google", desc_
    #raw= subprocess.Popen(["curl", "-e", "http://es.wikipedia.org/wiki/User:Emijrp", "'%s'" % url], stdout=subprocess.PIPE).communicate[0]
    f=open("a.txt", "r")
    raw=f.read()
    f.close()
    f=open("a.txt", "w")
    f.write("")
    f.close()
    print "RAW de Google:", raw
    time.sleep(0.5)
    n=re.compile(ur'"language":"(?P<lang>[a-z]+)","isReliable":(?P<rel>true|false),"confidence":(?P<con>[0-9\.]+)\}').finditer(raw)
    lang=False
    con=0
    rel="false"    
    for j in n:
        lang=j.group("lang")
        con=float(j.group("con"))
        rel=j.group("rel")
    
    return lang, rel, con

commonswiki=wikipedia.Site("commons", "commons")

st=u"A" #start page

if (len(sys.argv)>=2):
    st=sys.argv[1]

gen=pagegenerators.AllpagesPageGenerator(start = st, namespace = 6, includeredirects = False, site = commonswiki)
pre=pagegenerators.PreloadingGenerator(gen, pageNumber=250, lookahead=250)

for page in pre:
    if not page.exists():
        print "No exist"
        continue
    
    wikipedia.output(u"%s\n=== %s ===" % ("#"*50, page.title()))    

    wtext=page.get()
    if not re.search(ur"(?i)\{\{ *information", wtext):
        print "No {{Information}} template"
        continue
    
    reg=ur"(?im)(?P<ini>Description *= *)(?P<desc>[^\n\r\{\/\:\<]+?)(?P<fin>\r\n *\| *Source *=)" # never templates, no <br>
    m=re.compile(reg).finditer(wtext)
    for i in m:
        desc=i.group("desc")
        if len(desc)<50 or len(desc)>4000: #el limite de google es 5000, probar límite inferior
            break
        
        try:
            [lang, rel, con]=checkLanguage(desc)
        except:
            continue
        if rel=="true" and con>0.5:
            [lang1, rel1, con1]=checkLanguage(desc[:(len(desc)-1)/2])
            [lang2, rel2, con2]=checkLanguage(desc[(len(desc)-1)/2:])
            if lang and lang1 and lang2 and lang1==lang and lang2==lang: # and rel1=="true" and rel2=="true":
                newtext=re.sub(reg, ur"\g<ini>{{%s|\g<desc>}}\g<fin>" % lang, wtext)
                print "Response by Google: Language:", lang, "    isReliable", rel, "    Confidence", con
                print '-'*50
                wikipedia.showDiff(wtext, newtext)
                print '-'*50
                page.put(newtext, u"BOT - Adding {{%s}} to description: %s" % (lang, desc))
            else:
                print "-----> Not conclusive <-----"
        break
    

