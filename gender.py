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
if family == 'wikispecies':
    site = wikipedia.Site(lang, 'species')
else:
    site = wikipedia.Site(lang, family)

print lang, family, dbname, server
conn = MySQLdb.connect(host='%s-fast' % server, read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("use %s;" % dbname)
cursor.execute("select user_name, user_editcount from user where user_editcount>=10 order by user_editcount desc limit %d;" % (limit*2))
result = cursor.fetchall()
cursor.close()
conn.close()

bots = botList(site)

users = []
edits = {}
for row in result:
    if len(users) < limit:
        try:
            nick = nick_ = unicode(row[0], 'utf-8')
        except:
            nick = nick_ = unicode(row[0], 'iso-8859-1')
        nick = re.sub('_', ' ', nick)
        nick_ = re.sub(' ', '_', nick_)
        if nick in bots or nick_ in bots:
            continue
        ed = int(row[1])
        users.append(nick)
        edits[nick] = ed

users.sort()
users.reverse()
print lang, family, len(users), 'usuarios'

#genders
genders = {}
c = 0
jump = 50
while c < len(users):
    c += jump
    #http://en.wikipedia.org/w/api.php?action=query&list=users&ususers=brion|TimStarling&usprop=groups|editcount|gender
    userschunk = users[c-jump:c]
    query = wikipedia.query.GetData({'action':'query', 'list':'users', 'ususers':'|'.join(userschunk), 'usprop':'gender'}, site=site, useAPI=True)
    for user in query['query']['users']:
        if user['name'] in users and user.has_key('gender'):
            genders[user['name']] = user['gender']
        else:
            print "Error retrieving gender:", user['name']
            print userschunk

male = 0
female = 0
unknown = 0
for user in users:
    if user not in bots and genders.has_key(user):
        #print user, genders[user], edits[user]
        if genders[user] == 'male':
            male += 1
        elif genders[user] == 'female':
            female += 1
        elif genders[user] == 'unknown':
            unknown += 1
        else:
            print "Value error for", user

print 'male =', male, ', female =', female, ', unknown =', unknown, ', 1 woman per', male/female, 'men'
