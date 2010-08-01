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
<style>
body {
    margin-left: 42px;
    margin-right: 42px;
    background: #ffffff;
    /*color: #002070;*/
    font-family: Verdana, Arial, Helvetica, sans-serif;
    font-size: 12px;
}
h1 {
    font-weight: bold;
    font-size: 16px;
}

h2 {
    font-size: 14px;
}

/* table style from http://es.wikipedia.org/wiki/MediaWiki:Common.css */
table.wikitable, table.prettytable {
    margin: 1em 1em 1em 1em;
    padding: 0.5em;
    font-size: 95%;
    background-color: #f9f9f9;
    border: 1px #aaa solid;
    border-collapse: collapse;
    text-align: center;
}
table.wikitable th, table.wikitable td,
table.prettytable th, table.prettytable td {
    border: 1px #aaa solid;
    padding: 0.2em;
}
table.wikitable th,
table.prettytable th {
    background-color: #f2f2f2;
    text-align: center;
}
table.wikitable caption,
table.prettytable caption {
    margin-left: inherit;
    margin-right: inherit;
}

img {
    border: 0px;
}
/*
estilo para los párrafos.-.
*/
</style>
</head>
<body>
<!-- start content -->
<?php
$langs_temp=array("en", "es", "de", "fr");
$langs=array();
foreach ($langs_temp as $lang_temp) { array_push($langs, '<a href="?lang='.$lang_temp.'">'.$lang_temp.'</a>'); }
//echo '<div style="clear: both; float: right;">Choose a language: ';
//echo join($langs, ' - ');
//echo '</div>';
?>
<h1><a href="http://toolserver.org/~emijrp">emijrp's tools</a></h1>
<hr/>"""
    if tool_title and tool_id:
        output+=u"<h2>%s (Tool #%s, <a href='http://toolserver.org/~emijrp/archive/tool%s'>archive</a>)</h2>" % (tool_title, tool_id, tool_id)
    return output

def getPHPFooter():
    return u"""<hr/>
<div style="float: right;"><a href="http://toolserver.org"><img src="wikimedia-toolserver-button.png" alt="Powered by Toolserver"></a></div>
<p><i>This page was last modified on <!-- timestamp -->%s<!-- timestamp -->.</i></p>
<!-- end content -->
</body>
</html>

<?php

ob_end_flush();

?>
""" % datetime.datetime.now()

def getPHPTools():
    return u"""<h2>My best tools (or I think so)</h2>
<ul>
<li><a href="imagesforbio/"><i>Images for biographies</i></a>: it shows a list of biographies missing images, with image proposals. It helps to include images in <a href="http://toolserver.org/~emijrp/imagesforbio/stats.php">+150 Wikipedia projects</a>, also in the smallest ones. Thousands of images have been included in articles ussing this method. Yay!</li>
<li><a href="wikimediacounter/">Wikimedia counter</a>: this counter shows the number of edits made in all the Wikimedia Foundation projects (Wikipedia, Wiktionary, Wikibooks, Wikiquote, Wikisource, Wikinews, Wikiversity, Meta, Wikispecies and Commons). The 1,000,000,000 (one billion) milestone was reached in <a href="wikimediacounter/onebillion.png">April 16, 2010</a>. Congratulations!</li>
<li><a href="wikimania/">Wikimania TV</a>: this is a mashup developed in a few minutes for Wikimania 2010 in Poland. It shows the video streaming for the rooms, the IRC channel and related tweets. Wikimania 2010 was finished, so, you can't see more streaming : (.</li>
<li><a href="best/"><i>Best free images</i></a>: a selection of the best Wikimedia Commons images that you can vote.</li>
<li><a href="tutoriales/">Tutorials</a>: some tutorials in Spanish for Wikipedia beginners.</li>
<li>(more soon...)</li>
</ul>

<h2>More tools</h2>
Here, you can see most of my <b>tools</b>. I hope they are useful:

<ol>

<li><a href="tool0001/">Replicated databases in Toolserver</a> [<a href="archive/tool0001/">archive</a>] [code]</li>
<li><a href="tool0002/">List of users by article count</a> [<a href="archive/tool0002/">archive</a>] [code]</li>
<li><a href="tool0003/"></a></li>
<li><a href="tool0004/"></a></li>
<li><a href="tool0005/">Active projects and languages in Wikimedia servers</a> [<a href="archive/tool0005/">archive</a>] [code]</li>
<li><a href="tool0006/"></a></li>
<li><a href="tool0007/"></a></li>
<li><a href="tool0008/"></a></li>
<li><a href="tool0009/"></a></li>
<li><a href="tool0010/"></a></li>
<li><a href="tool0011/"></a></li>
<li><a href="tool0012/"></a></li>
<li><a href="tool0013/"></a></li>
<li><a href="tool0014/"></a></li>
<li><a href="tool0015/"></a></li>
<li><a href="tool0016/"></a></li>
<li><a href="tool0017/"></a></li>
<li><a href="tool0018/"></a></li>
<li><a href="tool0019/"></a></li>
<li><a href="tool0020/"></a></li>
<li><a href="tool0021/"></a></li>
<li><a href="tool0022/"></a></li>
<li><a href="tool0023/"></a></li>
<li><a href="tool0024/"></a></li>
<li><a href="tool0025/">Most active users in all projects</a></li>
<li><a href="tool0026/"></a></li>
<li><a href="tool00027/">Last edit in all projects</a></li>
<li><a href="tool0028/"></a></li>

</ol>

<h2>Some old and very out-of-date tools</h2>

<ol>
<li><a href="wikiasearch/">Wikia Search design</a>: a proposed design for Wikia Search search engine that was closed some time ago.</li>
<li>(more soon... <i>tempus fugit</i>)</li>
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
<p><b>¡Welcome!</b> This is my userpage in <a href="http://toolserver.org">Toolserver</a> <a href="http://en.wikipedia.org/wiki/Webserver">webserver</a>. My username is <b>emijrp</b> (real name Emilio), I'm from Spain and I usually edit in <a href="http://es.wikipedia.org">Spanish Wikipedia</a> (you can see <a href="http://es.wikipedia.org/wiki/User:Emijrp">my userpage</a> there).</p>

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

