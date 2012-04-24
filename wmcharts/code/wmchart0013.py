# -*- coding: utf-8 -*-

# Copyright (C) 2012 emijrp <emijrp@gmail.com>
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

import re

from wmchart0000 import *

filename = 'wmchart0013.php'
title = 'Gender gap edits by project family'
description = "This chart shows which percent of edits were done by female editors in the last days grouped by project family. Not all users disclose her gender."

projectdbs = getProjectDatabases()

queries = [
    ["Total edits by editors with known gender", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges, user_properties WHERE rc_user=up_user AND rc_bot=0 AND up_property='gender' AND rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1  GROUP BY date ORDER BY date ASC" % (lastdays)],
    ["Edits by male editors", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges, user_properties WHERE rc_user=up_user AND rc_bot=0 AND up_property='gender' AND up_value='male' AND rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1  GROUP BY date ORDER BY date ASC" % (lastdays)],
    ["Edits by female editors", "SELECT CONCAT(YEAR(rc_timestamp),'-',LPAD(MONTH(rc_timestamp),2,'0'),'-',LPAD(DAY(rc_timestamp),2,'0'),'T00:00:00Z') AS date, COUNT(*) AS count FROM recentchanges, user_properties WHERE rc_user=up_user AND rc_bot=0 AND up_property='gender' AND up_value='female' AND rc_timestamp>=DATE_ADD(NOW(), INTERVAL -%d DAY) AND rc_type<=1  GROUP BY date ORDER BY date ASC" % (lastdays)],
    
]
projects = runQueries(projectdbs=projectdbs, queries=queries)
select = generateHTMLSelect(projects=[["all", '']])

accum = {}
for project, values in projects:
    for family, result in [["wikipedia", re.search(ur"wiki_p", project)], ["wikibooks", re.search(ur"wikibooks_p", project)], ["wikinews", re.search(ur"wikinews_p", project)], ["wikiquote", re.search(ur"wikiquote_p", project)], ["wikisource", re.search(ur"wikisource_p", project)], ["wikiversity", re.search(ur"wikiversity_p", project)], ["wiktionary", re.search(ur"wiktionary_p", project)], ]:
        if result:
            if accum.has_key(family):
                accum[family]["total"].append(values.has_key("Total edits by editors with known gender") and values["Total edits by editors with known gender"] or [])
                accum[family]["male"].append(values.has_key("Edits by male editors") and values["Edits by male editors"] or [])
                accum[family]["female"].append(values.has_key("Edits by female editors") and values["Edits by female editors"] or [])
            else:
                accum[family] = { "total": [values.has_key("Total edits by editors with known gender") and values["Total edits by editors with known gender"] or []], "male": [values.has_key("Edits by male editors") and values["Edits by male editors"] or []], "female": [values.has_key("Edits by female editors") and values["Edits by female editors"] or []] }
            if accum.has_key("all"):
                accum["all"]["total"].append(values.has_key("Total edits by editors with known gender") and values["Total edits by editors with known gender"] or [])
                accum["all"]["male"].append(values.has_key("Edits by male editors") and values["Edits by male editors"] or [])
                accum["all"]["female"].append(values.has_key("Edits by female editors") and values["Edits by female editors"] or [])
            else:
                accum["all"] = { "total": [values.has_key("Total edits by editors with known gender") and values["Total edits by editors with known gender"] or []], "male": [values.has_key("Edits by male editors") and values["Edits by male editors"] or []], "female": [values.has_key("Edits by female editors") and values["Edits by female editors"] or []] }
            break

var = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: []}
c = 1
for family in ["wikipedia", "wikibooks", "wikinews", "wikiquote", "wikisource", "wikiversity", "wiktionary", "all"]:
    dics = {"total": {}, "male": {}, "female": {}}
    for gender in ["total", "male", "female"]:
        for l in accum[family][gender]:
            for date, v in l:
                if dics[gender].has_key(date):
                    dics[gender][date] += int(v)
                else:
                    dics[gender][date] = int(v)
        dics["%s-l" % gender] = []
        for k, v in dics[gender].items():
            dics["%s-l" % gender].append([k, v])
        dics["%s-l" % gender].sort()
    
    dummy = []
    for date, v in dics["female-l"]:
        dummy.append([date, "%.1f" % (v/(dics["total"][date]/100.0))])
    var[c].append(dummy)
    
    c += 1

js = """function p() {
    var d1 = %s;
    var d2 = %s;
    var d3 = %s;
    var d4 = %s;
    var d5 = %s;
    var d6 = %s;
    var d7 = %s;
    var d8 = %s;
    var placeholder = $("#placeholder");
    var selected = document.getElementById('projects').selectedIndex;
    var data = [{ data: d1[selected], label: "wikipedia"}, { data: d2[selected], label: "wikibooks"}, { data: d3[selected], label: "wikinews"}, { data: d4[selected], label: "wikiquote"}, { data: d5[selected], label: "wikisource"}, { data: d6[selected], label: "wikiversity"}, { data: d7[selected], label: "wiktionary"}, { data: d8[selected], label: "all"} ];
    var options = { xaxis: { mode: "time" }, lines: {show: true}, points: {show: true}, legend: {noColumns: 2, noRows: 4}, grid: { hoverable: true }, };
    $.plot(placeholder, data, options);
}
p();""" % (str(var[1]), str(var[2]), str(var[3]), str(var[4]), str(var[5]), str(var[6]), str(var[7]), str(var[8]), )

output = generateHTML(title=title, description=description, select=select, js=js)
writeHTML(filename=filename, output=output)
