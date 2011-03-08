#!/usr/bin/env python2.5
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

import wikipedia, re
import time
import MySQLdb

def latestDump(family, lang, date):
    return

def userList(site, group):
    users=[]
    aufrom="!"
    while aufrom:
        query=wikipedia.query.GetData({'action':'query', 'list':'allusers', 'augroup':group, 'aulimit':'500', 'aufrom':aufrom},site=site,useAPI=True)
        for allusers in query['query']['allusers']:
            users.append(allusers['name'])
        if query.has_key('query-continue'):
            aufrom=query.has_key('query-continue')
        else:
            aufrom=""
    return users

def adminList(site):
    return userList(site, 'sysop')

def botList(site):
    bots=userList(site, 'bot') #local bots
    #also meta bots (all are global bots?)
    bots+=[u'AHbot', u'Aibot', u'AkhtaBot', u'Albambot', u'Alecs.bot', 
           u'Alexbot', u'AlleborgoBot', u'Almabot', u'AlnoktaBOT', 
           u'Amirobot', u'AnankeBot', u'ArthurBot', 
           u'BOT-Superzerocool', u'BodhisattvaBot', u'BokimBot', 
           u'BotMultichill', u'Broadbot', u'ButkoBot', u'CarsracBot', 
           u'CarsracBot', u'ChtitBot', u"D'ohBot", u'DSisyphBot', 
           u'Darkicebot', u'Dinamik-bot', u'DirlBot', u'DorganBot', 
           u'DragonBot', u'Drinibot', u'DumZiBoT', u'EivindBot', 
           u'Escarbot', u'Estirabot', u'FiriBot', u'FoxBot', 
           u'Gerakibot', u'GhalyBot', u'GnawnBot', u'GrouchoBot', 
           u'HerculeBot', u'Idioma-bot', u'Interwicket', u'JAnDbot', 
           u'Jotterbot', u'KhanBot', u'Kwjbot', u'LaaknorBot', 
           u'Louperibot', u'Loveless', u'Luckas-bot', u'MSBOT', 
           u'MagnusA.Bot', u'Maksim-bot', u'MalafayaBot', u'MastiBot', 
           u'MelancholieBot', u'MenoBot', u'MondalorBot', u'Muro Bot', 
           u'MystBot', u'Nallimbot', u'OKBot', u'Obersachsebot', 
           u'Ptbotgourou', u'RedBot', u'Robbot', u'RobotQuistnix', 
           u'RoggBot', u'Rubinbot', u'SassoBot', u'SieBot', 
           u'SilvonenBot', u'Soulbot', u'SpBot', u'SpaceBirdyBot', 
           u'SpillingBot', u'StigBot', u'Synthebot', u'Sz-iwbot', 
           u'TXiKiBoT', u'Tanhabot', u'Thijs!bot', 
           u'TinucherianBot II', u'TuvicBot', u'VVVBot', u'Ver-bot', 
           u'VolkovBot', u'WeggeBot', u'Xqbot', u'Zorrobot', u'Zxabot']
    """aufrom="!"
    while aufrom:
        query=wikipedia.query.GetData({'action':'query', 'list':'allusers', 'augroup':'bot', 'aulimit':'500', 'aufrom':aufrom},site=wikipedia.Site("meta", "meta"),useAPI=True)
        for allusers in query['query']['allusers']:
            bots.append(allusers['name'])
        if query.has_key('query-continue'):
            aufrom=query.has_key('query-continue')
        else:
            aufrom=""
    """
    bots.sort()
    return bots

def unflaggedBotsList(site):
    bots=[]
    page=wikipedia.Page(wikipedia.Site("meta", "meta"), u"User:Emijrp/List of Wikimedians by number of edits/Unflagged bots")
    lines=page.get().splitlines()
    linesupdated=[]
    for line in lines:
        if line[0]=="#":
            linesupdated.append(line)
        elif len(re.findall(";", line))==2:
            [lang, family, nick]=line.split(";")
            if (lang==site.lang and family==site.family.name) or \
               (lang=='*' and family==site.family.name) or \
               (lang==site.lang and family=='*') or \
               (lang=='*' and family=='*'):
                bots.append(nick)
            if (lang!="*" and family!="*"):
                if lines.count("*;*;%s" % (nick))==0 and \
                   lines.count("%s;*;%s" % (lang, nick))==0 and \
                   lines.count("*;%s;%s" % (family, nick))==0:
                    linesupdated.append(line)
            else:
                linesupdated.append(line)
        else:
            print "error, bad format,", line
            linesupdated.append(line)
    bots.sort()
    linesupdated.sort()
    #updating page list
    page.put(u"\n".join(linesupdated), u"BOT - Updating list")
    
    return bots

#unflaggedBotsList(wikipedia.Site("es", "wikipedia"))

def insertBOTijoInfo(site):
    delay=10
    
    #/info page
    botinfo=wikipedia.Page(site, u"User:BOTijo/info")
    info=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u"User:Emijrp/BOTijoInfo.css").get()
    
    #todo: con excludedprojects cambiar los enlaces a rankings que aparecen
    
    if not botinfo.exists() or botinfo.get()!=info:
        botinfo.put(info, u"BOT - Bot info page")
        time.sleep(delay)

    #talk
    bot=wikipedia.Page(site, u"User:BOTijo")
    bottalk=bot.toggleTalkPage()
    if not bottalk.exists():
        bottalk.put(u"#REDIRECT [[User:BOTijo]]", u"BOT - Redirect")
        time.sleep(delay)
    elif not bottalk.isRedirectPage():
        bottalk.put(u"#REDIRECT [[User:BOTijo]]\n\n%s" % bottalk.get(), u"BOT - Redirect")
    
    #bot userpage
    if botList(site).count(u"BOTijo")==0: #no tiene flag
        if not bot.exists():
            bot.put(u"{{/info}}", u"BOT - Creating bot userpage")
            time.sleep(delay)
        elif not re.search(ur"{{/info}}", bot.get()):
            bot.put(u"{{/info}}\n%s" % bot.get(), u"BOT - Adding info")
            time.sleep(delay)
    else: #tiene flag
        if not bot.exists():
            #bot.put(u"This is a bot account operated by [[w:es:User:Emijrp|emijrp]] ([[w:es:User talk:Emijrp|talk]]) from [[w:es:Mainpage|Spanish Wikipedia]].\n\n'''This [[w:en:Wikipedia:Bot policy|bot]] runs on the [[meta:Toolserver|Wikimedia Toolserver]].''' <br /><small>''Administrators: If this bot needs to be blocked due to a malfunction, please remember to disable autoblocks so that other Toolserver bots are not affected.''", u"BOT - Creating bot userpage")
            bot.put(u"{{/info|flag}}", u"BOT - Creating bot userpage")
            time.sleep(delay)
        elif not re.search(ur"(?i)\{\{\/info\|flag\}\}", bot.get()):
            bot.put(u"%s\n{{/info|flag}}" % re.sub(ur"(?i)\{\{\s*/info[^\}]*?\}\}", ur"", bot.get()), u"BOT - Flag granted")
            time.sleep(delay)

def getLangsByFamily(family, min=0, max=999999999):
    conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute("SELECT lang from wiki where family='%s' and is_closed=0 and size>%s and size<%s;" % (family, min, max))
    result=cursor.fetchall()
    langs=[]
    for row in result:
        if len(row)==1:
            langs.append(row[0])        

    cursor.close()
    conn.close()
    return langs

def getNamespaceName(lang, family, nsnumber):
    if lang=='simple':
        lang='en-simple'
    conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute("SELECT ns_name from namespace where dbname='%s' and ns_id=%s;" % (getDbname(lang, family), nsnumber))
    result=cursor.fetchall()
    nsname=""
    for row in result:
        if len(row)==1:
            nsname=unicode(row[0], "utf-8")

    cursor.close()
    conn.close()
    return nsname

def getDbname(lang, family):
    if lang=='simple':
        lang='en-simple'
    multilang = 0
    if family in ['commons', 'wikispecies']:
        multilang = 1
    conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute("SELECT dbname from wiki where family='%s' and lang='%s' and is_multilang=%d;" % (family, lang, multilang))
    result=cursor.fetchall()
    dbname=""
    for row in result:
        if len(row)==1:
            dbname=row[0]

    cursor.close()
    conn.close()
    return dbname

def getServer(lang, family):
    if lang=='simple':
        lang='en-simple'
    multilang = 0
    if family in ['commons', 'wikispecies']:
        multilang = 1
    conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute("SELECT server from wiki where family='%s' and lang='%s' and is_multilang=%d;" % (family, lang, multilang))
    result=cursor.fetchall()
    server=""
    for row in result:
        if len(row)==1: #por si no existe ese idioma
            server="sql-s%s" % row[0]
            break

    cursor.close()
    conn.close()
    return server

def getServers():
    conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute("SELECT distinct server from wiki;")
    result=cursor.fetchall()
    servers=[]
    for row in result:
        servers.append("sql-s%s" % row[0])

    cursor.close()
    conn.close()
    return servers

def getArticleCount(lang, family):
    if lang=='simple':
        lang='en-simple'
    conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute("SELECT size from wiki where family='%s' and lang='%s';" % (family, lang))
    result=cursor.fetchall()
    size=0
    for row in result:
        if len(row)==1:
            size=int(row[0])

    cursor.close()
    conn.close()
    return size

def isExcluded(tarea, family, lang):
    #ejemplo de que funciona http://dv.wikipedia.org/w/index.php?title=%DE%89%DE%AC%DE%89%DE%B0%DE%84%DE%A6%DE%83%DE%AA:Emijrp/List_of_Wikipedians_by_number_of_edits_%28bots_included%29&diff=prev&oldid=64351

    excludedprojects={
        'tarea008': {
            'wikipedia': [
                'de', #http://de.wikipedia.org/wiki/Wikipedia:L%C3%B6schkandidaten/24._Juli_2010#Benutzer:Emijrp.2FList_of_Wikipedians_by_number_of_edits_.28gel.C3.B6scht.29
                'ko', #no les interesa http://es.wikipedia.org/w/index.php?title=Usuario_Discusi%C3%B3n:Emijrp&diff=35727924&oldid=35727631
                'pl', #ya tienen uno http://es.wikipedia.org/w/index.php?title=Usuario_Discusi%C3%B3n:Emijrp&diff=35726268&oldid=35726116
                'hu', #ya tienen su propio ranking http://hu.wikipedia.org/wiki/Wikip%C3%A9dia:Wikip%C3%A9dist%C3%A1k_list%C3%A1ja_szerkeszt%C3%A9ssz%C3%A1m_szerint lo desactivo porque les recreaba las páginas /begin y /end
                'movementroles', #wmf wiki?
                'ten', #no es idioma, es el wiki de los 10 anyos
                ],
            'wiktionary': [],
            'wikinews': [],
            'wikibooks': [],
            'wikisource': [],
            }
        }

    if excludedprojects.has_key(tarea):
        if excludedprojects[tarea].has_key(family):
            if excludedprojects[tarea][family].count(lang)>0:
                return True
    
    return False


