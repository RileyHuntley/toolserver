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
<link href="style.css" rel="stylesheet" type="text/css"></link>
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
//echo '<div style="clear: both; float: right;">Choose a language: ';
//echo join($langs, ' - ');
//echo '</div>';
?>
<h1><a href="http://toolserver.org/~emijrp">emijrp's tools</a></h1>
<hr/>"""
    if tool_title and tool_id:
        output+=u"<h2>Tool #%s: %s [<a href='http://toolserver.org/~emijrp/archive/tool%s'>archive</a>] [code]</h2>" % (tool_id, tool_title, tool_id)
    return output

def getPHPFooter():
    return u"""<hr/>
<div style="float: right;"><a href="http://toolserver.org"><img src="wikimedia-toolserver-button.png" alt="Powered by Toolserver"></a></div>
<p><i>Total visits: <?php include ("counter.php"); ?>. This page was last modified on <!-- timestamp -->%s<!-- timestamp --> (UTC).</i></p>
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
<li><a href="imagesforbio/">Images for biographies</a>: it shows a list of biographies missing images, with image proposals. It helps to include images in <a href="http://toolserver.org/~emijrp/imagesforbio/stats.php">+150 Wikipedia projects</a>, also in the smallest ones. Thousands of images have been included in articles using this method. Yay!</li>
<li><a href="imagesforplaces/">Images for places</a>: a map with geolocated articles which have no pictures. Can you help taking a photo?</li>
<li><a href="wlm/">Wiki <i>Loves</i> Monuments</a>: a map for the Spanish edition of Wiki Loves Monuments.</li>
<li><a href="commonsexplorer/">Wikimedia Commons Explorer</a>: a map to explore geocoded Wikimedia Commons images by date.</li>
<li><a href="wikimediacounter/">Wikimedia counter</a>: this counter shows the number of edits made in all the Wikimedia Foundation projects (Wikipedia, Wiktionary, Wikibooks, Wikiquote, Wikisource, Wikinews, Wikiversity, Meta, Wikispecies and Commons). The 1,000,000,000 (one billion) milestone was reached in <a href="wikimediacounter/onebillion.png">April 16, 2010</a>. Congratulations!</li>
<li><a href="wmcharts/">Wmcharts</a>: a lot of charts about Wikimedia projects activity.</li>
<li><a href="wikimania/">Wikimania TV</a> (<a href="wikimania/2010/">2010</a>): this is a mashup developed in a few minutes for Wikimania 2010 in Poland. It shows the video streaming for the rooms, the IRC channel and related tweets. Wikimania 2010 was finished, so, you can't see more streaming : (.</li>
<li><a href="best/"><i>Best free images</i></a>: a selection of the best Wikimedia Commons images that you can vote.</li>
<li><a href="tutoriales/">Tutorials</a>: some tutorials in Spanish for Wikipedia beginners.</li>
<li>(more soon...)</li>
</ul>

<h2>Some old and very out-of-date tools</h2>

<ul>
<li><a href="wikiasearch/">Wikia Search design</a>: a proposed design for Wikia Search search engine that was closed some time ago.</li>
</ul>

<h2>Source code</h2>

You can find most of the source code for these tools in my <a href="http://code.google.com/p/toolserver/source/browse/#svn%2Ftrunk">SVN repository</a> at Google Code. If you want to send me any comment or report a bug, reach me at <a href="mailto:emijrp@gmail.com">emijrp@gmail.com</a>.
"""

    """<h2>More tools</h2>
    Here, you can see most of my <b>tools</b>. I hope they are useful:

    <ol>

    <li><a href="tool0001/">Replicated databases in Toolserver</a> [<a href="archive/tool0001/">archive</a>] [code]</li>
    <li><a href="tool0002/">List of users by article count</a> [<a href="archive/tool0002/">archive</a>] [code]</li>
    <li><a href="tool0003/">Revert rates</a> [todo]</li>
    <li><a href="tool0004/">Welcome newbies, they are the future!</a> [todo]</li>
    <li><a href="tool0005/">Active projects and languages in Wikimedia servers</a> [<a href="archive/tool0005/">archive</a>] [code]</li>
    <li><a href="tool0006/">General activity</a> [todo]</li>
    <li><a href="tool0007/">Most linked external links</a> [todo]</li>
    <li><a href="tool0008/">Pages distribution</a> [todo]</li><!-- porcentaje de redirecciones respecto de artículos (y resto de namespaces)-->
    <li><a href="tool0009/">Most linked Toolserver tools and users</a> [todo :)]</li>
    <li><a href="tool0010/">Most edited articles by different users in the last day</a> [todo]</li><!-- count(distinct rc_user_text) -->
    <li><a href="tool0011/">Edit activity levels</a> [todo]</li>
    <li><a href="tool0012/">Anonymous edits by location</a> [todo]</li>
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
    <li><a href="tool0025/">Most active users in all projects</a> [archive] [code]</li>
    <li><a href="tool0026/"></a></li>
    <li><a href="tool0027/"><i>Endangered</i> projects</a> [archive] [code]</li>
    <li><a href="tool0028/"></a></li>

    </ol>
    """

def writeToFile(filename, output):
    f=open(filename, "w")
    f.write(output.encode("utf-8"))
    f.close()

def createIndex():
    output=u"""%s
<p><b>Welcome!</b> This is my userpage in the <a href="http://toolserver.org">Toolserver</a> <a href="http://en.wikipedia.org/wiki/Webserver">webserver</a>. My username is <b>emijrp</b>, I'm from Spain and I use to edit <a href="http://en.wikipedia.org">English Wikipedia</a> (you can see <a href="http://en.wikipedia.org/wiki/User:Emijrp">my userpage</a> there).</p>

<p><img src="Wikihands.jpg" alt="me" style="clear:right;float:right"/></p>
%s
<!--
<h2>Useful links</h2>
Some useful links for developing tools and <i>just for fun</i>:
<ul>
<li>MediaWiki Database schema: <a href="http://svn.wikimedia.org/svnroot/mediawiki/trunk/phase3/maintenance/tables.sql">SVN</a> and <a href="http://www.mediawiki.org/wiki/Manual:Database_layout">Manual:Database layout</a> (possibly out of date)</li>
</ul>

<h2>External links</h2>
<u><b>NOT</b></u> my tools. But cool ones:
<ul>
<li>Counters: <a href="http://www.7is7.com/software/firefox/partycounter.html">Firefox downloads</a>, <a href="http://gigatweeter.com/counter">Twitter</a></li>
</ul>
-->

<?php
/*

OLD DESIGN

<h2>Lists</h2>
<ul>
<li><a href="http://en.wikipedia.org/wiki/User:Emijrp/Most_redirected_pages_(Small_version)">Most redirected pages</a> (English Wikipedia)</li>
<li><a href="http://en.wikipedia.org/wiki/User:Emijrp/Most_interwiked_articles">Most interwiked articles</a> (English Wikipedia)</li>
</ul>

<h2>Miscellany</h2>
<ul>
<li><a href="http://www.toolserver.org/~emijrp/red/">Wikipedia Redlinks</a>: <i>perpetual work-in-progress</i>.</li>
</ul>

*/
?>
%s
""" % (getPHPHeader(), getPHPTools(), getPHPFooter())
    writeToFile("/home/emijrp/public_html/index.php", output)

createIndex()

