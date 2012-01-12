# -*- coding: utf-8 -*-

# Copyright (C) 2011 emijrp <emijrp@gmail.com>
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

from wmchart0000 import *

filename = 'wmchart0012.html'
title = 'Images for bio progress'
description = "This chart shows how many images have been added to articles using the <i><a href='http://toolserver.org/~emijrp/imagesforbio/'>Images for biographies</a> tool."

projectdbs = getProjectDatabases()

lastdays = 100

queries = [
    ["Total added images", "SELECT CONCAT(YEAR(rev_timestamp),'-',LPAD(MONTH(rev_timestamp),2,'0'),'-',LPAD(DAY(rev_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(DISTINCT rev_user) AS count FROM revision WHERE /*rev_namespace=0 AND */ rev_comment rlike 'imagesforbio' AND rev_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) GROUP BY date ORDER BY date ASC" % (lastdays)],
    
]
projects = runQueries(projectdbs=projectdbs, queries=queries)
select = "" # no select generateHTMLSelect()

var1 = []
dic1 = {}
for project, values in projects:
    if values["Total added images"]:
        if dic1.has_key(values["Total added images"][0][0]):
            dic1[values["Total added images"][0][0]] += values["Total added images"][0][1]
        else:
            dic1[values["Total added images"][0][0]] = values["Total added images"][0][1]

for k, v in dic1.items():
    var1.append([k, v])

var1.sort() #la query nos lo daba ordenado, pero al hacer el paso intermedio con el dictionary, se desordena

js = """function p() {
    var d1 = %s;
    var placeholder = $("#placeholder");
    var selected = document.getElementById('projects').selectedIndex;
    var data = [{ data: d1[selected], label: "Total added images"}];
    var options = { xaxis: { mode: "time" }, lines: {show: true}, points: {show: true}, legend: {noColumns: 1}, grid: { hoverable: true }, };
    $.plot(placeholder, data, options);
}
p();""" % (str(var1))

output = generateHTML(title=title, description=description, select=select, js=js)
writeHTML(filename=filename, output=output)
