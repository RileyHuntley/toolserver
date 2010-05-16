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

# clear;python svn-gource.py --filter-dirs gourceforwiki.log > gourceforwikib.log;gource --log-format custom gourceforwikib.log -s 4

import wikipedia,re,sys,os,gzip,time
import MySQLdb
import math
import datetime
import sets

start='<?xml version="1.0"?>\n<log>\n'
end='</log>'

f=open("gourceforwiki.log", "w")
f.write(start)
conn = MySQLdb.connect(host='sql-s3', db='eswiki_p', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
limit=100000
cursor.execute("SELECT rc_id, rc_user_text, rc_timestamp, rc_title from recentchanges where rc_namespace=0 and rc_deleted=0 order by rc_timestamp asc limit %d;" % limit)
#cursor.execute("SELECT rev_id, rev_user_text, rev_timestamp, page_title from revision inner join page on rev_page=page_id where page_namespace=0 order by rev_timestamp asc limit %d;" % limit)
result=[]

pages=sets.Set()
creations=sets.Set()
while True:
    row = cursor.fetchone()
    if row == None:
        break
    page_title=row[3]
    page_title=re.sub("/", " ", page_title)
    rc_timestamp=row[2]
    if page_title not in pages:
        creations.add('%s%s' % (page_title, rc_timestamp))
        pages.add(page_title)
    result.append(row)
result.reverse()

c=0
rows=len(result)
for row in result:
    c+=1
    if c % 10000 == 0:
        print c
    if len(row)==4:
        rc_id=row[0]
        rc_author=row[1]
        rc_timestamp=t=row[2]
        t="%s-%s-%sT%s:%s:%s.000000Z" % (t[0:4], t[4:6], t[6:8], t[8:10], t[10:12], t[12:14])
        #print rc_timestamp
        rc_title=row[3]
        rc_title=re.sub("/", " ", rc_title)
        
        action="M"
        creation='%s%s' % (rc_title, rc_timestamp)
        if creation in creations:
            action="A"
        
        logentry="""<logentry
           revision="%d">
        <author>%s</author>
        <date>%s</date>
        <paths>
        <path
           kind=""
           action="%s">%s</path>
        </paths>
        <msg></msg>
        </logentry>\n""" % ((rows-c+1), rc_author, t, action, rc_title)
        
        logentry=re.sub("&", "&amp;", logentry)
        logentry=re.sub("_", " ", logentry)
        
        #print logentry
        try:
            f.write(logentry.encode("utf-8"))
        except:
            try:
                f.write(logentry)
            except:
                print 'Error'
                pass

conn.close()
cursor.close()
f.write(end)
f.close()