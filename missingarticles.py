#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

import catlib
import os
import pagegenerators
import re
import wikipedia

#todo: sugerir titulos comparando con .lower() ?
# usar una sqlite en vez de un diccionario?

Rlink = re.compile(r'\[\[(?P<title>[^|\[\]]+?)(\|[^\|\[\]]*?)?\]\]') #la original era Rlink = re.compile(r'\[\[(?P<title>[^\]\|\[]*)(\|[^\]]*)?\]\]')
topics = [
'Spain',
]
lang = 'en'
family = 'wikipedia'
site = wikipedia.Site(lang, family)

def getLinks(wtext):
    #adapted from linkedPages() http://svn.wikimedia.org/svnroot/pywikipedia/trunk/pywikipedia/wikipedia.py
    links = []
    wtext = wikipedia.removeLanguageLinks(wtext, site)
    wtext = wikipedia.removeCategoryLinks(wtext, site)
    # remove HTML comments, pre, nowiki, and includeonly sections
    # from text before processing
    wtext = wikipedia.removeDisabledParts(wtext)
    # resolve {{ns:-1}} or {{ns:Help}}
    wtext = site.resolvemagicwords(wtext)
    for match in Rlink.finditer(wtext):
        title = match.group('title')
        title = title.replace("_", " ").strip(" ")
        if title.startswith("#"): # this is an internal section link
            continue
        if not site.isInterwikiLink(title):
            title = title.split('#')[0] #removing sections
            title = '%s%s' % (title[0].upper(), title[1:]) #first up
            if title.startswith(":") or title.startswith("File:") or title.startswith("Image:") or title.startswith("Category:"): # files, cats, etc
                continue
            if title not in links:
                links.append(title)

    return links

def getTitles():
    path = '/home/emijrp/titles.txt'
    #os.system("""mysql -h enwiki-p.db.toolserver.org -e "use enwiki_p;select page_title from page where page_namespace=0;" > %s""" % path)
    f = open(path, 'r')
    titles = {}
    c = 0
    for l in f:
        l = unicode(l, 'utf-8')
        l = l[:-1] #\n
        l = re.sub('_', ' ', l)
        titles[l] = False
        c += 1
        if c % 100000 == 0:
            print c
    f.close()
    return titles

titles = getTitles()

for topic in topics:
    output = '{{User:Emijrp/Redlink-intro|%s}}' % (topic)
    cats = [
    'Top-importance %s articles' % (topic),
    'High-importance %s articles' % (topic),
    'Mid-importance %s articles' % (topic),
    'Low-importance %s articles' % (topic),
    'NA-importance %s articles' % (topic),
    'Unknown-importance %s articles' % (topic),
    ]
    for cat in cats:
        category = catlib.Category(site=site, title=cat)
        if not category.exists():
            wikipedia.output('Error, no category %s' % (cat))
        talkgen = pagegenerators.CategorizedPageGenerator(category, recurse=False, start=None)
        talkpre = pagegenerators.PreloadingGenerator(talkgen, pageNumber=100)
        
        pagetitles = []
        for talkpage in talkpre:
            try:
                wtitle = talkpage.title().split('Talk:')[1]
                pagetitles.append(wtitle)
            except:
                pass #no talk page, probably template talk: or other, skip
        
        gen = pagegenerators.PagesFromTitlesGenerator(pagetitles, site=site)
        pre = pagegenerators.PreloadingGenerator(gen, pageNumber=100)
        alllinks = {}
        for page in pre:
            if not page.exists() or page.isRedirectPage():
                continue
            wtext = page.get()
            links = getLinks(wtext)
            #wikipedia.output('%s - %d' % (page.title(), len(links)))
            links = set(links) #only 1 link per page, no dupes
            #sum
            for link in links:
                if alllinks.has_key(link):
                    alllinks[link] += 1
                else:
                    alllinks[link] = 1
        
        linkslist = [[v, k] for k, v in alllinks.items()]
        linkslist.sort()
        linkslist.reverse()
        
        c = 0
        limit = len(pagetitles)/10
        outputlist = []
        for times, link in linkslist:
            if c > limit:
                break
            if not titles.has_key(link):
                print link, times
                outputlist.append([link, times])
                c += 1
        
        output += '\n\n== Red links from [[:Category:%s|%s]] ==\n{{User:Emijrp/Redlink-start|%d}}' % (cat, cat, limit)
        for item, times in outputlist:
            output += '\n* {{User:Emijrp/Redlink|%s|%d}}' % (item, times)
        output += '\n{{User:Emijrp/Redlink-end}}'

    output += '\n\n{{User:Emijrp/Redlink-footer}}'
    outputpage = wikipedia.Page(site, 'User:Emijrp/Sandbox')
    outputpage.put(output, 'BOT - Testing in subpage sandbox')
