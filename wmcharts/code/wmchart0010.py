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

filename = 'wmchart0010.html'
title = 'Gender gap edits'
description = "This chart shows how many edits were done by male and female editors in the last days. Not all users disclose her gender."

projectdbs = getProjectDatabases(lang='en', family='wikipedia')

queries = [
    ["Total edits by known gender", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges, user_properties WHERE rc_user=up_user AND rc_bot=0 AND up_property='gender' AND rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1  GROUP BY date ORDER BY date ASC" % (lastdays)],
    ["Edits by males", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges, user_properties WHERE rc_user=up_user AND rc_bot=0 AND up_property='gender' AND up_value='male' AND rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1  GROUP BY date ORDER BY date ASC" % (lastdays)],
    ["Edits by females", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges, user_properties WHERE rc_user=up_user AND rc_bot=0 AND up_property='gender' AND up_value='female' AND rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1  GROUP BY date ORDER BY date ASC" % (lastdays)],
    
]
projects = runQueries(projectdbs=projectdbs, queries=queries)
select = generateHTMLSelect(projects)

var1 = []
var2 = []
var3 = []
for project, values in projects:
    var1.append(values["Total edits by known gender"])
    var2.append(values["Edits by males"])
    var3.append(values["Edits by females"])

js = """function p() {
    var d1 = %s;
    var d2 = %s;
    var d3 = %s;
    var placeholder = $("#placeholder");
    var selected = document.getElementById('projects').selectedIndex;
    var data = [{ data: d1[selected], label: "Total edits by known gender"}, { data: d2[selected], label: "Edits by males"}, { data: d3[selected], label: "Edits by females"}];
    var options = { xaxis: { mode: "time" }, lines: {show: true}, points: {show: true}, legend: {noColumns: 3}, grid: { hoverable: true }, };
    $.plot(placeholder, data, options);
}
p();""" % (str(var1), str(var2), str(var3))

output = generateHTML(title=title, description=description, select=select, js=js)
writeHTML(filename=filename, output=output)
