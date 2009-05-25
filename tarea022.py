# -*- coding: utf-8 -*-

import wikipedia,re,sys,os,gzip,time, datetime

def percent(c):
	if c % 1000 == 0:
		wikipedia.output(u'Llevamos %d' % c)

		
site=wikipedia.Site('es', 'wikipedia')

bots=[u'BOTpolicia', u'AVBOT', u'CommonsDelinker', u'Eskimbot']
data=site.getUrl("/w/index.php?title=Special:Listusers&limit=5000&group=bot")
data=data.split('<!-- start content -->')
data=data[1].split('<!-- end content -->')[0]
m=re.compile(ur" title=\".*?:(.*?)\">").finditer(data)
for i in m:
	bots.append(i.group(1))

admins=[]
data=site.getUrl("/w/index.php?title=Special:Listusers&limit=5000&group=sysop")
data=data.split('<!-- start content -->')
data=data[1].split('<!-- end content -->')[0]
m=re.compile(ur" title=\".*?:(.*?)\">").finditer(data)
for i in m:
	admins.append(i.group(1))
	
	
users={}

limite=7
timestamp=datetime.datetime.today()-datetime.timedelta(days=limite)
month=timestamp.month
day=timestamp.day
if int(month)<10:
	month='0%s' % month
if int(day)<10:
	day='0%s' % day
timestamplimite=u'%s%s%s000000' % (timestamp.year, month, day)

print timestamplimite

os.system('mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select rc_user_text from recentchanges where (rc_namespace=0 or rc_namespace=104) and rc_type=0 and rc_bot=0 and rc_timestamp>=%s;" > /home/emijrp/temporal/ultimasedicionesrc.txt' % timestamplimite)
f=open('/home/emijrp/temporal/ultimasedicionesrc.txt', 'r')
c=0
print 'Cargando ediciones de cambios recientes'
for line in f:
	if c==0: #saltamos la primera linea q es el describe de sql
		c+=1
		continue
	line=unicode(line, 'utf-8')
	line=line[:len(line)-1] #evitamos \n
	line=re.sub('_', ' ', line)
	trozos=line.split('	')
	if len(trozos)==1:
		rc_user_text=trozos[0]
		
		if users.has_key(rc_user_text):
			users[rc_user_text]+=1
		else:
			users[rc_user_text]=1
		
		c+=1
		percent(c)
f.close()

users_list = [(v, k) for k, v in users.items()]
users_list.sort()
users_list.reverse()
users_list = [(k, v) for v, k in users_list]


c=0
multiplicador=10
s=u"{{/begin|%s|%s}}\n" % (limite, multiplicador)
for user, edits in users_list:
	if edits>=limite*multiplicador and bots.count(user)==0:
		c+=1
		#wikipedia.output(u'%d) %s - %d' % (c, user, edits))
		if admins.count(user):
			s+=u"|-\n| %s || [[User:%s|%s]] (Admin) || [[User talk:%s|Discusión]] || [[Special:Contributions/%s|Ver]] || %d \n" % (str(c),user,user,user,user,edits)
		else:
			s+=u"|-\n| %s || [[User:%s|%s]] || [[User talk:%s|Discusión]] || [[Special:Contributions/%s|Ver]] || %d \n" % (str(c),user,user,user,user,edits)

s+=u"{{/end}}"
page=wikipedia.Page(site, u'Wikipedia:Usuarios muy activos')
page.put(s, "BOT - Actualizando lista de usuarios muy activos [%d]" % c)




c=0
multiplicador=2
s=u"{{/begin|%s|%s}}\n" % (limite, multiplicador)
for user, edits in users_list:
	if edits>=limite*multiplicador and bots.count(user)==0:
		c+=1
		#wikipedia.output(u'%d) %s - %d' % (c, user, edits))
		if admins.count(user):
			s+=u"|-\n| %s || [[User:%s|%s]] (Admin) || [[User talk:%s|Discusión]] || [[Special:Contributions/%s|Ver]] || %d \n" % (str(c),user,user,user,user,edits)
		else:
			s+=u"|-\n| %s || [[User:%s|%s]] || [[User talk:%s|Discusión]] || [[Special:Contributions/%s|Ver]] || %d \n" % (str(c),user,user,user,user,edits)

s+=u"{{/end}}"
page=wikipedia.Page(site, u'Wikipedia:Usuarios activos')
page.put(s, "BOT - Actualizando lista de usuarios activos [%d]" % c)





