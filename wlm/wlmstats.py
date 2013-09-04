#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2013 emijrp <emijrp@gmail.com>
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

import catlib
import datetime
import json
import os
import oursql
import pagegenerators
import re
import time
import wikipedia

#wlm counter con contador de subidas y megabytes
#http://commons.wikimedia.org/wiki/Commons:Wiki_Loves_Monuments_2012/CentralNotice

"""
yuvipanda request ranking of mobile users
select page_title,  
(select  rev_user_text from revision where rev_page = page_id order by rev_timestamp  limit 1 ) as original 
from iwlinks join page on iwl_from=page_id join revision on page_latest = rev_id where iwl_prefix='mw' and iwl_title='Wiki_Loves_Monuments_mobile_application' and page_namespace=6
"""

year = u'2013'
path = "/home/emijrp/public_html/wlm"
uploadcats = { 
    u'algeria': u'Images from Wiki Loves Monuments %s in Algeria' % (year), 
    u'andorra': u'Images from Wiki Loves Monuments %s in Andorra' % (year), 
    u'antarctica': u'Images from Wiki Loves Monuments %s in Antarctica' % (year), 
    u'argentina': u'Images from Wiki Loves Monuments %s in Argentina' % (year), 
    u'armenia': u'Images from Wiki Loves Monuments %s in Armenia' % (year), 
    u'aruba': u'Images from Wiki Loves Monuments %s in Aruba' % (year), 
    u'austria': u'Images from Wiki Loves Monuments %s in Austria' % (year), 
    u'azerbaijan': u'Images from Wiki Loves Monuments %s in Azerbaijan' % (year), 
    u'belarus': u'Images from Wiki Loves Monuments %s in Belarus' % (year), 
    u'belgium': u'Images from Wiki Loves Monuments %s in Belgium' % (year), 
    u'bolivia': u'Images from Wiki Loves Monuments %s in Bolivia' % (year), 
    u'cameroon': u'Images from Wiki Loves Monuments %s in Cameroon' % (year), 
    u'canada': u'Images from Wiki Loves Monuments %s in Canada' % (year), 
    u'chile': u'Images from Wiki Loves Monuments %s in Chile' % (year), 
    u'china': u'Images from Wiki Loves Monuments %s in China' % (year), 
    u'colombia': u'Images from Wiki Loves Monuments %s in Colombia' % (year), 
    u'czechrepublic': u'Images from Wiki Loves Monuments %s in the Czech Republic' % (year), 
    #u'denmark': u'Images from Wiki Loves Monuments %s in Denmark' % (year), 
    u'egypt': u'Images from Wiki Loves Monuments %s in Egypt' % (year), 
    u'elsalvador': u'Images from Wiki Loves Monuments %s in El Salvador' % (year), 
    u'estonia': u'Images from Wiki Loves Monuments %s in Estonia' % (year), 
    u'france': u'Images from Wiki Loves Monuments %s in France' % (year), 
    u'germany': u'Images from Wiki Loves Monuments %s in Germany' % (year), 
    #u'ghana': u'Images from Wiki Loves Monuments %s in Ghana' % (year), 
    u'hongkong': u'Images from Wiki Loves Monuments %s in Hong Kong' % (year), 
    u'hungary': u'Images from Wiki Loves Monuments %s in Hungary' % (year), 
    u'india': u'Images from Wiki Loves Monuments %s in India' % (year), 
    u'israel': u'Images from Wiki Loves Monuments %s in Israel' % (year), 
    u'italy': u'Images from Wiki Loves Monuments %s in Italy' % (year), 
    u'jordan': u'Images from Wiki Loves Monuments %s in Jordan' % (year), 
    #u'kenya': u'Images from Wiki Loves Monuments %s in Kenya' % (year), 
    #u'liechtenstein': u'Images from Wiki Loves Monuments %s in Liechtenstein' % (year), 
    u'luxembourg': u'Images from Wiki Loves Monuments %s in Luxembourg' % (year), 
    u'mexico': u'Images from Wiki Loves Monuments %s in Mexico' % (year), 
    u'nepal': u'Images from Wiki Loves Monuments %s in Nepal' % (year), 
    u'netherlands': u'Images from Wiki Loves Monuments %s in the Netherlands' % (year), 
    u'norway': u'Images from Wiki Loves Monuments %s in Norway' % (year), 
    u'panama': u'Images from Wiki Loves Monuments %s in Panama' % (year), 
    u'philippines': u'Images from Wiki Loves Monuments %s in the Philippines' % (year), 
    u'poland': u'Images from Wiki Loves Monuments %s in Poland' % (year), 
    u'romania': u'Images from Wiki Loves Monuments %s in Portugal' % (year), 
    u'romania': u'Images from Wiki Loves Monuments %s in Romania' % (year), 
    u'russia': u'Images from Wiki Loves Monuments %s in Russia' % (year), 
    u'serbia': u'Images from Wiki Loves Monuments %s in Serbia' % (year), 
    u'slovakia': u'Images from Wiki Loves Monuments %s in Slovakia' % (year), 
    u'southafrica': u'Images from Wiki Loves Monuments %s in South Africa' % (year), 
    #u'southtyrol': u'Images from Wiki Loves Monuments %s in South Tyrol' % (year), 
    u'spain': u'Images from Wiki Loves Monuments %s in Spain' % (year), 
    u'sweden': u'Images from Wiki Loves Monuments %s in Sweden' % (year), 
    u'switzerland': u'Images from Wiki Loves Monuments %s in Switzerland' % (year), 
    u'syria': u'Images from Wiki Loves Monuments %s in Syria' % (year), 
    u'taiwan': u'Images from Wiki Loves Monuments %s in Taiwan' % (year), 
    u'thailand': u'Images from Wiki Loves Monuments %s in Thailand' % (year), 
    u'tunisia': u'Images from Wiki Loves Monuments %s in Tunisia' % (year), 
    u'ukraine': u'Images from Wiki Loves Monuments %s in Ukraine' % (year), 
    u'unitedkingdom': u'Images from Wiki Loves Monuments %s in the United Kingdom' % (year), 
    u'unitedstates': u'Images from Wiki Loves Monuments %s in the United States' % (year), 
    u'uruguay': u'Images from Wiki Loves Monuments %s in Uruguay' % (year), 
    u'venezuela': u'Images from Wiki Loves Monuments %s in Venezuela' % (year), 
}

countrynames = { 
    u'algeria': u'Algeria', 
    u'andorra': u'Andorra', 
    u'antarctica': u'Antarctica', 
    u'argentina': u'Argentina', 
    u'armenia': u'Armenia', 
    u'aruba': u'Aruba', 
    u'austria': u'Austria', 
    u'azerbaijan': u'Azerbaijan', 
    u'belarus': u'Belarus', 
    u'belgium': u'Belgium', 
    u'bolivia': u'Bolivia', 
    u'cameroon': u'Cameroon', 
    u'canada': u'Canada', 
    u'chile': u'Chile', 
    u'china': u'China', 
    u'colombia': u'Colombia', 
    u'czechrepublic': u'Czech Republic‎', 
    u'denmark': u'Denmark', 
    u'egypt': u'Egypt', 
    u'elsalvador': u'El Salvador', 
    u'estonia': u'Estonia', 
    u'france': u'France', 
    u'germany': u'Germany', 
    u'ghana': u'Ghana', 
    u'hongkong': u'Hong Kong', 
    u'hungary': u'Hungary', 
    u'india': u'India', 
    u'israel': u'Israel', 
    u'italy': u'Italy', 
    u'jordan': u'Jordan', 
    u'kenya': u'Kenya', 
    u'liechtenstein': u'Liechtenstein', 
    u'luxembourg': u'Luxembourg', 
    u'mexico': u'Mexico', 
    u'nepal': u'Nepal', 
    u'netherlands': u'Netherlands', 
    u'norway': u'Norway', 
    u'panama': u'Panama', 
    u'philippines': u'Philippines', 
    u'poland': u'Poland', 
    u'portugal': u'Portugal', 
    u'romania': u'Romania', 
    u'russia': u'Russia', 
    u'serbia': u'Serbia', 
    u'slovakia': u'Slovakia', 
    u'southafrica': u'South Africa', 
    u'southtyrol': u'South Tyrol', 
    u'spain': u'Spain', 
    u'sweden': u'Sweden', 
    u'switzerland': u'Switzerland', 
    u'syria': u'Syria', 
    u'taiwan': u'Taiwan', 
    u'thailand': u'Thailand', 
    u'tunisia': u'Tunisia', 
    u'ukraine': u'Ukraine', 
    u'unitedkingdom': u'United Kingdom', 
    u'unitedstates': u'United States', 
    u'uruguay': u'Uruguay', 
    u'venezuela': u'Venezuela', 
}

def convert2unix(mwtimestamp):
    #from wmchart0000.py
    #2010-12-25T12:12:12Z
    [year, month, day] = [int(mwtimestamp[0:4]), int(mwtimestamp[5:7]), int(mwtimestamp[8:10])]
    [hour, minute, second] = [int(mwtimestamp[11:13]), int(mwtimestamp[14:16]), int(mwtimestamp[17:19])]
    d = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    return int((time.mktime(d.timetuple())+1e-6*d.microsecond)*1000)

def main():
    #loading files metadata
    conn = oursql.connect(db='commonswiki_p', host='sql-s1.toolserver.org', read_default_file=os.path.expanduser("~/.my.cnf"), charset="utf8", use_unicode=True)
    curs = conn.cursor(oursql.DictCursor)
    filename = 'files.txt'
    files = []
    filesdict = {}
    for country in uploadcats.keys():
        #continue
        print country
        curs.execute(u"""SELECT page_title, 
        (SELECT rev_user_text FROM revision WHERE rev_page=page_id ORDER BY rev_timestamp LIMIT 1) AS username,
        (SELECT rev_timestamp FROM revision WHERE rev_page=page_id ORDER BY rev_timestamp LIMIT 1) AS timestamp,
        (SELECT img_size FROM image WHERE img_name=page_title) AS size,
        (SELECT img_width FROM image WHERE img_name=page_title) AS width,
        (SELECT img_height FROM image WHERE img_name=page_title) AS height
        FROM categorylinks JOIN page ON cl_from=page_id JOIN revision ON page_latest=rev_id JOIN image ON img_name=page_title WHERE cl_to=? AND page_namespace=6;""", (re.sub(u' ', u'_', uploadcats[country]), ))
        row = curs.fetchone()
        while row:
            try:
                page_title = unicode(row['page_title'], 'utf-8')
                username = unicode(row['username'], 'utf-8')
                date = row['timestamp']
                date = u'%s-%s-%sT%s:%s:%sZ' % (date[0:4], date[4:6], date[6:8], date[8:10], date[10:12], date[12:14])
                resolution = u'%s×%s' % (str(row['width']), str(row['height']))
                size = str(row['size'])
                files.append([page_title, country, date, username, resolution, size])
                filesdict[page_title] = {'page_title': page_title, 'country': country, 'date': date, 'username': username, 'resolution': resolution, 'size': size}
            except:
                try:
                    print row
                except:
                    print 'Error'
            row = curs.fetchone()
    
    conn.close()
    print len(files), 'files'
    f = open("%s/%s" % (path, filename), 'w')
    output = u'%s\n%s' % (u';;;'.join(['filename', 'country', 'date', 'username', 'resolution', 'size']), u'\n'.join([u';;;'.join(i) for i in files]))
    f.write(output.encode('utf-8'))
    f.close()
    with open('%s/files.json' % (path), 'w') as jsonfile:
        json.dump(filesdict, jsonfile)

    #stats
    dates = {}
    hours = {}
    users = {}
    countries = {}
    resolutions = {}
    sizes_list = []
    c = 0
    for title, country, date, username, resolution, size in files:
        c += 1
        #print c, title
        if countries.has_key(country):
            countries[country]['files'] += 1
            countries[country]['size'] += int(size)
            if not username in countries[country]['uploaders']:
                countries[country]['uploaders'].append(username)
        else:
            countries[country] = { 'files': 1, 'size': int(size), 'uploaders': [username]}
        d = u'%sT00:00:00Z' % (date.split('T')[0])
        h = date.split('T')[1].split(':')[0]
        if dates.has_key(d):
            dates[d] += 1
        else:
            dates[d] = 1
        if hours.has_key(h):
            hours[h] += 1
        else:
            hours[h] = 1
        if users.has_key(username):
            users[username]['files'] += 1
            users[username]['size'] += int(size)
        else:
            users[username] = {'files': 1, 'size': int(size)}
        if resolutions.has_key(resolution):
            resolutions[resolution]['files'] += 1
            resolutions[resolution]['size'] += int(size)
        else:
            resolutions[resolution] = {'files': 1, 'size': int(size)}
        sizes_list.append([int(size), title, username, country])

    sizes_list.sort(reverse=1)
    countries_list = [[v['files'], k] for k, v in countries.items()]
    countries_list.sort(reverse=1)
    countries_list = [[k, v] for v, k in countries_list]
    dates_list = [[k, v] for k, v in dates.items()]
    dates_list.sort()
    hours_list = [[k, v] for k, v in hours.items()]
    hours_list.sort()
    users_list = [[v, k] for k, v in users.items()]
    users_list.sort(reverse=1)
    users_list = [[k, v] for v, k in users_list]
    resolutions_list = [[v, k] for k, v in resolutions.items()]
    resolutions_list.sort(reverse=1)
    resolutions_list = [[k, v] for v, k in resolutions_list]

    width = u'1000px'
    height = u'250px'
    dates_graph_data = u', '.join([u'["%s", %s]' % (convert2unix(k), v) for k, v in dates_list])
    dates_graph = u"""<div id="dates_graph" style="width: %s;height: %s;"></div>
    <script type="text/javascript">
    $(function () {
        var dates_graph_data_2013 = [%s];
        var dates_graph_data_2012 = [["1377907200000", 525], ["1377993600000", 7641], ["1378080000000", 8638], ["1378166400000", 6954], ["1378252800000", 7276], ["1378339200000", 7946], ["1378425600000", 6513], ["1378512000000", 7268], ["1378598400000", 8386], ["1378684800000", 10372], ["1378771200000", 10613], ["1378857600000", 8214], ["1378944000000", 8694], ["1379030400000", 9046], ["1379116800000", 8725], ["1379203200000", 8627], ["1379289600000", 11119], ["1379376000000", 9520], ["1379462400000", 8408], ["1379548800000", 7387], ["1379635200000", 8284], ["1379721600000", 10391], ["1379808000000", 10656], ["1379894400000", 14308], ["1379980800000", 11642], ["1380067200000", 12848], ["1380153600000", 13158], ["1380240000000", 17252], ["1380326400000", 20409], ["1380412800000", 26966], ["1380499200000", 47387], ["1380585600000", 5554]];
        var dates_graph_data_2011 = [["1377907200000", 222], ["1377993600000", 2373], ["1378080000000", 1560], ["1378166400000", 2211], ["1378252800000", 3473], ["1378339200000", 3333], ["1378425600000", 2968], ["1378512000000", 3050], ["1378598400000", 2850], ["1378684800000", 3146], ["1378771200000", 3546], ["1378857600000", 4306], ["1378944000000", 4069], ["1379030400000", 3755], ["1379116800000", 3378], ["1379203200000", 4762], ["1379289600000", 3596], ["1379376000000", 4648], ["1379462400000", 7038], ["1379548800000", 5095], ["1379635200000", 4185], ["1379721600000", 4669], ["1379808000000", 4390], ["1379894400000", 4807], ["1379980800000", 6123], ["1380067200000", 8159], ["1380153600000", 6691], ["1380240000000", 9158], ["1380326400000", 10408], ["1380412800000", 13188], ["1380499200000", 21971], ["1380585600000", 927]];
       
        var dates_graph = $("#dates_graph");
        var dates_graph_data = [{ data: dates_graph_data_2013, label: "WLM 2013"}, { data: dates_graph_data_2012, label: "WLM 2012"}, { data: dates_graph_data_2011, label: "WLM 2011"}];
        var dates_graph_options = { xaxis: { mode: "time", min: (new Date("2013/08/31")).getTime(), max: (new Date("2013/10/01")).getTime() }, lines: { show: true }, points: { show: true }, legend: { noColumns: 3, position: "nw" }, grid: { hoverable: true }, clickable: true, hoverable: true };
        $.plot(dates_graph, dates_graph_data, dates_graph_options);
    });
    
    //from http://people.iola.dk/olau/flot/examples/interacting.html
    function showTooltip(x, y, contents) {
        $('<div id="tooltip">' + contents + '</div>').css( {
            position: 'absolute',
            display: 'none',
            top: y + 5,
            left: x + 12,
            border: '1px solid #fdd',
            padding: '2px',
            'background-color': '#fee',
            opacity: 0.80
        }).appendTo("body").fadeIn(200);
    }

    var previousPoint = null;
    $("#dates_graph").bind("plothover", function (event, pos, item) {
        $("#x").text(pos.x.toFixed(2));
        $("#y").text(pos.y.toFixed(2));
        
        if (item) {
            if (previousPoint != item.datapoint) {
                previousPoint = item.datapoint;
                
                $("#tooltip").remove();
                var x = item.datapoint[0].toFixed(2),
                    y = item.datapoint[1].toFixed(2);
                
                showTooltip(item.pageX, item.pageY,
                            "y = "+Math.round(y));
            }
        } else {
            $("#tooltip").remove();
            previousPoint = null;            
        }
    });

    </script>""" % (width, height, dates_graph_data)

    hours_graph_data = u', '.join([u'["%s", %s]' % (k, v) for k, v in hours_list])
    hours_graph = u"""<div id="hours_graph" style="width: %s;height: %s;"></div>
    <script type="text/javascript">
    $(function () {
        var hours_graph_data = [%s];
       
        var hours_graph = $("#hours_graph");
        var hours_graph_data = [ hours_graph_data, ];
        var hours_graph_options = { xaxis: { mode: null, tickSize: 1, tickDecimals: 0, min: 1, max: 23}, bars: { show: true, barWidth: 0.6 }, points: { show: false }, legend: { noColumns: 1 }, grid: { hoverable: true }, };
        $.plot(hours_graph, hours_graph_data, hours_graph_options);
    });
    </script>""" % (width, height, hours_graph_data)
    
    countries_rank = u''
    c = 0
    for k, v in countries_list:
        c += 1
        countries_rank += u'<tr><td>%s</td><td>%s</td><td><a href="http://commons.wikimedia.org/wiki/Category:%s">%s</a></td><td>%d</td><td>%.1f</td><td><a href="http://toolserver.org/~superzerocool/wlm/?pais=%s">Details</a></td></tr>\n' % (c, countrynames[k], uploadcats[k], countries[k]['files'], len(countries[k]['uploaders']), countries[k]['size']/1024.0/1024, k)
    countries_rank += u'<tr><td></td><td><b>Total</b></td><td><b><a href="http://commons.wikimedia.org/wiki/Category:Images from Wiki Loves Monuments %s">%s</a></b></td><td><b>%d</b></td><td><b>%.1f</b></td><td></td></tr>\n' % (year, sum([countries[k]['files'] for k in countries.keys()]), len(users.keys()), sum([countries[k]['size'] for k in countries.keys()])/1024.0/1024)
    countries_rank = u"""<table id="countries" class="wikitable" style="text-align: center;">
    <tr><th>#</th><th>Country</th><th>Files</th><th>Uploaders</th><th>MBytes</th><th>Details</th></tr>
    %s
    </table>""" % (countries_rank)
    
    users_rank = u''
    c = 0
    for k, v in users_list[:100]:
        c += 1
        users_rank += u'<tr><td>%s</td><td><a href="http://commons.wikimedia.org/wiki/User:%s">%s</a></td><td><a href="http://commons.wikimedia.org/wiki/Special:ListFiles/%s">%s</a></td><td>%.1f</td></tr>' % (c, k, k, k, users[k]['files'], users[k]['size']/1024.0/1024)
    users_rank += u'<tr><td></td><td><b>Total</b></td><td><b><a href="http://commons.wikimedia.org/wiki/Category:Images from Wiki Loves Monuments %s">%s</a></b></td><td><b>%.1f</b></td></tr>' % (year, sum([users[k]['files'] for k in users.keys()]), sum([users[k]['size'] for k in users.keys()])/1024.0/1024)
    users_rank = u"""<table id="uploaders" class="wikitable" style="text-align: center;">
    <tr><th>#</th><th>Uploader</th><th>Files</th><th>MBytes</th></tr>
    %s
    </table>""" % (users_rank)
    
    resolutions_rank = u''
    c = 0
    for k, v in resolutions_list[:15]:
        c += 1
        resolutions_rank += u'<tr><td>%s</td><td>%s</td><td>%s</td><td>%.1f</td></tr>' % (c, k, resolutions[k]['files'], resolutions[k]['size']/1024.0/1024)
    resolutions_rank += u'<tr><td></td><td><b>Total</b></td><td><b><a href="http://commons.wikimedia.org/wiki/Category:Images from Wiki Loves Monuments %s">%s</a></b></td><td><b>%.1f</b></td></tr>' % (year, sum([resolutions[k]['files'] for k in resolutions.keys()]), sum([resolutions[k]['size'] for k in resolutions.keys()])/1024.0/1024)
    resolutions_rank = u"""<table id="resolutions" class="wikitable" style="text-align: center;">
    <tr><th>#</th><th>Resolution</th><th>Files</th><th>MBytes</th></tr>
    %s
    </table>""" % (resolutions_rank)
    
    sizes_rank = u''
    c = 0
    for size, title, username, country in sizes_list[:15]: 
        c += 1
        sizes_rank += u'<tr><td>%s</td><td><a href="http://commons.wikimedia.org/wiki/File:%s">%s</a></td><td>%.1f</td><td><a href="http://commons.wikimedia.org/wiki/User:%s">%s</a></td><td>%s</td></tr>' % (c, title, len(title)>10 and (u'%s...' % title[:10]) or title, size/1024.0/1024, username, username, countrynames[country])
    sizes_rank += u'<tr><td></td><td><b>Total</b></td><td><b>%.1f</b></td><td></td><td></td></tr>' % (sum([resolutions[k]['size'] for k in resolutions.keys()])/1024.0/1024)
    sizes_rank = u"""<table id="sizes" class="wikitable" style="text-align: center;">
    <tr><th>#</th><th>File</th><th>MBytes</th><th>Uploader</th><th>Country</th></tr>
    %s
    </table>""" % (sizes_rank)
    
    intro = u"<b>%s files</b> by <b>%s uploaders</b> from <b>%s countries</b> so far" % (sum([countries[k]['files'] for k in countries.keys()]), len(users.keys()), len(countries.keys()))
    output = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Wiki Loves Monuments statistics</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<link rel="stylesheet" type="text/css" href="wlm.css" />
<script language="javascript" type="text/javascript" src="modules/jquery.js"></script>
<script language="javascript" type="text/javascript" src="modules/jquery.flot.js"></script>
</head>

<body style="background-color: white;">

<center>
<table border=0 cellpadding=0px width=%s style="text-align: center;">
<tr>
<td valign=middle ><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/LUSITANA_WLM_2011_d.svg/120px-LUSITANA_WLM_2011_d.svg.png" /></td>
<td valign=top width=99%%>
<br/><big><big><big><b><a href="index.php">Wiki <i>Loves</i> Monuments</a></b></big></big></big>
<br/><b>September %s</b>
<br/><br/>%s
<br/><br/>Uploads <a href="#day">per day</a> and <a href="#hour">per hour</a> - Rankings for <a href="#countries">countries</a>, <a href="#uploaders">uploaders</a>, <a href="#sizes">sizes</a> and <a href="#resolutions">resolutions</a>
</td>
<td valign=middle><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/LUSITANA_WLM_2011_d.svg/120px-LUSITANA_WLM_2011_d.svg.png" /></td>
</tr>
</table>

<h2 id="day">Uploads per day</h2>
%s

<h2 id="hour">Uploads per hour</h2>
%s

<h2 id="detailed">Detailed statistics</h2>
<table border=0>
<tr>
<td valign=top>
<center>
<!-- countries rank -->%s
<!-- resolutions rank -->%s
<!-- sizes rank -->%s
</center>
</td>
<td valign=top>
<center>
<!-- users rank -->%s
</center>
</td>
</tr>
</table>

Download 2013 metadata and make your own statistics: <a href="files.txt">CSV</a> and <a href="files.json">JSON</a>
<br/><br/><b>See also:</b> <a href="stats-2012.php">2012 stats</a> (<a href="files-2012.txt">2012 metadata</a>) and <a href="stats-2011.php">2011 stats</a> (<a href="files-2011.txt">2011 metadata</a>)
<br/><br/><b>Other statistics:</b> <a href="http://toolserver.org/~superzerocool/wlm/?pais=germany">country details</a> (Superzerocool), <a href="http://www.geobib.fr/mh/stats/">cumulative</a> (Sylvain), <a href="http://wikizabytki.pl/stats/">country race</a> (Yarl) and <a href="https://commons.wikimedia.org/wiki/Commons:Wiki_Loves_Monuments_2013/Tools">many more</a>!
<br/><br/>

<i><b>Last update:</b> %s (UTC). Developed by <a href="http://toolserver.org/~emijrp/">emijrp</a> using <a href="http://code.google.com/p/flot/">flot</a>. <a href="http://code.google.com/p/toolserver/source/browse/trunk/wlm/wlmstats.py">Source code</a> is GPL. Visits: <?php include ("../visits.php"); ?></i>

</center>

</body>
</html>""" % (width, year, intro, dates_graph, hours_graph, countries_rank, resolutions_rank, sizes_rank, users_rank, datetime.datetime.now())

    f = open('%s/stats.php' % (path), 'w')
    f.write(output.encode('utf-8'))
    f.close()

if __name__ == '__main__':
    main()
