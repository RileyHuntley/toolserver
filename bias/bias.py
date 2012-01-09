#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re
import os
import sys
import time
import MySQLdb

# trying to put some light on wiki bias, not only gender bias

def domain(lang, family):
    if family == 'commons':
        return 'http://commons.wikimedia.org'
    else:
        return 'http://%s.%s.org' % (lang, family)

path = "/home/emijrp/public_html/bias"
conn = MySQLdb.connect(host='sql-s1', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT lang, family, CONCAT('sql-s', server) AS dbserver, dbname FROM toolserver.wiki WHERE 1 ORDER BY lang;")
result = cursor.fetchall()
checked = 0
families = ["wikibooks", "wikipedia", "wiktionary", "wikimedia", "wikiquote", "wikisource", "wikinews", "wikiversity", "commons", "wikispecies"]
genderdic = {}
for row in result:
    time.sleep(0.1)
    lang = row[0]
    family = row[1]
    if family not in families:
        continue
    dbserver = row[2] + "-fast"
    dbname = row[3]
    
    #if checked > 15:
    #    break
    
    try:
        conn2 = MySQLdb.connect(host=dbserver, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
        cursor2 = conn2.cursor()
        #print "OK:", dbserver, dbname
        cursor2.execute("SELECT up_value, count(*) AS count FROM user_properties WHERE up_property='gender' GROUP BY up_value")
        result2 = cursor2.fetchall()
        for row2 in result2:
            gender = row2[0].lower()
            count = int(row2[1])
            print family, lang, gender, count
            if genderdic.has_key(family):
                if genderdic[family].has_key(lang):
                    genderdic[family][lang][gender] += count
                else:
                    genderdic[family][lang] = {'female': 0, 'male': 0}
                    genderdic[family][lang][gender] += count
            else:
                genderdic[family] = { lang: {'female': 0, 'male': 0}}
                genderdic[family][lang][gender] += count
        
        cursor2.close()
        conn2.close()
        checked += 1
    except:
        print "Error in", dbserver, dbname

cursor.close()
conn.close()

#gendergap
#table 1
l = []
for family, langs in genderdic.items():
    male = 0
    female = 0
    for lang, values in langs.items():
        male += values['male']
        female += values['female']
    l.append([family, male, female, female/((male+female)/100.0)])
l.sort()
gender_table_core1 = u""
for family, males, females, percent in l:
    gender_table_core1 += u"<tr><td>%s</td><td>%d</td><td>%d</td><td>%.2f</td></tr>\n" % (family, males, females, percent)
gender_table1 = u"""<table align=center class="sortable" style="text-align: center;">\n<tr><th>Family</th><th>Male</th><th>Female</th><th>Female (%%)</th></tr>\n%s\n</table>""" % (gender_table_core1)

#table 2
l = []
temp = {}
for family, langs in genderdic.items():
    for lang, values in langs.items():
        if temp.has_key(lang):
            temp[lang]['male'] += values['male']
            temp[lang]['female'] += values['female']
        else:
            temp[lang] = { 'male': values['male'], 'female': values['female'] }
for lang, values in temp.items():
    l.append([lang, values['male'], values['female'], values['female']/((values['male']+values['female'])/100.0)])
l.sort()
gender_table_core2 = u""
for lang, males, females, percent in l:
    gender_table_core2 += u"<tr><td>%s</td><td>%d</td><td>%d</td><td>%.2f</td></tr>\n" % (lang, males, females, percent)
gender_table2 = u"""<table align=center class="sortable" style="text-align: center;">\n<tr><th>Lang</th><th>Male</th><th>Female</th><th>Female (%%)</th></tr>\n%s\n</table>""" % (gender_table_core2)

#table 3
l = []
for family, langs in genderdic.items():
    for lang, values in langs.items():
        l.append([family, lang, values['male'], values['female'], values['female']/((values['male']+values['female'])/100.0)])
l.sort()
gender_table_core3 = u""
for family, lang, males, females, percent in l:
    gender_table_core3 += u"<tr><td>%s</td><td><a href='%s'>%s</a></td><td>%d</td><td>%d</td><td>%.2f</td></tr>\n" % (family, domain(lang, family), lang, males, females, percent)
gender_table3 = u"""<table align=center class="sortable" style="text-align: center;">\n<tr><th>Family</th><th>Lang</th><th>Male</th><th>Female</th><th>Female (%%)</th></tr>\n%s\n</table>""" % (gender_table_core3)

#end gendergap

output = u"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link rel="stylesheet" type="text/css" href="style.css" />
    <script src="sorttable.js" type="text/javascript"></script>
    <title>Biases</title>
</head>
<body>
<p>This page analyzes some possible biases in Wikimedia projects. Tables are sortable (click on headers). %d wikis checked.</p>

<p><i>This page was last modified on <!-- timestamp -->%s<!-- timestamp --> (UTC).</i></p>

<h2>Biography bias</h2>

TODO.

<h2>Gender gap</h2>

<p>A lot have been written about <a href="http://meta.wikimedia.org/wiki/Gender_gap">gender gap and Wikimedia projects</a>. Well, really <a href="http://meta.wikimedia.org/wiki/Category:Gender_gap">not that much</a>, only a few data is available from some surveys and studies. <a href="http://lists.wikimedia.org/pipermail/gendergap/2011-February/000073.html">12.94%% of females (2011)? 7.3%% (2007)?</a> Look the last data.</p>

<table align=center>
<tr><td valign=top>%s %s</td><td valign=top>%s</td></tr>
</table>

<h2>Geography bias</h2>

TODO.

</body>
</html>
""" % (checked, datetime.datetime.now(), gender_table1, gender_table2, gender_table3)

f = open('%s/index.html' % (path), 'w')
f.write(output.encode('utf-8'))
f.close()
