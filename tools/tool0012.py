#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import Gnuplot
import MySQLdb
import sys
from tool0000 import *
import os

tool_id = "0012"
tool_title = "Edits maps"
tool_desc = "."
tool_path = generateToolPath(tool_id)
tool_archive_path = generateToolArchivePath(tool_id)

if not os.path.exists(tool_path):
	os.makedirs(tool_path)

if not os.path.exists(tool_archive_path):
	os.makedirs(tool_archive_path)

geoipdb = {}
catlimit = 10000000 #to make faster geolocation

def loadGeoIP():
	try:
		f = open("/home/emijrp/geoip/IpToCountry.csv", "r")
	except:
		os.system("wget software77.net/geo-ip/?DL=1 -O /home/emijrp/geoip/IpToCountry.csv.gz")
		os.system("gunzip /home/emijrp/geoip/IpToCountry.csv.gz")
		f = open("/home/emijrp/geoip/IpToCountry.csv", "r")
	
	c=0
	for l in f:
		l = l[:-1]
		l=re.sub("\"", "", l)
		if l[0] in ["#", " "]:
			continue
		t = l.split(",")
		start = int(t[0])
		end = int(t[1])
		iso2 = t[4]
		
		cat = (start / catlimit) * catlimit
		if geoipdb.has_key(cat):
			geoipdb[cat].append([start, end, iso2])
		else:
			geoipdb[cat] = [ [start, end, iso2] ]
		#print start, end, iso2
		c+=1
		if c % 10000 == 0:
			print "Loaded %d ip ranges for geolocation" % c
	f.close()
	#print geoipdb.keys()

def getIPCountry(ip):
	t=ip.split(".")
	ipnumber=int(t[3])+int(t[2])*256+int(t[1])*256*256+int(t[0])*256*256*256
	cat = ipnumber - (ipnumber % catlimit)
	#print ipnumber, cat
	if geoipdb.has_key(cat):
		for start, end, iso2 in geoipdb[cat]:
			if ipnumber>=start and ipnumber<=end:
				return iso2
	
	return False

loadGeoIP()

conn = MySQLdb.connect(host='sql-s1', db='enwiki_p', read_default_file='~/.my.cnf', use_unicode=True)
cursor = conn.cursor()
cursor.execute("""SELECT rc_user_text FROM recentchanges WHERE rc_timestamp>=date_add(now(), interval -1 day) and rc_user=0;""")
result = cursor.fetchall()
countries = {}
for row in result:
	ip = row[0]
	country = getIPCountry(ip)
	#print ip, country
	if countries.has_key(country):
		countries[country] += 1
	else:
		countries[country] = 1

countries_isos = ""
countries_values = ""
max = 0
for iso2, edits in countries.items():
	if iso2 != False:
		countries_isos += '"%s", ' % iso2
		countries_values += '%d, ' % edits
		if max < edits:
			max = edits
countries_isos = countries_isos[:-2]
countries_values = countries_values[:-2]

rscript = u"""library(maptools)
data(wrld_simpl)

#ISO2 http://www.unc.edu/~rowlett/units/codes/country.htm
country2    = c(%s)
country3 = c(%s)

country.all = wrld_simpl$ISO2
n.all       = length(country.all)
col.map     = numeric(n.all)
max         = %d

# grep country2 in country.all
for (i in 1:length(country2)){
  col.map[grep(country2[i],country.all)] = 0.1 + (country3[i]/max) * 0.9
}

c2      = col.map!=0
col.map2=col.map
col.map2[!c2]=rgb(1,.90,.90)
col.map2[c2]= rgb(1, 1, 1-col.map[c2])
png(filename="%s/a.png", width=1000, height=600)
plot(wrld_simpl,col=col.map2)
dev.off()""" % (countries_isos, countries_values, max, tool_path)

f = open("%s/r.script" % tool_path, "w")
f.write(rscript.encode("utf-8"))
f.close()

#os.system("cat %s/r.script | R --no-save" % (tool_path))

countries_list = []
for country, edits in countries.items():
	countries_list.append([edits, country])
countries_list.sort()
countries_list.reverse()

headers = ["Country", "Edits"]
row0=[]
row1=[]
row2=[]
c=0
for edits, country in countries_list:
	row0.append(str(c))
	row1.append(country)
	row2.append(edits)
	c+=1
	if c>=20:
		break

rows = [row1, row2]

title = u"Anonymous user edits by location"
file = "%s/graph.png" % (tool_path)
printBarsGraph(title=title, file=file, headers=headers, rows=rows)
