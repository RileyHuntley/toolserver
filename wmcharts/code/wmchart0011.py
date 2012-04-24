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

filename = 'wmchart0011.php'
title = 'Gender gap editors'
description = "This chart shows how many male and female editors edited in the last days. Not all users disclose her gender."

projectdbs = getProjectDatabases()

queries = [
    ["Total editors with known gender", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(DISTINCT rc_user) AS count FROM recentchanges, user_properties WHERE rc_user=up_user AND rc_bot=0 AND up_property='gender' AND rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1  GROUP BY date ORDER BY date ASC" % (lastdays)],
    ["Male editors", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(DISTINCT rc_user) AS count FROM recentchanges, user_properties WHERE rc_user=up_user AND rc_bot=0 AND up_property='gender' AND up_value='male' AND rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1  GROUP BY date ORDER BY date ASC" % (lastdays)],
    ["Female editors", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(DISTINCT rc_user) AS count FROM recentchanges, user_properties WHERE rc_user=up_user AND rc_bot=0 AND up_property='gender' AND up_value='female' AND rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1  GROUP BY date ORDER BY date ASC" % (lastdays)],
    
]
projects = runQueries(projectdbs=projectdbs, queries=queries)
select = generateHTMLSelect(projects)

var1 = []
var2 = []
var3 = []
for project, values in projects:
    var1.append(values.has_key("Total editors with known gender") and values["Total editors with known gender"] or 0)
    var2.append(values.has_key("Male editors") and values["Male editors"] or 0)
    var3.append(values.has_key("Female editors") and values["Female editors"] or 0)

js = """function p() {
    var d1 = %s;
    var d2 = %s;
    var d3 = %s;
    var placeholder = $("#placeholder");
    var selected = document.getElementById('projects').selectedIndex;
    var data = [{ data: d1[selected], label: "Total editors with known gender"}, { data: d2[selected], label: "Male editors"}, { data: d3[selected], label: "Female editors"}];
    var options = { xaxis: { mode: "time" }, lines: {show: true}, points: {show: true}, legend: {noColumns: 3}, grid: { hoverable: true }, };
    $.plot(placeholder, data, options);
}
p();""" % (str(var1), str(var2), str(var3))

output = generateHTML(title=title, description=description, select=select, js=js)
writeHTML(filename=filename, output=output)
