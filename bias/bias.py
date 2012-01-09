#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re
import os
import sys
import time
import MySQLdb

# trying to put some light on wiki bias, not only gender bias

path="/home/emijrp/public_html/bias"
conn = MySQLdb.connect(host='sql-s1', db='toolserver', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("SELECT lang, family, CONCAT('sql-s', server) AS dbserver, dbname FROM toolserver.wiki WHERE 1;")
result = cursor.fetchall()
checked = 0
families = ["wikibooks", "wikipedia", "wiktionary", "wikimedia", "wikiquote", "wikisource", "wikinews", "wikiversity", "commons", "wikispecies"]
ranking = []
for row in result:
    time.sleep(0.1)
    lang = row[0]
    family = row[1]
    if family not in families:
        continue
    dbserver = row[2] + "-fast"
    dbname = row[3]
    
    try:
        conn2 = MySQLdb.connect(host=dbserver, db=dbname, read_default_file='~/.my.cnf', use_unicode=True)
        cursor2 = conn2.cursor()
        #print "OK:", dbserver, dbname
        cursor2.execute("SELECT up_value, count(*) AS count FROM user_properties WHERE up_property='gender' GROUP BY up_value")
        result2 = cursor2.fetchall()
        male = 0
        female = 0
        for row2 in result2:
            if row2[0] == 'male':
                male = int(row2[1])
            elif row2[0] == 'female':
                female = int(row2[1])
        
        ranking.append([female/((male+female)/100.0), lang, family, male+female, male, female])
        ranking.sort()
        ranking.reverse()
        print '#'*50
        limit = 25
        if len(ranking) >= limit:
            for i in range(limit):
                print '|', ' || '.join([str(v) for v in ranking[i]])
                print '|-'
        
        cursor2.close()
        conn2.close()
    except:
        print "Error in", dbserver, dbname


cursor.close()
conn.close()


