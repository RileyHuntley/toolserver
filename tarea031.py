#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
 
import wikipedia
import MySQLdb
import time, datetime

limite=7
minedits=25
timestamp=datetime.datetime.today()-datetime.timedelta(days=limite)
timestamplimite=u'%s%s%s000000' % (timestamp.year, timestamp.month, timestamp.day)

site = wikipedia.Site('es', 'wikipedia')
 
conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf')
cursor = conn.cursor()
sqlquery='select concat("| [[User:",rc_user_text,"|",rc_user_text,"]] \n| [[User talk:",rc_user_text,"|Disc]] \n| [[Special:Contributions/",rc_user_text,"|",user_editcount,"]] \n|-") from recentchanges, user where rc_timestamp>%s and rc_user_text=user_name and user_editcount>%s and not rc_user_text regexp "[Bb]ot" and replace(rc_user_text, " ", "_") not in (select page_title from page where page_namespace=3) and replace(rc_user_text, " ", "_") not in (select log_title from logging where log_namespace=2 and log_action="block") group by rc_user_text;' % (timestamplimite, minedits)
cursor.execute(sqlquery)
 
query = [unicode(row[0], 'utf-8') for row in cursor.fetchall()]
page_list = []
for i, page in enumerate(query): page_list.append(u'| %d \n%s' % (i + 1, page))
 
report = wikipedia.Page(site, u'User:Emijrp/Bienvenidas')
report.put(u'{{/begin}}\n\n<center>\n{| class=\"wikitable ' +
u'sortable\" style=\"text-align: center;\"\n! #\n! Usuario\n! Discusión\n! Ediciones\n|-\n' + 
'\n'.join(page_list) + '\n|}\n</center>\n*sql query: <code><nowiki>%s</nowiki></code>\n\n{{/end}}' % sqlquery, u'BOT - Actualizando informe', None, False)
cursor.close()
conn.close()
 
wikipedia.stopme()
