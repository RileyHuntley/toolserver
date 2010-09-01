#!/usr/bin/python
#
# Copyright (C) 2006 Milos Rancic, emijrp
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# 
# Text of GNU GPL license can be found at http://www.gnu.org/licenses/gnu.html

import re
import sets
import sys

countries = {
'aa': u'Aruba',
'ac': u'Antigua and Barbuda',
'av': u'Anguilla',
'sp': u'Spain',
}

def main_program(file_name):
    countrycode = file_name.split('.')[0]
    rows = file(file_name).read().split("\r\n")
    header = rows[0]
    n=1
    output =u'{{User:Emijrp/GNS/header}}\n'
    #output =u'{{User:Emijrp/GNS/header}}\n{| class="wikitable sortable" \n'
    #output += u'! %s !! Other \n|-\n' % (' !! '.join(header.split('\t'))) 
    while n<=500 and n<=len(rows) and rows[n]: #evitamos errores con paises con pocos registros, o registro vacio al final
        row = unicode(rows[n], 'utf-8')
        row = row.split('\t')
        #19 short form
        name = row[22]
        names = sets.Set()
        names.add(name)
        names.add(row[23])
        names.add(row[25])
        names.add(row[26])
        names.add(u'%s, %s' % (name, countries[countrycode]))
        type = row[9]
        date = row[28]
        coord = u"{{coord|%s|%s|display=inline}}" % (row[3], row[4])
        names_=u''
        if len(names)>1:
            names.remove(name)
            names_ = u'[['
            names_ += u']], [['.join(names)
            names_ += u']]'
        output += u'| %d || [[%s]] || %s || %s || %s || %s \n|-\n' % (n, name, type, coord, date, names_)
        n+=1
    #output+=u'|}\n{{User:Emijrp/GNS/footer}}'
    output+=u'{{User:Emijrp/GNS/footer}}'
    output = re.sub(ur"\[\[ *\]\]", ur"", output)
    #print output
    f=open('gns.txt', 'w')
    f.write(output.encode('utf-8'))
    f.close()

file_name = sys.argv[1]
main_program(file_name)

