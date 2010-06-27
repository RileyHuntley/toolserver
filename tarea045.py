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

""" Actualiza la lista global de ediciones en meta """

import re
import sys
import time
import os

import MySQLdb

import wikipedia

import tarea000

wtitle=u"User:Emijrp/List of Wikimedians by number of edits"
site=wikipedia.Site('meta', 'meta')
limit=1000

def loadUnflaggedBots():
    bots = []
    botssubpage = wikipedia.Page(site, u"%s/Unflagged bots" % wtitle)
    if botssubpage.exists():
        bots = botssubpage.get().splitlines()
        output = botssubpage.get().splitlines()
        output.sort()
        botssubpage.put("\n".join(output), u"BOT - Sorting list")
    return bots

def loadProjects():
    conn = MySQLdb.connect(host='sql', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
    cursor = conn.cursor()
    cursor.execute("SELECT dbname, domain, server, lang, family from wiki where is_closed=0 and (family='commons' or family='wikibooks' or family='wikinews' or family='wikipedia' or family='wikiquote' or family='wikisource' or family='wikispecies' or family='wikiversity' or family='wiktionary');")
    result = cursor.fetchall()
    projects = []
    for row in result:
        if len(row)==5:
            #fix simple en
            [dbname, domain, server, lang, family] = row
            if lang=="simple-en":
                lang="simple"
            if family=="species":
                lang="species"
            projects.append([dbname, domain, server, lang, family])
    cursor.close()
    conn.close()
    return projects

def main():
    users = []
    bots = loadUnflaggedBots()
    projects = loadProjects()
    
    for dbname, domain, server, lang, family in projects:
        #if lang=="am":
        #    break
        try:
            t1 = time.time()
            conn2 = MySQLdb.connect(host='sql-s%s' % server, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
            cursor2 = conn2.cursor()
            cursor2.execute("select user_name, user_editcount from user where user_editcount!=0 order by user_editcount desc limit %s;" % limit)
            result2 = cursor2.fetchall()
            print domain, time.time()-t1, "seconds"
        
            for row2 in result2:
                user_name = unicode(row2[0], "utf-8")
                user_editcount = row2[1]
                users.append([user_editcount, user_name, domain, lang, family])
            cursor2.close()
            conn2.close()
            
            lang2=lang
            family2=family
            if lang2=='en-simple':
                lang2='simple'
            elif lang2=='en' and family=='wikispecies':
                lang2='species'
                family2='species'
            bots2 = tarea000.botList(wikipedia.Site(lang2, family2))
            for bot in bots2:
                bots.append('%s;%s;%s' % (lang, family, bot))
        except:
            print "error", lang, family, domain
            
    users.sort()
    users.reverse()

    #hide users
    hidepage=wikipedia.Page(site, u"%s/Anonymous" % wtitle)
    m=re.compile(ur"(?i)\[\[\s*User\s*:\s*(?P<user>[^\]\|]+?)\s*[\|\]]").finditer(hidepage.get())
    hidden=[]
    for i in m:
        hidden.append(i.group("user"))

    print len(hidden), "usuarios ocultos"

    output=u"{{/begin|%s}}\n<center>\n{| class='wikitable sortable' style='text-align: center;' \n! # !! User !! Project !! Edits" % limit
    outputbot=u"{{/begin|%s}}\n<center>\n{| class='wikitable sortable' style='text-align: center;' \n! # !! User !! Project !! Edits" % limit
    c=1
    cbots=1
    for user_editcount, user_name, domain, lang, family in users:
        prefix=u""
        if family in ["commons", "wikispecies"]:
            prefix=family
        else:
            lang2=lang
            if lang2=='en-simple':
                lang2='simple'
            prefix=u"%s:%s" % (family, lang2)
        # no usamos regexp porque algunos nicks de bots contienen ( ) u otros
        isBot=False
        for botline in bots:
            if botline=='%s;%s;%s' % (lang, family, user_name) or \
               botline=='*;%s;%s' % (family, user_name) or \
               botline=='%s;*;%s' % (lang, user_name) or \
               botline=='*;*;%s' % (user_name):
                isBot=True
        if hidden.count(user_name)>0: # usuario oculto
            if not isBot: #no es bot
                if c<=limit:
                    output+=u"\n|-\n| %d || [Placeholder] || %s || %d " % (c, domain, user_editcount)
                    c+=1
            #sea bot o no
            if cbots<=limit:
                outputbot+=u"\n|-\n| %d || [Placeholder] || %s || %d " % (cbots, domain, user_editcount)
                cbots+=1
        else: #usuario no oculto
            if not isBot: #no es bot
                if c<=limit:
                    output+=u"\n|-\n| %d || [[%s:User:%s|%s]] || %s || [[%s:Special:Contributions/%s|%d]] " % (c, prefix, user_name, user_name, domain, prefix, user_name, user_editcount)
                    c+=1
            #sea bot o no
            if cbots<=limit:
                outputbot+=u"\n|-\n| %d || [[%s:User:%s|%s]] || %s || [[%s:Special:Contributions/%s|%d]] " % (cbots, prefix, user_name, user_name, domain, prefix, user_name, user_editcount)
                cbots+=1
        if c>limit and cbots>limit:
            break
    output+=u"\n|}\n</center>\n{{/end}}"
    outputbot+=u"\n|}\n</center>\n{{/end}}"
    wiii=wikipedia.Page(site, wtitle)
    wiii.put(output, u"BOT - Updating ranking")
    wiii=wikipedia.Page(site, u"%s (bots included)" % wtitle)
    wiii.put(outputbot, u"BOT - Updating ranking")

if __name__ == "__main__":
    main()
