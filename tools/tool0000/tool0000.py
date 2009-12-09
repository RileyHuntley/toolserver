# -*- coding: utf-8 -*-

import re
import urllib

def generateToolPath(tool_id):
	return "/home/emijrp/public_html/tool%s/" % tool_id

def loadAllDatabasesFromNoc():
	dbs=[]
	f=urllib.urlopen("http://noc.wikimedia.org/conf/all.dblist")
	ll=f.read().splitlines()
	for l in ll:
		l=unicode(l, "utf-8")
		dbs.append(u"%s_p" % l)
		l=f.readline()
	return dbs

def getAllWikimediaFamilies():
	return ["commons", "labs", "mediawiki", "memoriam", "wikibooks", "wikimania", "wikimedia", "wikinews", "wikipedia", "wikiquote", "wikisource", "wikispecies", "wikiversity", "wiktionary"] #from toolserver.wiki table

def getPHPHeader():
	return u"<?php require_once('../header.php'); ?>"

def getPHPFooter():
	return u"<?php require_once('../footer.php'); ?>"
