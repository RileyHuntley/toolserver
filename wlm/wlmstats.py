#!/usr/bin/env python
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

import catlib
import datetime
import os
import pagegenerators
import re
import time
import wikipedia

#wlm counter con contador de subidas y megabytes
#http://commons.wikimedia.org/wiki/Commons:Wiki_Loves_Monuments_2012/CentralNotice

path = "/home/emijrp/public_html/wlm"
uploadcats = { 
    u'andorra': u'Images from Wiki Loves Monuments 2012 in Andorra', 
    u'argentina': u'Images from Wiki Loves Monuments 2012 in Argentina', 
    u'austria': u'Images from Wiki Loves Monuments 2012 in Austria', 
    u'belarus': u'Images from Wiki Loves Monuments 2012 in Belarus', 
    u'belgium': u'Images from Wiki Loves Monuments 2012 in Belgium', 
    u'canada': u'Images from Wiki Loves Monuments 2012 in Canada', 
    u'chile': u'Images from Wiki Loves Monuments 2012 in Chile', 
    u'colombia': u'Images from Wiki Loves Monuments 2012 in Colombia', 
    u'czechrepublic‎': u'Images from Wiki Loves Monuments 2012 in the Czech Republic‎', 
    u'denmark': u'Images from Wiki Loves Monuments 2012 in Denmark', 
    u'estonia': u'Images from Wiki Loves Monuments 2012 in Estonia', 
    u'france': u'Images from Wiki Loves Monuments 2012 in France', 
    u'germany': u'Images from Wiki Loves Monuments 2012 in Germany', 
    u'ghana': 'uImages from Wiki Loves Monuments 2012 in Ghana', 
    u'hungary': u'Images from Wiki Loves Monuments 2012 in Hungary', 
    u'india': u'Images from Wiki Loves Monuments 2012 in India', 
    u'israel': u'Images from Wiki Loves Monuments 2012 in Israel', 
    u'italy': u'Images from Wiki Loves Monuments 2012 in Italy', 
    u'kenya': u'Images from Wiki Loves Monuments 2012 in Kenya', 
    u'liechtenstein‎': u'Images from Wiki Loves Monuments 2012 in Liechtenstein‎', 
    u'luxembourg‎': u'Images from Wiki Loves Monuments 2012 in Luxembourg‎', 
    u'mexico': u'Images from Wiki Loves Monuments 2012 in Mexico', 
    u'netherlands‎': u'Images from Wiki Loves Monuments 2012 in the Netherlands‎', 
    u'norway‎': u'Images from Wiki Loves Monuments 2012 in Norway‎', 
    u'panama': u'Images from Wiki Loves Monuments 2012 in Panama', 
    u'philippines‎': u'Images from Wiki Loves Monuments 2012 in the Philippines‎', 
    u'poland': u'Images from Wiki Loves Monuments 2012 in Poland', 
    u'romania': u'Images from Wiki Loves Monuments 2012 in Romania', 
    u'russia': u'Images from Wiki Loves Monuments 2012 in Russia', 
    u'serbia': u'Images from Wiki Loves Monuments 2012 in Serbia', 
    u'southafrica': u'Images from Wiki Loves Monuments 2012 in South Africa', 
    u'southtyrol': u'Images from Wiki Loves Monuments 2012 in South Tyrol', 
    u'spain': u'Images from Wiki Loves Monuments 2012 in Spain', 
    u'sweden': u'Images from Wiki Loves Monuments 2012 in Sweden', 
    u'switzerland‎': u'Images from Wiki Loves Monuments 2012 in Switzerland‎', 
    u'ukraine': u'Images from Wiki Loves Monuments 2012 in Ukraine', 
    u'unitedstates': u'Images from Wiki Loves Monuments 2012 in the United States', 
}

countrynames = { 
    u'andorra': u'Andorra', 
    u'argentina': u'Argentina', 
    u'austria': u'Austria', 
    u'belarus': u'Belarus', 
    u'belgium': u'Belgium', 
    u'canada': u'Canada', 
    u'chile': u'Chile', 
    u'colombia': u'Colombia', 
    u'czechrepublic‎': u'Czech Republic‎', 
    u'denmark': u'Denmark', 
    u'estonia': u'Estonia', 
    u'france': u'France', 
    u'germany': u'Germany', 
    u'ghana': 'uGhana', 
    u'hungary': u'Hungary', 
    u'india': u'India', 
    u'israel': u'Israel', 
    u'italy': u'Italy', 
    u'kenya': u'Kenya', 
    u'liechtenstein‎': u'Liechtenstein‎', 
    u'luxembourg‎': u'Luxembourg‎', 
    u'mexico': u'Mexico', 
    u'netherlands‎': u'Netherlands‎', 
    u'norway‎': u'Norway‎', 
    u'panama': u'Panama', 
    u'philippines‎': u'Philippines‎', 
    u'poland': u'Poland', 
    u'romania': u'Romania', 
    u'russia': u'Russia', 
    u'serbia': u'Serbia', 
    u'southafrica': u'South Africa', 
    u'southtyrol': u'South Tyrol', 
    u'spain': u'Spain', 
    u'sweden': u'Sweden', 
    u'switzerland‎': u'Switzerland‎', 
    u'ukraine': u'Ukraine', 
    u'unitedstates': u'United States', 
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
    filename = 'files.txt'
    if os.path.exists("%s/%s" % (path, filename)):
        files = [i.split(';;;') for i in unicode(open("%s/%s" % (path, filename)).read(), 'utf-8').strip().splitlines()]
    else:
        files = []

    #adding new files metadata
    for country in uploadcats.keys():
        #continue
        cat = catlib.Category(wikipedia.Site("commons", "commons"), u"Category:%s" % uploadcats[country])
        gen = pagegenerators.CategorizedPageGenerator(cat, start="!")
        pre = pagegenerators.PreloadingGenerator(gen, pageNumber=250)
        for image in pre:
            #(datetime, username, resolution, size, comment)
            if image.title() not in [i[0] for i in files]:
                if len(files) % 50 == 0:
                    print len(files)
                date, username, resolution, size, comment = image.getFileVersionHistory()[-1]
                comment = re.sub(ur"(?im)\s", ur" ", comment)
                files.append([image.title(), country, date, username, resolution, str(size), comment])

    #saving files metadata
    print len(files), 'files'
    f = open("%s/%s" % (path, filename), 'w')
    output = u'\n'.join([u';;;'.join(i) for i in files])
    f.write(output.encode('utf-8'))
    f.close()

    #stats
    #File:Woodstock - Old Carleton Court House Side.JPG;;;2012-09-01T04:17:51Z;;;Amqui;;;2736×3648;;;4672852;;;User created page with UploadWizard
    dates = {}
    hours = {}
    users = {}
    countries = {}
    resolutions = {}
    sizes_list = []
    for title, country, date, username, resolution, size, comment in files:
        if countries.has_key(country):
            countries[country]['files'] += 1
            countries[country]['size'] += int(size)
            if not username in countries[country]['uploaders']:
                countries[country]['uploaders'].append(username)
        else:
            countries[country] = { 'files': 1, 'size': int(size), 'uploaders': [username]}
        d = '%sT00:00:00Z' % (date.split('T')[0])
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

    width = '800px'
    height = '250px'
    dates_graph_data = u', '.join([u'["%s", %s]' % (convert2unix(k), v) for k, v in dates_list])
    dates_graph = u"""<div id="dates_graph" style="width: %s;height: %s;"></div>
    <script type="text/javascript">
    $(function () {
        var dates_graph_data = [%s];
       
        var dates_graph = $("#dates_graph");
        var dates_graph_data = [ dates_graph_data, ];
        var dates_graph_options = { xaxis: { mode: "time", min: (new Date("2012/08/31")).getTime(), max: (new Date("2012/09/30")).getTime() }, bars: { show: false, barWidth: 0.6 }, lines: { show: true }, points: { show: true }, legend: { noColumns: 1 }, grid: { hoverable: true }, clickable: true, hoverable: true
};
        $.plot(dates_graph, dates_graph_data, dates_graph_options);
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
        countries_rank += u'<tr><td>%s</td><td>%s</td><td><a href="http://commons.wikimedia.org/wiki/Category:%s">%s</a></td><td>%d</td><td>%.1f</td></tr>\n' % (c, countrynames[k], uploadcats[k], countries[k]['files'], len(countries[k]['uploaders']), countries[k]['size']/1024.0/1024)
    countries_rank += u'<tr><td></td><td><b>Total</b></td><td><b><a href="http://commons.wikimedia.org/wiki/Category:Images from Wiki Loves Monuments 2012">%s</a></b></td><td><b>%d</b></td><td><b>%.1f</b></td></tr>\n' % (sum([countries[k]['files'] for k in countries.keys()]), sum([len(countries[k]['uploaders']) for k in countries.keys()]), sum([countries[k]['size'] for k in countries.keys()])/1024.0/1024)
    countries_rank = u"""<table id="countries" class="wikitable" style="text-align: center;">
    <tr><th>#</th><th>Country</th><th>Files</th><th>Uploaders</th><th>MBytes</th></tr>
    %s
    </table>""" % (countries_rank)
    
    users_rank = u''
    c = 0
    for k, v in users_list[:100]:
        c += 1
        users_rank += u'<tr><td>%s</td><td><a href="http://commons.wikimedia.org/wiki/User:%s">%s</a></td><td><a href="http://commons.wikimedia.org/wiki/Special:ListFiles/%s">%s</a></td><td>%.1f</td></tr>' % (c, k, k, k, users[k]['files'], users[k]['size']/1024.0/1024)
    users_rank += u'<tr><td></td><td><b>Total</b></td><td><b><a href="http://commons.wikimedia.org/wiki/Category:Images from Wiki Loves Monuments 2012">%s</a></b></td><td><b>%.1f</b></td></tr>' % (sum([users[k]['files'] for k in users.keys()]), sum([users[k]['size'] for k in users.keys()])/1024.0/1024)
    users_rank = u"""<table id="users" class="wikitable" style="text-align: center;">
    <tr><th>#</th><th>Uploader</th><th>Files</th><th>MBytes</th></tr>
    %s
    </table>""" % (users_rank)
    
    resolutions_rank = u''
    c = 0
    for k, v in resolutions_list[:15]:
        c += 1
        resolutions_rank += u'<tr><td>%s</td><td>%s</td><td>%s</td><td>%.1f</td></tr>' % (c, k, resolutions[k]['files'], resolutions[k]['size']/1024.0/1024)
    resolutions_rank += u'<tr><td></td><td><b>Total</b></td><td><b><a href="http://commons.wikimedia.org/wiki/Category:Images from Wiki Loves Monuments 2012">%s</a></b></td><td><b>%.1f</b></td></tr>' % (sum([resolutions[k]['files'] for k in resolutions.keys()]), sum([resolutions[k]['size'] for k in resolutions.keys()])/1024.0/1024)
    resolutions_rank = u"""<table id="users" class="wikitable" style="text-align: center;">
    <tr><th>#</th><th>Resolution</th><th>Files</th><th>MBytes</th></tr>
    %s
    </table>""" % (resolutions_rank)
    
    sizes_rank = u''
    c = 0
    for size, title, username, country in sizes_list[:15]: 
        c += 1
        sizes_rank += u'<tr><td>%s</td><td><a href="http://commons.wikimedia.org/wiki/%s">%s</a></td><td>%.1f</td><td><a href="http://commons.wikimedia.org/wiki/User:%s">%s</a></td><td>%s</td></tr>' % (c, title, len(title)>5+15 and (u'%s...' % title[5:15]) or title[5:], size/1024.0/1024, username, username, countrynames[country])
    sizes_rank += u'<tr><td></td><td><b>Total</b></td><td><b>%.1f</b></td><td></td><td></td></tr>' % (sum([resolutions[k]['size'] for k in resolutions.keys()])/1024.0/1024)
    sizes_rank = u"""<table id="sizes" class="wikitable" style="text-align: center;">
    <tr><th>#</th><th>File</th><th>MBytes</th><th>Uploader</th><th>Country</th></tr>
    %s
    </table>""" % (sizes_rank)
    
    intro = u"%s files by %s uploaders from %s countries so far" % (sum([countries[k]['files'] for k in countries.keys()]), len(users.keys()), len(countries.keys()))
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
    <table border=0 cellpadding=5px width=%s style="text-align: center;">
    <tr>
    <td><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/LUSITANA_WLM_2011_d.svg/100px-LUSITANA_WLM_2011_d.svg.png" /></td>
    <td valign=top width=99%%><big><big><big><b><a href="index.php">Wiki <i>Loves</i> Monuments</a></b></big></big></big><br/><b>September 2012</b><br/><br/>%s<br/><a href="#day">Uploads per day</a> - <a href="#hour">Uploads per hour</a> - <a href="#countries">Countries ranking</a> - <a href="#uploaders">Uploaders ranking</a> - <a href="#sizes">Sizes ranking</a> - <a href="#resolutions">Resolutions ranking</a></td>
    <td><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/LUSITANA_WLM_2011_d.svg/100px-LUSITANA_WLM_2011_d.svg.png" /></td>
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
    
    (<a href="files.txt">Download metadata and make your own statistics</a>)
    <br/><br/>
    
    <i>Last update: %s (UTC). Developed by <a href="http://toolserver.org/~emijrp/">emijrp</a> using <a href="http://code.google.com/p/flot/">flot</a>. Visits: <?php include ("../visits.php"); ?></i>
    
    </center>

    </body>
    </html>
    """ % (width, intro, dates_graph, hours_graph, countries_rank, resolutions_rank, sizes_rank, users_rank, datetime.datetime.now())

    f = open('%s/stats.php' % (path), 'w')
    f.write(output.encode('utf-8'))
    f.close()

if __name__ == '__main__':
    main()

