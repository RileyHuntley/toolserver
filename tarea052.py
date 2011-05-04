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
import string
import sys
import subprocess
import urllib
import wikipedia

#langs = ['en', 'fr', 'pl', 'it', 'ja', 'ru', 'nl', 'pt', 'sv', 'zh', 'ca', 'no', 'uk', 'fi', 'vi', 'cs', 'hu', 'tr', 'id', 'ko', 'ro', 'da', 'ar', 'eo', 'sr', 'lt', 'fa', 'sk', 'ms', 'vo', 'he', 'bg', 'sl', 'war', ]

langs = sys.argv[1].split(',')

for lang in langs:
    print 'Analysing... %s:' % (lang)
    f = urllib.urlopen('http://dumps.wikimedia.org/%swiki/latest/%swiki-latest-md5sums.txt' % (lang, lang))
    raw = f.read()
    f.close()
    date = re.findall(r'%swiki-(\d{8})-externallinks.sql.gz' % (lang), raw)[0]
    date_ = '%s-%s-%s' % (date[:4], date[4:6], date[6:8])
    urllib.urlretrieve('http://dumps.wikimedia.org/%swiki/latest/%swiki-latest-externallinks.sql.gz' % (lang, lang), '%swiki-latest-externallinks.sql.gz' % (lang))
    urllib.urlretrieve('http://dumps.wikimedia.org/%swiki/latest/%swiki-latest-page.sql.gz' % (lang, lang), '%swiki-latest-page.sql.gz' % (lang))
    
    #pages, articles nm=0
    pages = {}
    g = gzip.GzipFile('%swiki-latest-page.sql.gz' % (lang), 'r')
    id_r = re.compile(r'\((\d+),(0),')
    c = 0
    for line in g:
        ids = re.findall(id_r, line)
        for id, nm in ids:
            pages[int(id)] = int(nm) #nm=0 in the regexp, ready to change it to support more nms
            if c % 10000 == 0:
                print 'Loaded %d pages' % (c)
            c += 1
    g.close()
    print 'Loaded %d pageids for pages in nm = 0 (including redirects)' % (len(pages.keys()))
    
    #subprocess.Popen(["""gunzip -c %swiki-latest-externallinks.sql.gz | egrep -o "[0-9],'https?://[^/']+[^\./'][/']" | cut -d "'" -f 2- | sed -r -e "s/['/]$//g" | sed -r -e "s/^(https?):\/\/www\-?[0-9]*\./\1:\/\//g" | sort | uniq -c | sort -nr | head -n 1000 > ranking-%s""" % (lang, lang)], stdout=devnull)
    
    #get urls
    g = gzip.GzipFile('%swiki-latest-externallinks.sql.gz' % (lang), 'r')
    ranking_dic = {}
    r_urls = re.compile(r'\((\d+),\'([a-z]+://[^/\']{3,})[/\']')
    c = 0
    for line in g:
        m = re.findall(r_urls, line) # 3 chars x.y
        for pageid, url in m:
            pageid = int(pageid)
            if c % 10000 == 0:
                print 'Loaded %d external links' % (c)
            #merge subdomains
            domain = re.sub(r'(?im)^([a-z]+)://www\-?[0-9]*\.', r'\1://', url)
            #print pageid, url, domain
            
            if ranking_dic.has_key(domain):
                if pages.has_key(pageid) and pages[pageid] == 0:
                    ranking_dic[domain][0] += 1
                else:
                    ranking_dic[domain]['all'] += 1
            else:
                if pages.has_key(pageid) and pages[pageid] == 0:
                    ranking_dic[domain] = {0: 1, 'all': 1}
                else:
                    ranking_dic[domain] = {0: 0, 'all': 1}
            
            c += 1
    g.close()
    
    #sort
    ranking_list_art = []
    ranking_list_all = []
    for url, nms_dic in ranking_dic.items():
        if nms_dic[0] > 1: #discarding links with only 1 occurence
            ranking_list_art.append([nms_dic[0], url])
        if nms_dic['all'] > 1:
            ranking_list_all.append([nms_dic['all'], url])
    #del ranking_dic
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
            tableart += '\n|-\n| %s || %s || [{{fullurl:Special:LinkSearch|target=%s}} %s] ' % (c, domain, search, times, )
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
    tableart += "\n|-\n| colspan=3 | <small>''%d links in %d different domains''\n''Link details: %s''</small> " % (totallinks, c-1, details) #c-1 due to c starts in 1 for the ranking #position
    
    tableall = ''
    c = 1
    totallinks = 0
    protocols = {}
    for times, domain in ranking_list_all:
        if c <= limit:
            search = len(re.findall('\.', domain)) == 1 and re.sub(r'http://', 'http://*.', domain) or domain
            tableall += '\n|-\n| %s || %s || [{{fullurl:Special:LinkSearch|target=%s}} %s] ' % (c, domain, search, times, )
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
    tableall += "\n|-\n| colspan=3 | <small>''%d links in %d different domains''\n''Link details: %s''</small> " % (totallinks, c-1, details)
    
    output += """\n\n== Ranking ==
{|
| valign=top |
{| class="wikitable sortable" style="text-align: center;"
! colspan=3 | Only articles (namespace = 0)
|-
! # !! Domain !! Num. of links
%s
|}
| valign=top |
{| class="wikitable sortable" style="text-align: center;"
! colspan=3 | All pages (all namespaces)
|-
! # !! Domain !! Num. of links
%s
|}
|}""" % (tableart, tableall)
    
    iws = ''
    for iw in langs:
        if iw != lang:
            iws += '\n[[%s:User:Emijrp/External Links Ranking]]' % (iw)
    output += '\n%s' % (iws)
    output += '\n'
    
    #print output
    
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
            urlspam = result[2]['edit']['spamblacklist']
            output = string.replace(output, ' %s' % (urlspam), '<nowiki>%s</nowiki>' % (urlspam)) # important blank space before url
            print '<nowiki> to', urlspam
        else:
            spam = False
    
    os.system('rm %swiki-latest-externallinks.sql.gz' % (lang))
    os.system('rm %swiki-latest-page.sql.gz' % (lang))
