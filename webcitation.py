# -*- coding: utf-8 -*-

import datetime
import re
import string
import sys
import urllib

import pagegenerators
import wikipedia

"""
general doc

http://en.wikipedia.org/wiki/User:WebCiteBOT
http://www.webcitation.org/faq
http://en.wikipedia.org/wiki/Wikipedia:WikiProject_External_links/Webcitebot2
http://svn.wikimedia.org/svnroot/pywikipedia/trunk/pywikipedia/
http://en.wikipedia.org/wiki/Wikipedia_talk:Link_rot#Proposal_for_new_WikiProject_to_repair_dead_links
http://en.wikipedia.org/wiki/Wikipedia:WikiProject_Council/Proposals/Dead_Link_Repair

"""

"""
examples

2 days http://en.wikipedia.org/w/index.php?title=100_metres&diff=prev&oldid=288764193
3 days http://en.wikipedia.org/w/index.php?title=1983_Beirut_barracks_bombing&diff=prev&oldid=288764280
weeks http://en.wikipedia.org/w/index.php?title=1985+BC+Lions+season&diff=288556972&oldid=283855431

logs
http://en.wikipedia.org/wiki/User:WebCiteBOT/Logs/2009-05-07.log

"""

"""
TODO

exclude domains: web.archive.org (better migrate to {{cite web| archiveurl= ... |}})
do not archive dupes http://en.wikipedia.org/w/index.php?title=!T.O.O.H.!&diff=377595705&oldid=364859494

"""

def isURL(url=''):
    if re.search(r'https?://', url):
        return True
    return False

def undoHTMLEntities(text=''):
    #from WikiTeam, dumpgenerator.py
    text = re.sub('&lt;', '<', text) # i guess only < > & " need conversion http://www.w3schools.com/html/html_entities.asp
    text = re.sub('&gt;', '>', text)
    text = re.sub('&amp;', '&', text)
    text = re.sub('&quot;', '"', text)
    text = re.sub('&#039;', '\'', text)
    return text

def getURLTitle(url=''):
    #replace \n to ' ' http://www.the-fly.co.uk/words/reviews/album-reviews/1242/the-long-blondes
    title = ''
    f = urllib.urlopen(url)
    html = f.read()
    try:
        html = unicode(html, 'utf-8')
    except:
        try:
            html = unicode(html, 'iso-8859-1')
        except:
            pass
    f.close()
    
    m = re.findall(r'<title>([^<>]+)</title>', html)
    if m and len(m) == 1 and len(m[0]) >= 5:
        title = m[0]
    
    title = re.sub(r'[\r\n]+', ' ', title)
    title = undoHTMLEntities(text=title)
    title = re.sub(r'\|', '{{!}}', title) #broke cite web template
    
    return title

def getDateURLFirstTime(history=[], url=''):
    #history = revision ID, edit date/time, user name and content
    date = ''
    if history and url:
        for revid, revdate, revusername, revcontent in history:
            if string.find(revcontent, url) != -1:
                date = revdate
                break
    
    if date:
        print date
        date = datetime.datetime(year=int(date[:4]), month=int(date[5:7]), day=int(date[8:10]))
        print date
    return date

def isURLDead(url=''):
    #detect 404, 403, etc
    return ''

def archiveURL(url='', email=''):
    archiveurl = ''
    if not url or not email:
        print 'Error not URL or email'
        sys.exit()
    url2 = 'http://www.webcitation.org/archive?url=%s&email=%s' % (url, email)
    f = urllib.urlopen(url2)
    raw = f.read()
    f.close()
    
    if re.search('', raw):
        archiveurl = ''
    
    return archiveurl

r_case1 = r'(?P<all><ref>\s*\[*\s*(?P<url>[^> ]+)\s*\]*\s*</ref>)' #only URL, no title
#<ref>{{cite web|title=CFL.ca <!-- BOT GENERATED TITLE -->|url=http://www.cfl.ca/standings/1985/reg|work=|archiveurl=http://www.webcitation.org/5gbBs41sC|archivedate=2009-05-07|deadurl=no|accessdate=2009-03-28}}</ref>
r_case1 = re.compile(r_case1)
r_case2 = r''

gen = pagegenerators.AllpagesPageGenerator(sys.argv[1], 0, includeredirects=False)
preload = pagegenerators.PreloadingGenerator(gen)
email = sys.argv[2]

for page in preload:
    if not page.exists() or \
       page.isRedirectPage() or \
       page.isDisambig():
        continue
    
    wtitle = page.title()
    print '='*5, wtitle, '='*5
    wtext = newtext = page.get()
    refs = r_case1.finditer(wtext)
    if refs:
        history = page.fullVersionHistory(getAll=True, reverseOrder=True)
        for ref in refs:
            all = ref.group('all')
            url = ref.group('url')
            if not isURL(url=url):
                continue
            
            urltitle = getURLTitle(url=url)
            deadurl = isURLDead(url=url)
            accessdate = getDateURLFirstTime(history=history, url=url)
            if not accessdate:
                print 'Unknown first URL date, skiping...'
                continue
            #ok, archive it
            archiveurl = archiveURL(url=url, email=email)
            if not archiveurl:
                print 'Error while archiving URL', url
                continue
            r_sub1 = '<ref>{{cite web|title=%s <!-- BOT GENERATED TITLE -->|url=%s|work=|archiveurl=%s|deadurl=%s|accessdate=%s}}</ref>' % (urltitle, url, archiveurl, deadurl, accessdate.strftime('%Y-%m-%d'))
            newtext = string.replace(newtext, all, r_sub1)
        
    if newtext != wtext:
        pass
        wikipedia.showDiff(wtext, newtext)
        summary = 'BOT - Adding link to [[WebCite]] archive for recently added reference(s)'
        #wikipedia.put(newtext, summary)
        
