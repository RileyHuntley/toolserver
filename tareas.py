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

import re,os,sys,wikipedia

def percent(c, d=1000):
    if c % d == 0:
        #print '\nLlevamos %d' % c
        sys.stderr.write(".")

def getPageIdPageTitle(wiki, namespace=0):
    print '-'*70
    print 'Cargando pageid/pagetitles para %s:' % wiki
    pageid2pagetitle={}
    pagetitle2pageid={}
    os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_id, page_title from page where page_namespace=%d and page_is_redirect=0;" > /home/emijrp/temporal/%swikipageidpagetitle.txt' % (wiki, wiki, namespace, wiki))
    f=open('/home/emijrp/temporal/%swikipageidpagetitle.txt' % (wiki), 'r')
    c=0
    for line in f:
        line=unicode(line, 'utf-8')
        line=line[:len(line)-1] #evitamos \n
        line=re.sub('_', ' ', line)
        trozos=line.split('    ')
        if len(trozos)==2:
            pageid=trozos[0]
            pagetitle=trozos[1]
            c+=1
            percent(c)
            pageid2pagetitle[pageid]=pagetitle
            pagetitle2pageid[pagetitle]=pageid
    print '\nCargados %d pageid/pagetitle para %s:' % (c, wiki)
    f.close()
    
    return pageid2pagetitle, pagetitle2pageid

def getPageTitle(wiki, namespace=0, redirects=False):
    print '-'*70
    print 'Cargando pagetitles para %s:' % wiki
    pagetitles={}
    if redirects:
        os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title from page where page_namespace=%d;" > /home/emijrp/temporal/%swikipagetitle.txt' % (wiki, wiki, namespace, wiki))
    else:
        os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title from page where page_namespace=%d and page_is_redirect=0;" > /home/emijrp/temporal/%swikipagetitle.txt' % (wiki, wiki, namespace, wiki))
    f=open('/home/emijrp/temporal/%swikipagetitle.txt' % (wiki), 'r')
    c=0
    for line in f:
        line=unicode(line, 'utf-8')
        line=line[:len(line)-1] #evitamos \n
        line=re.sub('_', ' ', line)
        trozos=line.split('    ')
        if len(trozos)==1:
            pagetitle=trozos[0]
            c+=1
            percent(c)
            pagetitles[pagetitle]=False
    print '\nCargados %d pagetitle para %s:' % (c, wiki)
    f.close()
    
    return pagetitles

def getPageTitleWithoutInterwiki(wiki, namespace=0):
    #mysql -h commonswiki-p.db.toolserver.org -e "use commonswiki_p;select count(page_title) from page where page_namespace=0 and page_is_redirect=0 and not page_id in (select ll_from from langlinks, page where page_id=ll_from group by ll_from);"
    pass

def getBotsDic(site):
    bots={u'BOTpolicia':False, u'AVBOT':False, u'CommonsDelinker':False, u'Eskimbot':False, u'YurikBot':False, u'H-Bot':False, u'Paulatz bot':False, u'TekBot':False, u'Alfiobot':False, u'RoboRex':False, u'Agtbot':False, u'Felixbot':False, u'Pixibot':False, u'Sz-iwbot':False, u'Timbot (Gutza)':False, u'Ginosbot':False, u'GrinBot':False, u'.anacondabot':False, u'Omdirigeringsrättaren':False}
    data=site.getUrl("/w/index.php?title=Special:Listusers&limit=5000&group=bot")
    data=data.split('<!-- start content -->')
    data=data[1].split('<!-- end content -->')[0]
    m=re.compile(ur" title=\".*?:(.*?)\">").finditer(data)
    for i in m:
        bots[i.group(1)]=False
    return bots

def getAdminsDic(site):
    admins={}
    data=site.getUrl("/w/index.php?title=Special:Listusers&limit=5000&group=sysop")
    data=data.split('<!-- start content -->')
    data=data[1].split('<!-- end content -->')[0]
    m=re.compile(ur" title=\".*?:(.*?)\">").finditer(data)
    for i in m:
        admins[i.group(1)]=False
    return admins

def getNamespacesList(site):
    nm=[]
    data=site.getUrl("/w/index.php?title=Special:RecentChanges&limit=0")
    data=data.split('<select id="namespace" name="namespace" class="namespaceselector">')[1].split('</select>')[0]
    m=re.compile(ur'<option value="([1-9]\d*)">(.*?)</option>').finditer(data)
    for i in m:
        number=i.group(1)
        name=i.group(2)
        nm.append(name)
    return nm

def getRedirectsAndTargets(wiki, targetStartsWith="A"):
    os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title, rd_title from redirect, page where rd_namespace=0 and rd_title like \'%s%s\' and page_id=rd_from;" > /home/emijrp/temporal/redirects.txt' % (wiki, wiki, targetStartsWith, '%'))
    f=open('/home/emijrp/temporal/redirects.txt', 'r')
    c=0
    print 'Cargando redirecciones'
    redirects={}
    for line in f:
        if c==0: #saltamos la primera linea q es el describe de sql
            c+=1
            continue
        line=unicode(line, 'utf-8')
        line=line[:len(line)-1] #evitamos \n
        line=re.sub('_', ' ', line)
        trozos=line.split('    ')
        if len(trozos)==2:
            redirect=trozos[0]
            target=trozos[1]
            redirects[redirect]=target
            c+=1
            percent(c, 10000)
    f.close()
    
    return redirects


