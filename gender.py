#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

# Copyright (C) 2011 emijrp

import MySQLdb
import sys
from tarea000 import *

lang = sys.argv[1]
family = sys.argv[2]
limit = int(sys.argv[3])
dbname = getDbname(lang, family)
server = getServer(lang, family)
site = wikipedia.Site(lang, family)

conn = MySQLdb.connect(host='%s-fast' % server, read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("use %s;" % dbname)
cursor.execute("select user_name, user_editcount from user where user_editcount!=0 order by user_editcount desc limit %d;" % (limit))
result = cursor.fetchall()
cursor.close()
conn.close()

users = []
edits = {}
for row in result:
    nick = nick_ = unicode(row[0], 'utf-8')
    nick = re.sub('_', ' ', nick)
    nick_ = re.sub(' ', '_', nick_)
    ed = int(row[1])
    users.append(nick)
    edits[nick] = ed

users.sort()
users.reverse()
bots = botList(site)

#genders
genders = {}
c = 0
while c < len(users):
    c += 10
    #http://en.wikipedia.org/w/api.php?action=query&list=users&ususers=brion|TimStarling&usprop=groups|editcount|gender
    query = wikipedia.query.GetData({'action':'query', 'list':'users', 'ususers':'|'.join(users[c-10:c]), 'usprop':'gender'}, site=site, useAPI=True)
    for user in query['query']['users']:
        if user['name'] in users:
            genders[user['name']] = user['gender']
        else:
            print "Error", user['name']

male = 0
female = 0
unknown = 0
for user in users:
    if user not in bots:
        #print user, genders[user], edits[user]
        if genders[user] == 'male':
            male += 1
        elif genders[user] == 'female':
            female += 1
        elif genders[user] == 'unknown':
            unknown += 1
        else:
            print "Error", user

print 'male =', male, ', female =', female, ', unknown =', unknown, ', 1 woman per', male/female, 'men'
