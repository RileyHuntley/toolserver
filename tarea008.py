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

import datetime, time
import os, re, wikipedia, sys
import tarea000
import MySQLdb

delay=5
minimumedits=100 #edits to appear in the ranking, para evitar que aparezcan muchos usuarios con pocas ediciones
minimumusers=10 #para evitar listas de 2 personas
daily=False
dailylimit=100000
if len(sys.argv)>1:
    if sys.argv[1].startswith('--daily'):
        daily=True

table_header=u"{| class='wikitable sortable' style='text-align:center;'\n! #\n! User\n! Edits\n"
table_footer=u"|}"
optouttext=u"Users who don't wish to be on this list can add themselves to this [[meta:User:Emijrp/List of Wikimedians by number of edits/Anonymous|anonymizing list]] for future versions."
begin=u"''Please, translate this into your language and delete the english text'': This table shows '''first {{{1}}} users with more edits''' in this Wikipedia. Bots are not included.\n\n''If you want to change page title, contact to [[:es:User talk:Emijrp]]. Thanks.''\n\n<center>\n%s" % table_header
begin2=u"''Please, translate this into your language and delete the english text'': This table shows '''first {{{1}}} users with more edits''' in this Wikipedia. Bots are included.\n\n''If you want to change page title, contact to [[:es:User talk:Emijrp]]. Thanks.''\n\n<center>\n%s" % table_header
end=u"%s\n</center>\n\n''Please, put here a category similar to <nowiki>[[Category:Wikipedia statistics]]</nowiki>.''" % table_footer

"""\n\n[[cs:Wikipedie:Nejaktivnější wikipedisté]]\n[[de:Wikipedia:Beitragszahlen]]\n[[es:Wikipedia:Lista de wikipedistas por número de ediciones]]\n[[fr:Wikipédia:Liste des Wikipédiens par nombre d'éditions]]\n[[zh-classical:維基大典:編輯次數]]\n[[id:Wikipedia:Daftar pengguna menurut jumlah suntingan]]\n[[is:Wikipedia:Notendur eftir breytingafjölda]]\n[[he:ויקיפדיה:נתונים סטטיסטיים/משתמשים/1-100]]\n[[jv:Wikipedia:Daftar panganggo miturut cacahé suntingan]]\n[[ka:ვიკიპედია:ვიკიპედიელები აქტიურობის მიხედვით]]\n[[lt:Vikipedija:Naudotojai pagal keitimų skaičių]]\n[[hu:Wikipédia:Szerkesztők listája szerkesztésszám szerint]]\n[[ja:Wikipedia:編集回数の多いウィキペディアンの一覧]]\n[[pl:Wikipedia:Najaktywniejsi wikipedyści]]\n[[pt:Wikipedia:Lista de wikipedistas por número de edições]]\n[[sq:Wikipedia:Lista e Wikipedianëve sipas redaktimeve]]\n[[uk:Вікіпедія:Найактивніші]]\n[[bat-smg:Vikipedėjė:Nauduotuojē palē keitėmu skaitliu]]\n[[zh:Wikipedia:最多贡献的用户]]"
"""

end2=end

noflagrequired=[
    ['ca', 'wikipedia'], #fix buscar diff donde diga que no hace falta flag
]

tras1={
'wikipedia': {
    u"default": u"User:Emijrp/List of Wikipedians by number of edits",
    u"ar": u"قائمة الويكيبيديين حسب عدد التعديلات",
    u"arz": u"List of Wikipedians by number of edits",
    u"ca": u"Llista de viquipedistes per nombre d'edicions",
    u"da": u"Wikipedianere efter antal redigeringer",
    u"eo": u"Listo de uzantoj laŭ redaktonombro",
    u"es": u"Ranking de ediciones", 
    u"fa": u"فهرست کاربران ویکی‌پدیا بر اساس تعداد ویرایش‌ها",
    u"fi": u"Luettelo Wikipedian käyttäjistä muokkausmäärän mukaan",
    #u"fr": u"Utilisateurs par nombre d'éditions", 
    u"gl": u"Estatísticas/Lista de usuarios por número de edicións",
    u"hr": u"Popis Wikipedista po broju uređivanja",
    u"ht": u"Lis Wikipedyen pa nonm edisyon yo fè",
    u"hu": u"Wikipédisták listája szerkesztésszám szerint",
    u"ko": u"편집횟수 순 사용자 목록",
    u"pl": u"Użytkownicy według liczby edycji",
    u"ro": u"Lista wikipediştilor după numărul de editări",
    u"simple": u"List of Wikipedians by number of changes",
    u"sl": u"Seznam Wikipedistov po številu urejanj",
    u"sv": u"Lista över Wikipedia-användare sorterad efter antalet redigeringar",
    u"th": u"รายชื่อชาววิกิพีเดียที่แก้ไขมากที่สุด 500 อันดับ",
    u"tr": u"Değişiklik sayılarına göre Vikipedistler listesi",
    u"vi": u"Danh sách thành viên Wikipedia theo số lần sửa trang",
    },
'wiktionary': {
    u"es": u"Ranking de ediciones",     
    u"simple": u"List of Wiktionarians by number of changes",
    },
'wikinews': {
    u"es": u"Ranking de ediciones", 
    },
}

tras2={
'wikipedia': {
    u"default": u"User:Emijrp/List of Wikipedians by number of edits (bots included)",
    u"ar": u"قائمة الويكيبيديين حسب عدد التعديلات (متضمنة البوتات)",
    u"arz": u"List of Wikipedians by number of edits (bots included)",
    u"ca": u"Llista de viquipedistes per nombre d'edicions (bots inclosos)",
    u"da": u"Wikipedianere efter antal redigeringer (bots inkluderet)",
    u"eo": u"Listo de uzantoj laŭ redaktonombro (inkluzivante robotojn)",
    u"es": u"Ranking de ediciones (incluye bots)", 
    #u"fr": u"Utilisateurs par nombre d'éditions (bots inclus)", 
    u"gl": u"Estatísticas/Lista de usuarios por número de edicións (bots incluídos)",
    u"hr": u"Popis Wikipedista po broju uređivanja (botovi uključeni)",
    u"hu": u"Wikipédisták listája szerkesztésszám szerint (botokkal)",
    u"ko": u"편집횟수 순 사용자 목록 (봇 포함)",
    u"pl": u"Użytkownicy według liczby edycji (w tym boty)",
    u"ro": u"Lista wikipediştilor după numărul de editări (inclusiv roboţi)",
    u"simple": u"List of Wikipedians by number of changes (bots included)",
    u"sl": u"Seznam Wikipedistov po številu urejanj (z boti)",
    u"sv": u"Lista över Wikipedia-användare sorterad efter antalet redigeringar (inklusive robotar)",
    u"th": u"รายชื่อชาววิกิพีเดียที่แก้ไขมากที่สุด 500 อันดับ (รวมบอต)",
    u"tr": u"Değişiklik sayılarına göre Vikipedistler listesi (botlar dahil)",
    u"vi": u"Danh sách thành viên Wikipedia theo số lần sửa trang (tính cả bot)",
    },
'wiktionary': {
    u"es": u"Ranking de ediciones (incluye bots)", 
    },
'wikinews': {
    u"es": u"Ranking de ediciones (incluye bots)", 
    },
}

#do not want: nl, simple 
# fix: hr
tt100={'rankingusers':True, 'rankingbots':True, 'limit':100, 'optout':''}
tt500={'rankingusers':True, 'rankingbots':True, 'limit':500, 'optout':''}
projects={
    'wikinews': {
        'es': tt100,
        },
    'wikipedia': {
        'ar': tt500,
        'arz': tt100,
        'ca': tt500,
        'da': tt500,
        'en': {'rankingusers':True, 'rankingbots':True, 'limit':500, 'optout':'Wikipedia:List of Wikipedians by number of edits/Anonymous'},
        'eo': tt500,
        'es': tt500,
        'fr': tt500,
        'gl': tt100,
        'hr': tt500,
        'ht': tt100,
        'ro': tt500,
        'simple': tt500,
        'sl': tt100,
        'th': tt500,
        'tr': tt500,
        'vi': tt500,
        },
    'wiktionary': {
        'es': tt100,
        'simple': {'rankingusers':True, 'rankingbots':False, 'limit':100, 'optout':''},
        },
}

"""
    'wikinews': {
        'es': tt100,
        },
    'wikipedia': {
        'ar': tt500,
        'ca': tt500,
        'da': tt500,
        'eo': tt500,
        'es': tt500,
        'gl': tt100,
        'hr': tt500,
        'ht': tt100,
        'ro': tt500,
        'simple': tt500,
        'sl': tt100,
        'th': tt500,
        'tr': tt500,
        'vi': tt500,
        },
    'wiktionary': {
        'es': tt100,
        'simple': {'rankingusers':True, 'rankingbots':False, 'limit':100, 'optout':''},
        },

"""

#metemos el resto de idiomas
#descomentar cuando arregle el fallo de _mysql_exceptions.OperationalError: (1040, 'Too many connections')
for lang in tarea000.getLangsByFamily('wikipedia'):
    if lang=='en-simple':
        lang='simple'
    if not projects['wikipedia'].has_key(lang):
        projects['wikipedia'][lang]=tt100

#generating interwikis
iws1={}
iws2={}
for family, langs in projects.items():
    iws1[family]=[]
    iws2[family]=[]
    for lang, v in langs.items():
        if tarea000.isExcluded('tarea008', family, lang):
            continue
        wikipedianm=tarea000.getNamespaceName(lang, family, 4)
        if projects[family][lang]['rankingusers']:
            traslation1=""
            if tras1[family].has_key(lang):
                traslation1=u"%s:%s" % (wikipedianm, tras1[family][lang])
            else:
                traslation1=tras1[family]['default']
            iws1[family].append(u"[[%s:%s]]" % (lang, traslation1))
        if projects[family][lang]['rankingbots']:
            traslation2=""
            if tras2[family].has_key(lang):
                traslation2=u"%s:%s" % (wikipedianm, tras2[family][lang])
            else:
                traslation2=tras2[family]['default']
            iws2[family].append(u"[[%s:%s]]" % (lang, traslation2))
    iws1[family].sort()
    iws2[family].sort()

conns={}
for server in tarea000.getServers():
    conns[server]=MySQLdb.connect(host=server, read_default_file='~/.my.cnf', use_unicode=True)

for family, langs in projects.items():
    for lang, v in langs.items():
        print family, lang
        if tarea000.isExcluded('tarea008', family, lang):
            continue
        
        title=u''
        #la lista de bots debe ir dentro del bucle, ya que se llena con más bots de cada caso
        #meter en unflagged? #fix
        bots=[u'BOTpolicia', u'AVBOT', u'CommonsDelinker', u'Eskimbot', u'EmxBot', u'YurikBot', u'H-Bot', u'Paulatz bot', u'TekBot', u'Alfiobot', u'RoboRex', u'Agtbot', u'Felixbot', u'Pixibot', u'Sz-iwbot', u'Timbot (Gutza)', u'Ginosbot', u'GrinBot', u'.anacondabot', u'Omdirigeringsrättaren', u'Rubinbot', u'HasharBot', u'NetBot', u"D'ohBot", u'Byrialbot', u'Broadbot', u'Guanabot', u'Chris G Bot 2', u'CCyeZBot', u'Soulbot', u'MSBOT', u'GnawnBot', u'Chris G Bot 3', u'Huzzlet the bot', u'JCbot', u'DodekBot', u'John Bot II', u'CyeZBot', u'Beefbot', u'Louperibot', u'SOTNBot', u'DirlBot', u'Obersachsebot', u'WikiDreamer Bot', u'YonaBot', u'Chlewbot', u'PixelBot', u'ToePeu.bot', u'HujiBot', u'Le Pied-bot', u'Ugur Basak Bot', u'NigelJBot', u'CommonsTicker', u'Tangobot', u'SeanBot', u'Corrector de redirecciones', u'HermesBot', u'Darkicebot', u'RedBot', u'HerculeBot', u'PatruBOT', u'RobotGMwikt', u'MonoBot', u'WikimediaNotifier', u'SBot39', u'DSisyphBot', u'GriffinBot1', u'WeggeBot', u'EhJBot3', u'Gerakibot', u'Picochip08', u'MondalorBot', u'Redirect fixer', u'Skagedalobot', u'EhJBot3', u'Tsca.bot'] #no meter a BOTijo, sino el summary no funciona diferente para las wikis donde no tengo flag no va
        
        try:
            site=wikipedia.Site(lang, family)
        except:
            print "Error", lang, family
            continue
        
        #usuarios que no quiere aparecer en los rankings
        optouts=[]
        for optoutsite, optoutpagetitle in {wikipedia.Site('meta', 'meta'): 'User:Emijrp/List of Wikimedians by number of edits/Anonymous', site: projects[family][lang]['optout'], }.items():
            if optoutpagetitle!='':
                optoutpage=wikipedia.Page(optoutsite, optoutpagetitle)
                if optoutpage.exists() and not optoutpage.isRedirectPage():
                    mm=re.compile(ur"\[\[ *[^\:]+? *\: *(?P<useroptout>[^\]\|]+?) *[\]\|]").finditer(optoutpage.get())
                    for ii in mm:
                        optouts.append(ii.group("useroptout"))
        print "Excluidos", optouts
        bots+=tarea000.botList(site)
        bots+=tarea000.unflaggedBotsList(site)
        admins=tarea000.adminList(site)
        wikipedianm=tarea000.getNamespaceName(lang, family, 4)
        articleCount=tarea000.getArticleCount(lang, family)
        print articleCount
        if (daily and articleCount<dailylimit) or (daily and lang=='vo'):
            #evitamos actualizar excesivamente proyectos pequeños
            print "Skip"
            continue
        dbname=tarea000.getDbname(lang, family)
        time.sleep(0.5)
        server=tarea000.getServer(lang, family)
        time.sleep(0.5)
        #conn = MySQLdb.connect(host='sql-s%s' % server, read_default_file='~/.my.cnf', use_unicode=True)
        cursor = conns[server].cursor()
        cursor.execute("use %s;" % dbname) #tiene que ser separado en dos lineas
        cursor.execute("select user_name, user_editcount from user where user_editcount!=0 order by user_editcount desc limit 5000;")
        result=cursor.fetchall()
        cursor.close()
        #conn.close()
        time.sleep(0.5)
        
        s=u""
        sbots=u""
        c=1
        cbots=1
        cplanti2=1
        cuantos=projects[family][lang]['limit']
        planti2=u"{{#switch:{{{1|User}}}\n"
        planti=u"{| class='wikitable sortable' style='font-size: 90%;text-align: center;float: right;'\n! #\n! Usuario\n! Ediciones\n"
        bot_r=re.compile(ur"(?m)(^([Rr][Oo])?[Bb][Oo][Tt] | ([Rr][Oo])?([Bb][Oo][Tt])$|[a-z0-9\.\- ]([Rr][Oo])?(Bot|BOT)$|^([Rr][Oo])?BOT[a-z0-9\.\- ])")
        for row in result:
            nick=unicode(row[0], 'utf-8')
            ed=int(row[1])
            if ed<minimumedits and c>minimumusers: #al menos minimumusers, aunque no tengan ni el minimumedits necesario
                continue

            if optouts.count(nick)==0:
                if bots.count(nick)>0 or re.search(bot_r, nick): #primero miramos si es bot, para evitar mostrar admins bots comoo Cydebot
                    if c<=10:
                        pass #no bots in the top 10 template
                    if c<=cuantos:
                        pass #no bots in this ranking
                    if cbots<=cuantos:
                        sbots+=u"|-\n| %d || [[User:%s|%s]] (Bot) || [[Special:Contributions/%s|%d]] \n" % (cbots,nick,nick,nick,ed)
                        cbots+=1
                elif admins.count(nick)>0:
                    if c<=10:
                        planti+=u"|-\n| %d || [[User:%s|%s]] (Admin) || [[Special:Contributions/%s|%d]] \n" % (c,nick,nick,nick,ed)
                        #no poner c+=1 sino incrementa dos veces
                    if c<=cuantos:
                        s+=u"|-\n| %d || [[User:%s|%s]] (Admin) || [[Special:Contributions/%s|%d]] \n" % (c,nick,nick,nick,ed)
                        c+=1
                    if cbots<=cuantos:
                        sbots+=u"|-\n| %d || [[User:%s|%s]] (Admin) || [[Special:Contributions/%s|%d]] \n" % (cbots,nick,nick,nick,ed)
                        cbots+=1
                else:
                    if c<=10:
                        planti+=u"|-\n| %d || [[User:%s|%s]] || [[Special:Contributions/%s|%d]] \n" % (c,nick,nick,nick,ed)
                        #no poner c+=1 sino incrementa dos veces
                    if c<=cuantos:
                        s+=u"|-\n| %d || [[User:%s|%s]] || [[Special:Contributions/%s|%d]] \n" % (c,nick,nick,nick,ed)
                        c+=1
                    if cbots<=cuantos:
                        sbots+=u"|-\n| %d || [[User:%s|%s]] || [[Special:Contributions/%s|%d]] \n" % (cbots,nick,nick,nick,ed)
                        cbots+=1
            elif optouts.count(nick)>0:
                if c<=10:
                    planti+=u"|-\n| %d || [Placeholder] || %d \n" % (c,ed)
                    #no poner c+=1 sino incrementa dos veces
                if c<=cuantos:
                    s+=u"|-\n| %d || [Placeholder] || %d \n" % (c,ed)
                    c+=1
                if cbots<=cuantos:
                    sbots+=u"|-\n| %d || [Placeholder] || %d \n" % (cbots,ed)
                    cbots+=1

            if cplanti2<=2500: #plantilla ediciones
                if optouts.count(nick)==0:    
                    planti2+=u"|%s=%s\n" % (nick,ed)
                    cplanti2+=1
        
        planti2+=u"|USUARIO DESCONOCIDO\n}}<noinclude>{{uso de plantilla}}</noinclude>"
        planti+=u"|-\n| colspan=3 | Véase también [[Wikipedia:Ranking de ediciones]]<br/>Actualizado a las {{subst:CURRENTTIME}} (UTC) del  {{subst:CURRENTDAY}}/{{subst:CURRENTMONTH}}/{{subst:CURRENTYEAR}} por [[Usuario:BOTijo|BOTijo]] \n|}<noinclude>{{uso de plantilla}}</noinclude>"
        
        resume=u""
        if bots.count(u"BOTijo") or noflagrequired.count([lang, family])>0:
            resume=u"BOT - Updating ranking"
        else:
            resume=u"BOT - Updating ranking (This bot [[User:BOTijo|only makes a few edits in user subpages]]. Please, don't block. Contact to [[w:es:User talk:Emijrp]])"
        
        
        #first ranking
        if projects[family][lang]['rankingusers']:
            title=u''
            if tras1[family].has_key(lang) and tras1[family][lang]:
                title=u"%s:%s" % (wikipedianm, tras1[family][lang])
                page=wikipedia.Page(site, u"%s/begin" % title)
                if projects[family][lang]['rankingusers'] and not page.exists():
                    page.put(begin, resume)
                    time.sleep(delay)
                page=wikipedia.Page(site, u"%s/end" % title)
                if projects[family][lang]['rankingusers'] and not page.exists():
                    page.put(end, resume)
                    time.sleep(delay)
                s=u"{{/begin|%d}}\n%s{{/end}}\n%s" % (cuantos, s, "\n".join(iws1[family]))
            else: #by default
                title=tras1[family]['default']
                s=u"For a list including bots, see [[%s]].\n\nFor a global list, see [[meta:User:Emijrp/List of Wikimedians by number of edits]].\n\n%s\n\nThis page was last updated in '''{{subst:CURRENTYEAR}}-{{subst:CURRENTMONTH}}-{{subst:CURRENTDAY2}}'''.\n\n%s%s%s\n%s" % (tras2[family]['default'], optouttext, table_header, s, table_footer, "\n".join(iws1[family]))
            #eliminamos autointerwiki
            s=re.sub(ur"(?im)\[\[%s:.*?\]\](\n|$)" % lang, ur"", s)
            page=wikipedia.Page(site, title)
            if projects[family][lang]['rankingusers'] and ((not page.exists()) or (not page.isRedirectPage() and not page.isDisambig() and page.get()!=s and int(page.getVersionHistory(revCount=1)[0][1][8:10])!=datetime.datetime.now().day)):# [0][1] es el timestamp de la última versión del historial, [8:10] es el día del mes, evitamos actualizar dos veces el mismo día
                page.put(s, resume)
                time.sleep(delay)
        
        #second ranking
        if projects[family][lang]['rankingbots']:
            title=u''
            if tras2[family].has_key(lang) and tras2[family][lang]:
                title=u"%s:%s" % (wikipedianm, tras2[family][lang])
                page=wikipedia.Page(site, u"%s/begin" % title)
                if projects[family][lang]['rankingbots'] and not page.exists():
                    page.put(begin2, resume)
                    time.sleep(delay)
                page=wikipedia.Page(site, u"%s/end" % title)
                if projects[family][lang]['rankingbots'] and not page.exists():
                    page.put(end2, resume)
                    time.sleep(delay)
                sbots=u"{{/begin|%d}}\n%s{{/end}}\n%s" % (cuantos, sbots, "\n".join(iws2[family]))
            else: #by defect
                title=tras2[family]['default']
                sbots=u"For a list excluding bots, see [[%s]].\n\nFor a global list, see [[meta:User:Emijrp/List of Wikimedians by number of edits]].\n\n%s\n\nThis page was last updated in '''{{subst:CURRENTYEAR}}-{{subst:CURRENTMONTH}}-{{subst:CURRENTDAY2}}'''.\n\n%s%s%s\n%s" % (tras1[family]['default'], optouttext, table_header, sbots, table_footer, "\n".join(iws2[family]))
            #eliminamos autointerwiki
            sbots=re.sub(ur"(?im)\[\[%s:.*?\]\]\n" % lang, ur"", sbots)
            page=wikipedia.Page(site, title)
            if projects[family][lang]['rankingbots'] and ((not page.exists()) or (not page.isRedirectPage() and not page.isDisambig() and page.get()!=sbots and int(page.getVersionHistory(revCount=1)[0][1][8:10])!=datetime.datetime.now().day)):# [0][1] es el timestamp de la última versión del historial, [8:10] es el día del mes, evitamos actualizar dos veces el mismo día
                page.put(sbots, resume)
                time.sleep(delay)
        
        #otras plantillas
        if lang=='es':
            page=wikipedia.Page(site, u"Template:RankingEdiciones")
            page.put(planti, resume)
            
            page=wikipedia.Page(site, u"Template:Ediciones")
            page.put(planti2, resume)

for server, conn in conns.items():
    print "Cerrando conexion con", server
    conn.close()

