# -*- coding: utf-8 -*-
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
import time
import wikipedia

countries = {
'AD': u'Andorra',
'AE': u'United Arab Emirates',
'AF': u'Afghanistan',
'AG': u'Antigua and Barbuda',
'AI': u'Anguilla',
'AL': u'Albania',
'AM': u'Armenia',
'AN': u'Netherlands Antilles',
'AO': u'Angola',
'AQ': u'Antarctica',
'AR': u'Argentina',
'AS': u'American Samoa',
'AT': u'Austria',
'AU': u'Australia',
'AW': u'Aruba',
'AX': u'Aland Islands',
'AZ': u'Azerbaijan',
'BA': u'Bosnia and Herzegovina',
'BB': u'Barbados',
'BD': u'Bangladesh',
'BE': u'Belgium',
'BF': u'Burkina Faso',
'BG': u'Bulgaria',
'BH': u'Bahrain',
'BI': u'Burundi',
'BJ': u'Benin',
'BL': u'Saint Barthélemy',
'BM': u'Bermuda',
'BN': u'Brunei',
'BO': u'Bolivia',
'BR': u'Brazil',
'BS': u'Bahamas',
'BT': u'Bhutan',
'BV': u'Bouvet Island',
'BW': u'Botswana',
'BY': u'Belarus',
'BZ': u'Belize',
'CA': u'Canada',
'CC': u'Cocos Islands',
'CD': u'Democratic Republic of the Congo',
'CF': u'Central African Republic',
'CG': u'Republic of the Congo',
'CH': u'Switzerland',
'CI': u'Ivory Coast',
'CK': u'Cook Islands',
'CL': u'Chile',
'CM': u'Cameroon',
'CN': u'China',
'CO': u'Colombia',
'CR': u'Costa Rica',
'CU': u'Cuba',
'CV': u'Cape Verde',
'CX': u'Christmas Island',
'CY': u'Cyprus',
'CZ': u'Czech Republic',
'DE': u'Germany',
'DJ': u'Djibouti',
'DK': u'Denmark',
'DM': u'Dominica',
'DO': u'Dominican Republic',
'DZ': u'Algeria',
'EC': u'Ecuador',
'EE': u'Estonia',
'EG': u'Egypt',
'EH': u'Western Sahara',
'ER': u'Eritrea',
'ES': u'Spain',
'ET': u'Ethiopia',
'FI': u'Finland',
'FJ': u'Fiji',
'FK': u'Falkland Islands',
'FM': u'Micronesia',
'FO': u'Faroe Islands',
'FR': u'France',
'GA': u'Gabon',
'GB': u'United Kingdom',
'GD': u'Grenada',
'GE': u'Georgia',
'GF': u'French Guiana',
'GG': u'Guernsey',
'GH': u'Ghana',
'GI': u'Gibraltar',
'GL': u'Greenland',
'GM': u'Gambia',
'GN': u'Guinea',
'GP': u'Guadeloupe',
'GQ': u'Equatorial Guinea',
'GR': u'Greece',
'GS': u'South Georgia and the South Sandwich Islands',
'GT': u'Guatemala',
'GU': u'Guam',
'GW': u'Guinea-Bissau',
'GY': u'Guyana',
'HK': u'Hong Kong',
'HM': u'Heard Island and McDonald Islands',
'HN': u'Honduras',
'HR': u'Croatia',
'HT': u'Haiti',
'HU': u'Hungary',
'ID': u'Indonesia',
'IE': u'Ireland',
'IL': u'Israel',
'IM': u'Isle of Man',
'IN': u'India',
'IO': u'British Indian Ocean Territory',
'IQ': u'Iraq',
'IR': u'Iran',
'IS': u'Iceland',
'IT': u'Italy',
'JE': u'Jersey',
'JM': u'Jamaica',
'JO': u'Jordan',
'JP': u'Japan',
'KE': u'Kenya',
'KG': u'Kyrgyzstan',
'KH': u'Cambodia',
'KI': u'Kiribati',
'KM': u'Comoros',
'KN': u'Saint Kitts and Nevis',
'KP': u'North Korea',
'KR': u'South Korea',
'XK': u'Kosovo',
'KW': u'Kuwait',
'KY': u'Cayman Islands',
'KZ': u'Kazakhstan',
'LA': u'Laos',
'LB': u'Lebanon',
'LC': u'Saint Lucia',
'LI': u'Liechtenstein',
'LK': u'Sri Lanka',
'LR': u'Liberia',
'LS': u'Lesotho',
'LT': u'Lithuania',
'LU': u'Luxembourg',
'LV': u'Latvia',
'LY': u'Libya',
'MA': u'Morocco',
'MC': u'Monaco',
'MD': u'Moldova',
'ME': u'Montenegro',
'MF': u'Saint Martin',
'MG': u'Madagascar',
'MH': u'Marshall Islands',
'MK': u'Macedonia',
'ML': u'Mali',
'MM': u'Myanmar',
'MN': u'Mongolia',
'MO': u'Macao',
'MP': u'Northern Mariana Islands',
'MQ': u'Martinique',
'MR': u'Mauritania',
'MS': u'Montserrat',
'MT': u'Malta',
'MU': u'Mauritius',
'MV': u'Maldives',
'MW': u'Malawi',
'MX': u'Mexico',
'MY': u'Malaysia',
'MZ': u'Mozambique',
'NA': u'Namibia',
'NC': u'New Caledonia',
'NE': u'Niger',
'NF': u'Norfolk Island',
'NG': u'Nigeria',
'NI': u'Nicaragua',
'NL': u'Netherlands',
'NO': u'Norway',
'NP': u'Nepal',
'NR': u'Nauru',
'NU': u'Niue',
'NZ': u'New Zealand',
'OM': u'Oman',
'PA': u'Panama',
'PE': u'Peru',
'PF': u'French Polynesia',
'PG': u'Papua New Guinea',
'PH': u'Philippines',
'PK': u'Pakistan',
'PL': u'Poland',
'PM': u'Saint Pierre and Miquelon',
'PN': u'Pitcairn',
'PR': u'Puerto Rico',
'PS': u'Palestinian Territory',
'PT': u'Portugal',
'PW': u'Palau',
'PY': u'Paraguay',
'QA': u'Qatar',
'RE': u'Reunion',
'RO': u'Romania',
'RS': u'Serbia',
'RU': u'Russia',
'RW': u'Rwanda',
'SA': u'Saudi Arabia',
'SB': u'Solomon Islands',
'SC': u'Seychelles',
'SD': u'Sudan',
'SE': u'Sweden',
'SG': u'Singapore',
'SH': u'Saint Helena',
'SI': u'Slovenia',
'SJ': u'Svalbard and Jan Mayen',
'SK': u'Slovakia',
'SL': u'Sierra Leone',
'SM': u'San Marino',
'SN': u'Senegal',
'SO': u'Somalia',
'SR': u'Suriname',
'ST': u'Sao Tome and Principe',
'SV': u'El Salvador',
'SY': u'Syria',
'SZ': u'Swaziland',
'TC': u'Turks and Caicos Islands',
'TD': u'Chad',
'TF': u'French Southern Territories',
'TG': u'Togo',
'TH': u'Thailand',
'TJ': u'Tajikistan',
'TK': u'Tokelau',
'TL': u'East Timor',
'TM': u'Turkmenistan',
'TN': u'Tunisia',
'TO': u'Tonga',
'TR': u'Turkey',
'TT': u'Trinidad and Tobago',
'TV': u'Tuvalu',
'TW': u'Taiwan',
'TZ': u'Tanzania',
'UA': u'Ukraine',
'UG': u'Uganda',
'UM': u'United States Minor Outlying Islands',
'US': u'United States',
'UY': u'Uruguay',
'UZ': u'Uzbekistan',
'VA': u'Vatican',
'VC': u'Saint Vincent and the Grenadines',
'VE': u'Venezuela',
'VG': u'British Virgin Islands',
'VI': u'U.S. Virgin Islands',
'VN': u'Vietnam',
'VU': u'Vanuatu',
'WF': u'Wallis and Futuna',
'WS': u'Samoa',
'YE': u'Yemen',
'YT': u'Mayotte',
'ZA': u'South Africa',
'ZM': u'Zambia',
'ZW': u'Zimbabwe',
'CS': u'Serbia and Montenegro',

}

wikien = wikipedia.Site("en", "wikipedia")

def main_program(file_name):
    countrycode = file_name.split('.')[0].lower()
    rows = file(file_name).read().splitlines()
    n=0
    output={}
    header =u'{{User:Emijrp/Geonames/Cities1000/header}}\n'
    footer=u'{{User:Emijrp/Geonames/Cities1000/footer}}'
    while n<len(rows) and rows[n]: #evitamos errores con paises con pocos registros, o registro vacio al final
        #print rows[n]
        row = unicode(rows[n], 'utf-8')
        row = row.split('\t')
        
        geonameid = row[0]
        name = row[1]
        asciiname = row[2]
        alternatenames = row[3]
        latitude = row[4]
        longitude = row[5]
        lat='N'
        if float(latitude)<0: lat='S'
        latitudeabs = abs(float(latitude))
        lon='E'
        if float(longitude)<0: lon='W'
        longitudeabs = abs(float(longitude))
        featureclass = row[6]
        featurecode = row[7]
        countrycode = row[8]
        cc2 = row[9]
        admin1code = row[10]
        admin2code = row[11]
        admin3code = row[12]
        admin4code = row[13]
        population = row[14]
        elevation = row[15]
        gtopo30 = row[16]
        timezone = row[17]
        date = row[18]
        
        if int(population)<1000:
            n+=1
            continue
        
        names = sets.Set()
        names.add(name)
        names.add(asciiname)
        names.add(u'%s, %s' % (name, countries[countrycode]))
        names.add(u'%s, %s' % (asciiname, countries[countrycode]))
        
        coord = u"{{Coord|%s|%s|display=inline}}" % (latitude, longitude)
        search = u"{{Search|%s}}" % (re.sub(ur" ", ur"+", u"%s %s" % (name, countries[countrycode])))
        names_=u''
        if len(names)>0:
            names.remove(name)
            names_ = u'[['
            names_ += u']], [['.join(names)
            names_ += u']]'
        coordurl=u'[http://toolserver.org/~geohack/geohack.php?params=%s_%s_%s_%s_ %sº%s %sº%s]' % (latitudeabs, lat, longitudeabs, lon, latitudeabs, lat, longitudeabs, lon)
        out = u'[[%s]] %s || %s (%s) || %s || %s || %s || %s \n|-\n' % (name, search, featureclass, featurecode, population, coordurl, names_, date)
        if output.has_key(countrycode):
            output[countrycode].append([name, out])
        else:
            output[countrycode] = [[name, out]]
        n+=1
    
    countrylist=[]
    countrylist2=[]
    limit=500
    for country, outlist in output.items():
        outlist2=outlist
        outlist2.sort()
        outlist=[]
        for name, item in outlist2:
            outlist.append(item)
        countrylist.append([countries[country], country])
        countrylist2.append([country, countries[country]])
        offset = 0
        while offset < len(outlist):
            out = header
            c=offset
            for item in outlist[offset:offset+limit]:
                c+=1
                out += u'| %s || %s' % (c, item)
            out += footer
            out = re.sub(ur"\[\[ *\]\]", ur"", out)
            index = offset/limit+1
            page=wikipedia.Page(wikien, u"User:Emijrp/Geonames/Cities1000/%s/%s" % (country, index))
            print page.title()
            if not page.exists():
                page.put(out, u"From http://www.geonames.org")
            offset += limit
        
    countrylist.sort()
    
    """
    out=""
    for country, iso in countrylist:
        out += u"{{flagicon|%s}} [[User:Emijrp/Geonames/City1000/%s/1|%s]] - " % (country, iso, country)
    print out
    
    countrylist2.sort()
    out2=""
    for iso, country in countrylist2:
        out2 += u"| %s = %s \n" % (iso, country)
    print out2"""
    
    """#print output
    f=open('geonames.txt', 'w')
    f.write(output.encode('utf-8'))
    f.close()"""

#file_name = sys.argv[1]
file_name = 'cities1000.txt'
main_program(file_name)

