# -*- coding: utf-8 -*-

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

path = '..'
filename = 'wmchart0005.html'
title = 'Blocked users'
description = "This chart shows how many users have been blocked in the last days."

projectdbs = getProjectDatabases()

queries = [
    ["Blocks", "SELECT CONCAT(YEAR(log_timestamp),'-',LPAD(MONTH(log_timestamp),2,'0'),'-',LPAD(DAY(log_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM logging WHERE log_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND log_action='block' GROUP BY date ORDER BY date ASC" % (lastdays)],
]
projects = runQueries(projectdbs=projectdbs, queries=queries)
select = generateHTMLSelect(projects)

var1 = []
for project, values in projects:
    var1.append(values["Blocks"])

js = """function p() {
    var d1 = %s;
    var placeholder = $("#placeholder");
    var selected = document.getElementById('projects').selectedIndex;
    var data = [{ data: d1[selected], label: "Blocks"}];
    var options = { xaxis: { mode: "time" }, lines: {show: true}, points: {show: true}, legend: {noColumns: 1}, };
    $.plot(placeholder, data, options);
}
p();""" % (str(var1))

output = generateHTML(title=title, description=description, select=select, js=js)
writeHTML(path=path, filename=filename, output=output)
