#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import sys
from tool0000 import *
import os

tool_id="0005"
tool_title="All active projects and languages in Wikimedia servers"
tool_desc=""
tool_path=generateToolPath(tool_id)
tool_archive_path=generateToolArchivePath(tool_id)
date=datetime.date.today()

if not os.path.exists(tool_path):
	os.makedirs(tool_path)

if not os.path.exists(tool_archive_path):
	os.makedirs(tool_archive_path)


f=urllib.urlopen("http://noc.wikimedia.org/conf/all.dblist")
raw=f.read()
filename="all-active-projects-and-languages.txt"
filedesc=u"Backup from <a href='http://noc.wikimedia.org/conf/all.dblist'>http://noc.wikimedia.org/conf/all.dblist</a>"
writeToFile("%s/%s" % (tool_path, filename), raw)
writeToFile("%s/%s-%s" % (tool_archive_path, date.isoformat(), filename), raw)
f.close()

output=getPHPHeader(tool_id, tool_title)
output+=u"<ul>\n<li><tt><a href=\"%s\">%s</a></tt> - %s</li>\n</ul>" % (filename, filename, filedesc)
output+=getPHPFooter()
filename="%s/index.php" % tool_path
writeToFile(filename, output)


