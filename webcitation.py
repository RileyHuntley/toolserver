# -*- coding: utf-8 -*-

# Copyright (C) 2011 emijrp
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
import os
import re
import string
import sys
import urllib
import urllib2

import pagegenerators
import wikipedia

"""
general doc

http://en.wikipedia.org/wiki/Wikipedia:Bots/Requests_for_approval/WebCiteBOT
Bestpractices: http://www.webcitation.org/doc/WebCiteBestPracticesGuide.pdf (http://www.webcitation.org/5y73OBWMw)
http://en.wikipedia.org/wiki/Template:WebCite
http://en.wikipedia.org/wiki/Template:Cite_web

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

def allowbots(text, user):
    #from http://en.wikipedia.org/wiki/Template:Bots#Python
    if (re.search(r'(?im)\{\{\s*(nobots|bots\|(allow=none|deny=.*?' + user + r'.*?|optout=all|deny=all))\s*\}\}', text)):
        return False
    return True

def isURL(url=''):
    #page4 bestpractices
    if url.startswith(('ftp://', 'http://', 'https://')):
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
    html = ''
    try:
        f = urllib.urlopen(url)
        html = f.read()
        f.close()
    except:
        pass
    
    try:
        html = unicode(html, 'utf-8')
    except:
        try:
            html = unicode(html, 'iso-8859-1')
        except:
            pass
    
    m = re.findall(r'<title>([^<>]+)</title>', html)
    if m and len(m) == 1 and len(m[0]) >= 5:
        title = m[0]
    
    title = re.sub(r'(?m)\s+', ' ', title)
    title = undoHTMLEntities(text=title)
    title = re.sub(r'\|', '{{!}}', title) #broke cite web template
    
    return title

def getDateURLFirstTimeInArticle(history=[], url=''):
    #history = revision ID, edit date/time, user name and content
    date = ''
    if history and url:
        for revid, revdate, revusername, revcontent in history:
            if string.find(revcontent, url) != -1:
                date = datetime.datetime(year=int(revdate[:4]), month=int(revdate[5:7]), day=int(revdate[8:10]))
                break
    return date

def isURLDead(url=''):
    #detect 404, 403, etc
    #http://bytes.com/topic/python/answers/30777-404-errors
    if not url:
        print 'isURLDead(): No URL given'
        sys.exit()
    code = ''
    try:
        f = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        code = str(e.code)
    except:
        return True
    if code.startswith(('4', '5')):
        return True
    return False

def recentArchived(url=''):
    archivedate = ''
    archiveurl = ''
    
    webcite = 'http://www.webcitation.org/query?returnxml=true&url=%s' % (urllib.quote(url))
    f = urllib.urlopen(webcite)
    xml = f.read()
    f.close()
    
    if re.search(r'<resultset>', xml): #archived before or never?
        xml = xml.split('<resultset>')[1].split('</resultset>')[0]
        if re.search(r'<result status="success">', xml):
            chunks = xml.split('<result status="success">')[1:] # skiping firsts empty or invalid (status!=success) chunk
            archives = []
            for chunk in chunks:
                archivedatechunk = ''
                archiveurlchunk = ''
                chunk = chunk.split('</result>')[0]
                m = re.findall(r'<timestamp>([^<]+)</timestamp>', chunk)
                if m:
                    archivedatechunk = datetime.datetime(year=int(m[0][:4]), month=int(m[0][5:7]), day=int(m[0][8:10]))
                m = re.findall(r'<webcite_url>(http://www.webcitation.org/[^<]+)</webcite_url>', chunk)
                if m:
                    archiveurlchunk = m[0]
                if archivedatechunk and archiveurlchunk:
                    archives.append([archivedatechunk, archiveurlchunk])
            
            if archives:
                archives.sort() #sort by date
                archives.reverse()
                archivedate, archiveurl = archives[0]
    
    return archiveurl, archivedate

def archiveURL(url='', email=''):
    oldestallowed = 30 #oldest OK archived snapshot
    archiveurl = ''
    webciteid = ''
    archivedate = ''
    if not url or not email:
        print 'Error, not URL or email given'
        sys.exit()
    
    archiveurl, archivedate = recentArchived(url=url)
    if archiveurl and archivedate and (datetime.datetime.now() - archivedate).days <= oldestallowed:
        #if archived recently, avoid archive it again, else, take another snapshot
        print 'This URL (%s) has been archived recently (%s) at %s' % (url, archivedate.strftime('%Y-%m-%d'), archiveurl)
        return archiveurl, archivedate
    
    #sys.exit()
    webcite = 'http://www.webcitation.org/archive?returnxml=true&url=%s&email=%s' % (urllib.quote(url), email)
    f = urllib.urlopen(webcite)
    xml = f.read()
    f.close()
    
    if re.search(r'<error type="email">', xml):
        print 'Error, no e-mail address given'
        sys.exit()
    
    if re.search(r'<result status="success">', xml):
        #it says success, we go to check
        m = re.findall(r'<webcite_url>(http://www.webcitation.org/[^<]+)</webcite_url>', xml)
        if m:
            archiveurl = m[0]
        
        #get webcite id
        m = re.findall(r'<webcite_id>([^<]+)</webcite_id>', xml)
        if m:
            webciteid = m[0]
        
        #try to load
        webciteidurl = 'http://www.webcitation.org/query?returnxml=true&id=%s' % (webciteid)
        f = urllib.urlopen(webciteidurl)
        xml2 = f.read()
        f.close()
        if re.search(r'(?m)<result status="success">\s*<webcite_id>%s</webcite_id>' % (webciteid), xml2): #check if this exactly id is archived successfully
            archivedate = datetime.datetime.now()
            print '%s archived it successfully at %s' % (url, archiveurl)
        else:
            archiveurl = '' #removing, it is not archived correctly
            archivedate = ''
    
    return archiveurl, archivedate

def main():
    limitdays = 700 # oldest allowed ref link
    
    r_case1 = r'(?P<ref><\s*ref[^<>]*>\s*\[*\s*(?P<url>[^<>\[\]\s]+)\s*[^<>]*\s*\]*\s*<\s*/\s*ref\s*>)' #only URL, no title
    #<ref>{{cite web|title=CFL.ca <!-- BOT GENERATED TITLE -->|url=http://www.cfl.ca/standings/1985/reg|work=|archiveurl=http://www.webcitation.org/5gbBs41sC|archivedate=2009-05-07|deadurl=no|accessdate=2009-03-28}}</ref>
    r_case1 = re.compile(r_case1)
    r_case2 = r'(?P<ref><ref[^<>]*>\s*\{\{\s*cite web(?P<param>\s*\|\s*(?!archiveurl|archivedate)(?P<paramname>url|title|first|last|author|authorlink|coauthors|date|month|year|work|publisher|location|page|pages|at|language|trans_title|format|doi|accessdate|quote|ref|separator|postscript)\s*=\s*(?P<paramvalue>[^<>\|]*))*\s*\}\}\s*</ref>)'
    r_case2 = re.compile(r_case2)
    
    start = '!'
    namespace = 0
    email = ''
    
    if len(sys.argv) > 1:
        start = sys.argv[1]
    if len(sys.argv) > 2:
        email = sys.argv[2]
    
    gen = pagegenerators.AllpagesPageGenerator(start, namespace, includeredirects=False)
    preload = pagegenerators.PreloadingGenerator(gen)

    for page in preload:
        if not page.exists() or \
           page.isRedirectPage() or \
           page.isDisambig():
            print 'This page is redirect or disambig, or it does not exist. Skiping...'
            continue
        
        wtitle = page.title()
        print '='*3, wtitle, '='*3
        wtext = newtext = page.get()
        
        if not allowbots(text=wtext, user='BOTijo'):
            print 'Skiping by page exclusion compliant'
            continue
        
        references = r_case1.finditer(wtext)
        if references:
            history = page.getVersionHistory(getAll=False, reverseOrder=True, revCount=500) #only metadata
            if len(history) >= 500:
                print 'Too long history, skiping...'
                continue
            history = page.fullVersionHistory(getAll=False, reverseOrder=True, revCount=500) #now, load history with content
            
            for reference in references:
                ref = reference.group('ref')
                url = reference.group('url')
                if not isURL(url=url):
                    print 'This is not an URL', url
                    continue
                if re.search(r'(web\.archive\.org|webcitation\.org)', url):
                    print 'URL is an archived URL, skiping...', url
                    continue
                
                urltitle = getURLTitle(url=url)
                deadurl = isURLDead(url=url)
                archiveurl = ''
                archivedate = ''
                
                accessdate = getDateURLFirstTimeInArticle(history=history, url=url)
                if not accessdate:
                    print 'Unknown URL (%s) date first time in article, skiping...' % (urls)
                    continue
                if (datetime.datetime.now() - accessdate).days > limitdays:
                    print 'This URL (%s) was added long time ago: %d days. Skiping...' % (url, (datetime.datetime.now() - accessdate).days)
                    continue
                        
                if deadurl:
                    print 'URL is dead (%s), cannot archive it, searching for an archived copy...' % (url)
                    archiveurl, archivedate = recentArchived(url=url)
                    if archiveurl and archivedate:
                        print 'There is an archived copy (%s, %s), YAY!' % (archiveurl, archivedate)
                    else:
                        print 'No archived copy available in WebCite, skiping this reference...'
                        continue
                else:
                    archiveurl, archivedate = archiveURL(url=url, email=email)
                
                if not archiveurl or not archivedate:
                    print 'Error, no archiveurl or no archivedate retrieved for %s' % (url)
                    continue
                
                r_sub1 = '%s - {{WebCite|url=%s|date=%s}}</ref>' % (ref.split('</ref>')[0], archiveurl, archivedate.strftime('%Y-%m-%d'),)
                newtext = string.replace(newtext, ref, r_sub1, 1)
            
        if newtext != wtext:
            wikipedia.showDiff(wtext, newtext)
            summary = 'BOT - Adding link to [[WebCite]] archive for recently added reference(s)'
            page.put(newtext, summary)
        
if __name__ == "__main__":
    main()
