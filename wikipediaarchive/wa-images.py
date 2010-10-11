import re, hashlib, urllib
from urllib import FancyURLopener
from random import choice
import tarfile
import os
import gzip

lang = 'en'
family = 'wikinews'
sel = ''

user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
]

class MyOpener(FancyURLopener, object):
    version = choice(user_agents)

urlretrieve = MyOpener().retrieve
myopener = MyOpener()

#('World_C_29May2007at2130UTC.jpg',146375,1074,512,'a:8:{s:11:\"Orientation\";i:1;s:11:\"XResolution\";s:4:\"72/1\";s:11:\"YResolution\";s:4:\"72/1\";s:14:\"ResolutionUnit\";i:2;s:8:\"Software\";s:26:\"Adobe Photoshop CS Windows\";s:8:\"DateTime\";s:19:\"2005:02:04 01:24:59\";s:10:\"ColorSpace\";i:65535;s:22:\"MEDIAWIKI_EXIF_VERSION\";i:1;}',8,'BITMAP','image','jpeg','\'\'\'Image:\'\'\' Temperatures for various cities across the globe on May 29, 2007 at 21:30 UTC.\n\n\'\'\'Source:\'\'\' I am the author of this, using Wikinews WeatherChecker.\n',6038,'DragonFire1024','20070529213348','doum6ct5z1g94pgadnkhfore468g8es'),
#('Wiki.png','20050212224111!Wiki.png',13175,135,86,8,'Draft logo for wikinews. From [[m:Image:Wikinews-draftlogo.png]]. {{PD}}',1,'Tim','20041108081142','dydrrza14rd8i0tlrg99hnhwnovl778','0','BITMAP','image','png',0)
#,('2August2005.pdf','',667947,0,0,0,'{{printedition|August 2, 2005}}',1808,'Cspurrier','20050802030623','','',NULL,'unknown','unknown',0),
list = [
['%s%s-latest-oldimage.sql.gz' % (lang, family), ur'\(\'.*?\',\'(.*?)\',\d+,\d+,\d+,\d+,\'.*?\',\d+,\'.*?\',\'(\d{14})\',\'.*?\',\'.*?\',(?:NULL|\'.*?\'),\'.*?\',\'.*?\',\d+\)', 'archive/'],
 
['%s%s-latest-image.sql.gz' % (lang, family), ur'\(\'(.*?)\',\d+,\d+,\d+,.*?,\'(\d{14})\',\'.*?\'\)', ''],
]

tar=tarfile.open('%s%s-%s.tar' % (lang, family, sel), 'a')
tarcontain = tar.getnames()
tar.close()

for filename, regexp, subdir in list:
	myopener.retrieve('http://download.wikimedia.org/%s%s/latest/%s' % (lang, family, filename), filename)
	f = gzip.GzipFile(filename, 'r')
	c=0
	
	for l in f:
		m = re.findall(regexp, l)
		if m:
			for image, timestamp in m:
				try:
					image = unicode(image, 'utf-8')
				except:
					print "ERROR", image
					continue
				if not image:
					continue #no existe o fue borrada http://en.wikinews.org/wiki/File:2August2005.pdf
				image=image.encode('utf-8')
				if timestamp.startswith(sel):
					md5=''
					if subdir:
						md5=hashlib.md5('!'.join(image.split('!')[1:])).hexdigest() 
					else:
						md5=hashlib.md5(image).hexdigest() 
					print image, timestamp, md5
					c+=1
					
					if image not in tarcontain:
						tar=tarfile.open('%s%s-%s.tar' % (lang, family, sel), 'a')
						url='http://upload.wikimedia.org/%s/%s/%s%s/%s/%s' % (family, lang, subdir, md5[0], md5[:2], image)
						myopener.retrieve(url, image)
						tar.add(image)
						os.remove(image)
						tar.close()
	print c
	f.close()

