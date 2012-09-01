#!/usr/bin/env python
# -*- coding: utf-8 -*-

import catlib
import os
import pagegenerators
import re
import wikipedia

#wlm counter con contador de subidas y megabytes

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
    u'spain': u'Images from Wiki Loves Monuments 2012 in Spain', 
    u'sweden': u'Images from Wiki Loves Monuments 2012 in Sweden', 
    u'switzerland‎': u'Images from Wiki Loves Monuments 2012 in Switzerland‎', 
    u'ukraine': u'Images from Wiki Loves Monuments 2012 in Ukraine', 
    u'unitedstates': u'Images from Wiki Loves Monuments 2012 in the United States', 
}

#loading files metadata
filename = 'files.txt'
if os.path.exists(filename):
    files = [i.split(';;;') for i in unicode(open(filename).read(), 'utf-8').strip().splitlines()]
else:
    files = []

#adding new files metadata
for country in ['russia', 'canada']: #uploadcats.keys():
    cat = catlib.Category(wikipedia.Site("commons", "commons"), u"Category:%s" % uploadcats[country])
    gen = pagegenerators.CategorizedPageGenerator(cat, start="!")
    pre = pagegenerators.PreloadingGenerator(gen, pageNumber=250)
    for image in pre:
        #(datetime, username, resolution, size, comment)
        if image.title() not in [i[0] for i in files]:
            if len(files) % 10 == 0:
                print len(files)
            date, username, resolution, size, comment = image.getFileVersionHistory()[-1]
            comment = re.sub(ur"(?im)\s", ur" ", comment)
            files.append([image.title(), date, username, resolution, str(size), comment])

#saving files metadata
print len(files), 'files'
f = open(filename, 'w')
output = u'\n'.join([u';;;'.join(i) for i in files])
f.write(output.encode('utf-8'))
f.close()

#stats
#File:Woodstock - Old Carleton Court House Side.JPG;;;2012-09-01T04:17:51Z;;;Amqui;;;2736×3648;;;4672852;;;User created page with UploadWizard
dates = {}
hours = {}
users = {}
resolutions = {}
sizes_list = []
for title, date, username, resolution, size, comment in files:
    d = date.split('T')[0]
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
        users[username] += 1
    else:
        users[username] = 1
    if resolutions.has_key(resolution):
        resolutions[resolution] += 1
    else:
        resolutions[resolution] = 1
    sizes_list.append(size)

sizes_list.sort(reverse=1)
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
dates_graph_data = u', '.join([u'["%s", %s]' % (k.split('-')[2], v) for k, v in dates_list])
dates_graph = u"""<div id="dates_graph" style="width: %s;height: %s;"></div>
<script type="text/javascript">
$(function () {
    var dates_graph_data = [%s];
   
    var dates_graph = $("#dates_graph");
    var dates_graph_data = [ dates_graph_data, ];
    var dates_graph_options = { xaxis: { mode: null, tickSize: 1, tickDecimals: 0, min: 1, max: 30}, bars: { show: true, barWidth: 0.6 }, points: { show: false }, legend: { noColumns: 1 }, grid: { hoverable: true }, };
    $.plot(dates_graph, dates_graph_data, dates_graph_options);
});
</script>""" % (width, height, dates_graph_data)


output = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>Wiki Loves Monuments statistics</title>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<link rel="stylesheet" type="text/css" href="" />
<script language="javascript" type="text/javascript" src="modules/jquery.js"></script>
<script language="javascript" type="text/javascript" src="modules/jquery.flot.js"></script>
</head>

<body style="background-color: white;">

<center>
<big><big><big><b><a href="index.php" target="_blank">Wiki <i>Loves</i> Monuments</a></b></big></big></big>

%s

</center>

</body>
</html>
""" % (dates_graph)

f = open('%s/stats.html' % (path), 'w')
f.write(output.encode('utf-8'))
f.close()

