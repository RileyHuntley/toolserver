#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import re
import urllib

def generateToolPath(tool_id, tool_subdir=""):
	if tool_subdir:
		tool_subdir="/%s" % tool_subdir
	return "/home/emijrp/public_html/tool%s%s" % (tool_id, tool_subdir)

def generateToolArchivePath(tool_id, tool_subdir="", tool_date=""):
	#tool_date debe ser un datetime.date() con año, mes y día
	#tool_subdir sirve para ordenar por wikis por ejemplo, en la tool0002
	if tool_subdir:
		if tool_subdir[0]!='/':
			tool_subdir="/%s" % tool_subdir
		if tool_subdir[-1]=='/':
			tool_subdir=tool_subdir[:len(tool_subdir)-1] #tool_subdir[:-1] no funciona bien
	if not tool_date:
		tool_date=datetime.date.today()
	return "/home/emijrp/public_html/archive/tool%s%s/%s/%s/%s" % (tool_id, tool_subdir, tool_date.year, tool_date.strftime("%m"), tool_date.strftime("%d"))

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

def getPHPHeader(tool_id=0, tool_title=""):
	output=u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr">
<head>
<title>emijrp's tools</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<meta name="generator" content="Sitio web hecho a manopla" />
<meta name="description" content="emijrp tools"/>
<meta name="keywords" content="emijrp,toolserver,tools,wikipedia,wiki"/> 
<meta name="author" content="emijrp"/> 
</head>
<body>
<!-- start content -->
<?php
$langs_temp=array("en", "es", "de", "fr");
$langs=array();
foreach ($langs_temp as $lang_temp) { array_push($langs, '<a href="?lang='.$lang_temp.'">'.$lang_temp.'</a>'); }
echo '<div style="clear: both; float: right;">Choose a language: ';
echo join($langs, ' - ');
echo '</div>';
?>
<h1><a href="http://toolserver.org/~emijrp/">emijrp's tools</a></h1>
<hr/>"""
	if tool_title and tool_id:
		output+=u"<h2>%s (Tool #%s, <a href='http://toolserver.org/~emijrp/archive/tool%s'>archive</a>)</h2>" % (tool_title, tool_id, tool_id)
	return output

def getPHPFooter():
	return u"""<hr/>
<div style="text-align: center;"><img src="wikimedia-toolserver-button.png" alt="Powered by Toolserver"></div>
<p><i>This page was last modified on <!-- timestamp -->%s<!-- timestamp -->.</i></p>
<!-- end content -->
</body>
</html>

<?php

ob_end_flush();

?>
""" % datetime.datetime.now()

def getPHPTools():
	return u"""<ol>

<li><a href="tool0001/">Replicated databases in Toolserver</a> (<a href="archive/tool0001/">archive</a>)</li>
<li><a href="tool0002/">List of users by article count</a> (<a href="archive/tool0002/">archive</a>)</li>
<li>aa<a href="tool0003/"></a></li>
<li>aa<a href="tool0004/"></a></li>
<li><a href="tool0005/">Active projects and languages in Wikimedia servers</a> (<a href="archive/tool0005/">archive</a>)</li>
<li>aa<a href="tool0006/"></a></li>
<li>aa<a href="tool0007/"></a></li>
<li>aa<a href="tool0008/"></a></li>

</ol>
"""

def writeToFile(filename, output):
	f=open(filename, "w")
	f.write(output.encode("utf-8"))
	f.close()

def createIndex():
	output=u"""%s
<h2>Introduction</h2>
<p><img src="Wikihands.jpg" alt="me" style="clear:right;float:right"/></p>
<p><b>¡Welcome!</b> This is my userpage in <a href="http://toolserver.org">Toolserver</a> <a href="http://en.wikipedia.org/wiki/Webserver">webserver</a>. My name is Emilio, I'm from Spain and I usually edit in <a href="http://es.wikipedia.org">Spanish Wikipedia</a>.</p>

<h2>Tools</h2>
Here, you can see most of my <b>tools</b>. I hope they are useful:

%s

<h2>Useful links</h2>
Some useful links for developing tools and <i>just for fun</i>:
<ul>
<li>MediaWiki Database schema: <a href="http://svn.wikimedia.org/svnroot/mediawiki/trunk/phase3/maintenance/tables.sql">SVN</a> and <a href="http://www.mediawiki.org/wiki/Manual:Database_layout">Manual:Database layout</a> (possibly out of date)</li>
</ul>

<?php
/*

OLD DESIGN

<h2>Image related</h2>
<ul>
<li><a href="http://toolserver.org/~emijrp/best/"><i>Best Free Images</i></a>: Vote your favorite images!</li>
<li><a href="http://commons.wikimedia.org/wiki/User:Emijrp/Commons">Proposed images for blind articles</a> (<tt>Updated!</tt>)</li>
<li>Duplicated images: <a href="http://commons.wikimedia.org/wiki/User:Emijrp/Duplicated_images">Commons</a> (<tt>Old</tt>), <a href="http://en.wikipedia.org/wiki/User:Emijrp/Duplicated_images">English Wikipedia</a> (<tt>Updated!</tt>), <a href="">Deutch Wikipedia</a>.</li>
<li><a href="http://toolserver.org/~emijrp/imagesforbio/">Images for biographies</a> (<tt>Updated!</tt>)</li>
</ul>

<h2>Lists</h2>
<ul>
<li><a href="http://en.wikipedia.org/wiki/User:Emijrp/Most_redirected_pages_(Small_version)">Most redirected pages</a> (English Wikipedia)</li>
<li><a href="http://en.wikipedia.org/wiki/User:Emijrp/Most_interwiked_articles">Most interwiked articles</a> (English Wikipedia)</li>
</ul>

<h2>Miscellany</h2>
<ul>
<li><a href="http://www.toolserver.org/~emijrp/avbot/">AVBOT logs</a>: Real time logs for an antivandalbot in Spanish Wikipedia.</li>
<li><a href="http://www.toolserver.org/~emijrp/wikiforja.php">WikiFORJA</a>: More tools.</li>
<li><a href="http://www.toolserver.org/~emijrp/red/">Wikipedia Redlinks</a>: <i>perpetual work-in-progress</i>.</li>
<li><a href="http://www.toolserver.org/~emijrp/tutoriales/">Tutoriales en Flash</a>: Para aprender las cosas bÃ¡sicas de Wikipedia.</li>
</ul>

<hr/>

<p>See my userpage in <a href="http://es.wikipedia.org/wiki/Usuario:Emijrp">Spanish</a> and <a href="http://en.wikipedia.org/wiki/User:Emijrp">English Wikipedia</a>. Bugs reports and suggestions to <tt>emijrp</tt> AATTTT <tt>gmail</tt> DDDOOOOOTTT <tt>com</tt></p>
*/
?>
%s
""" % (getPHPHeader(), getPHPTools(), getPHPFooter())
	writeToFile("/home/emijrp/public_html/index.php", output)

createIndex()

