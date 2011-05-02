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

""" Update ranking of most linked domains """

import gzip
import os
import re
import sys
import subprocess
import urllib
import wikipedia

langs = [ 'en', 'fr', 'pl', 'it', 'ja', 'ru', 'nl', 'pt', 'sv', 'zh', 'ca', 'no', 'uk', 'fi', 'vi', 'cs', 'hu', 'tr', 'id', 'ko', 'ro', 'da', 'ar', 'eo', 'sr', 'lt', 'fa', 'sk', 'ms', 'vo', 'he', 'bg', 'sl', 'war', ]

for lang in langs:
    print 'Analysing... %s:' % (lang)
    f = urllib.urlopen('http://dumps.wikimedia.org/%swiki/latest/%swiki-latest-md5sums.txt' % (lang, lang))
    raw = f.read()
    f.close()
    date = re.findall(r'%swiki-(\d{8})-externallinks.sql.gz' % (lang), raw)[0]
    date_ = '%s-%s-%s' % (date[:4], date[4:6], date[6:8])
    urllib.urlretrieve('http://dumps.wikimedia.org/%swiki/latest/%swiki-latest-externallinks.sql.gz' % (lang, lang), '%swiki-latest-externallinks.sql.gz' % (lang))
    urllib.urlretrieve('http://dumps.wikimedia.org/%swiki/latest/%swiki-latest-page.sql.gz' % (lang, lang), '%swiki-latest-page.sql.gz' % (lang))
    
    #articles
    articles = {}
    g = gzip.GzipFile('%swiki-latest-page.sql.gz' % (lang), 'r')
    for line in g:
        ids = re.findall(r'\((\d+),0,', line)
        for id in ids:
            articles[id] = True
    g.close()
    print 'Loaded %d pageids for pages in nm = 0 (including redirects)' % (len(articles))
    
    #subprocess.Popen(["""gunzip -c %swiki-latest-externallinks.sql.gz | egrep -o "[0-9],'https?://[^/']+[^\./'][/']" | cut -d "'" -f 2- | sed -r -e "s/['/]$//g" | sed -r -e "s/^(https?):\/\/www\-?[0-9]*\./\1:\/\//g" | sort | uniq -c | sort -nr | head -n 1000 > ranking-%s""" % (lang, lang)], stdout=devnull)
    
    #get urls
    g = gzip.GzipFile('%swiki-latest-externallinks.sql.gz' % (lang), 'r')
    ranking_dic_art = {}
    ranking_dic_all = {}
    r_urls = re.compile(r'\((\d+),\'([a-z]+://[^/\']{3,})[/\']')
    for line in g:
        m = re.findall(r_urls, line) # 3 chars x.y
        for pageid, url in m:
            #merge subdomains
            domain = re.sub(r'(?im)^([a-z]+)://www\-?[0-9]*\.', r'\1://', url)
            #print pageid, url, domain
            
            #only urls in articles
            if articles.has_key(pageid):
                if ranking_dic_art.has_key(domain):
                    ranking_dic_art[domain] += 1
                else:
                    ranking_dic_art[domain] = 1
            
            #all pages
            if ranking_dic_all.has_key(domain):
                ranking_dic_all[domain] += 1
            else:
                ranking_dic_all[domain] = 1
    g.close()
    
    #sort
    ranking_list_art = []
    ranking_list_all = []
    for url, times in ranking_dic_art.items():
        ranking_list_art.append([times, url])
    for url, times in ranking_dic_all.items():
        ranking_list_all.append([times, url])
    ranking_list_art.sort()
    ranking_list_all.sort()
    ranking_list_art.reverse()
    ranking_list_all.reverse()
    print len(ranking_list_art), 'urls in the ranking for nm = 0'
    print len(ranking_list_all), 'urls in the ranking for all namespaces'
    
    #generate output
    limit = 1000
    output = """'''Top %s most linked domains''' from [[w:en:Wikipedia:External links|external links]] as of '''%s'''. This ranking is [[w:en:public domain|public domain]].

== Technical details ==
This ranking was generated using the [http://download.wikimedia.org/%swiki/%s/%swiki-%s-externallinks.sql.gz externallinks.sql.gz] of %s from http://dumps.wikimedia.org/%swiki/

Domains like http://www.google.com are merged into http://google.com. The same for www1., www2., ..., www-1., etc.

Domains like http://books.google.com are not merged into http://google.com.""" % (limit, date_, lang, date, lang, date, date_, lang, )
    
    tableart = ''
    c = 1
    totallinks = 0
    protocols = {}
    for times, domain in ranking_list_art:
        if c <= limit:
            search = len(re.findall('\.', domain)) == 1 and re.sub(r'http://', 'http://*.', domain) or domain
            tableart += '\n|-\n| %s || %s || %s || [{{fullurl:Special:LinkSearch|target=%s}} Link search] ' % (c, times, domain, search, )
        totallinks += times
        protocol = domain.split('://')[0]
        if protocols.has_key(protocol):
            protocols[protocol] += times
        else:
            protocols[protocol] = times
        c += 1
    protocols_list = [[protocol, times] for protocol, times in protocols.items()]
    protocols_list.sort()
    details = ', '.join(['%s (%s)' % (protocol, times) for protocol, times in protocols_list])
    tableart += "\n|-\n| colspan=4 | <small>''%d links in %d different domains''\n''Link details: %s''</small> " % (totallinks, c, details)
    
    tableall = ''
    c = 1
    totallinks = 0
    protocols = {}
    for times, domain in ranking_list_all:
        if c <= limit:
            search = len(re.findall('\.', domain)) == 1 and re.sub(r'http://', 'http://*.', domain) or domain
            tableall += '\n|-\n| %s || %s || %s || [{{fullurl:Special:LinkSearch|target=%s}} Link search] ' % (c, times, domain, search, )
        totallinks += times
        protocol = domain.split('://')[0]
        if protocols.has_key(protocol):
            protocols[protocol] += times
        else:
            protocols[protocol] = times
        c += 1
    protocols_list = [[protocol, times] for protocol, times in protocols.items()]
    protocols_list.sort()
    details = ', '.join(['%s (%s)' % (protocol, times) for protocol, times in protocols_list])
    tableall += "\n|-\n| colspan=4 | <small>''%d links in %d different domains''\n''Link details: %s''</small> " % (totallinks, c, details)
    
    output += """\n\n== Ranking ==
{|
| valign=top |
{| class="wikitable sortable" style="text-align: center;"
! colspan=4 | Only articles (namespace = 0)
|-
! # !! Num. of links !! Domain !! Details
%s
|}
| valign=top |
{| class="wikitable sortable" style="text-align: center;"
! colspan=4 | All pages (all namespaces)
|-
! # !! Num. of links !! Domain !! Details
%s
|}
|}""" % (tableart, tableall)
    
    iws = ''
    for iw in langs:
        if iw != lang:
            iws += '\n[[%s:User:Emijrp/External Links Ranking]]' % (iw)
    output += '\n%s' % (iws)
    
    print output
    
    #save and detect spam black list
    s = wikipedia.Site(lang, 'wikipedia')
    p = wikipedia.Page(s, u'User:Emijrp/External Links Ranking')
    spam = True
    while spam:
        result = p.put(output, u'BOT - Updating ranking')
        #(200, 'OK', {u'edit': {u'spamblacklist': u'http://oocities.com', u'result': u'Failure'}})
        if len(result) > 2 and \
           result[2].has_key('edit') and \
           result[2]['edit'].has_key('spamblacklist') and result[2]['edit'].has_key('result'):
            urlspam = result[2]['edit'].has_key('spamblacklist')
            output = string.replace(output, ' %s' % (urlspam), '<nowiki>%s</nowiki>' % (urlspam)) # important blank space before url
            print '<nowiki> to', urlspam
        else:
            spam = False
    
    os.system('rm %swiki-latest-externallinks.sql.gz' % (lang))
    os.system('rm %swiki-latest-page.sql.gz' % (lang))
