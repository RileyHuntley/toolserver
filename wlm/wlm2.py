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

import _mysql
import datetime
import md5
import os
import re

path = '/home/emijrp/public_html/wlm'
codification = 'iso-8859-1'
conn = _mysql.connect(host='sql.toolserver.org', db='p_erfgoed_p', read_default_file='~/.my.cnf')
countrynames = {
    'ad': 'Andorra', 
    'ar': 'Argentina', 
    'at': 'Austria', 
    'by': 'Belarus',
    'ca': 'Canada',
    'ch': 'Switzerland',
    'cl': 'Chile',
    'co': 'Colombia',
    'cz': 'Czech Republic',
    'ee': 'Estonia',
    #'es': 'Spain',
    'fr': 'France',
    #'ie': 'Ireland',
    'il': 'Israel',
    'in': 'India',
    'it': 'Italy',
    'lu': 'Luxembourg', 
    #'mt': 'Malta', 
    'nl': 'Netherlands', 
    'pa': 'Panama',
    'pl': 'Poland',
    #'pt': 'Portugal',
    'ro': 'Romania',
    'rs': 'Serbia',
    'ru': 'Russia',
    #'sk': 'Slovakia',
    'ua': 'Ukraine',
    'us': 'United States',
    'za': 'South Africa',
}
capitals = {
    'us': 'us-nj',
}
wmurls = { 
    #'ad': '',
    'ar': 'http://www.wikimedia.org.ar', 
    #'at': '',
    'by': 'http://wikimedia.by', 
    'ca': 'http://wikimedia.ca', 
    'cl': 'http://www.wikimediachile.cl', 
    #'co': '',
    #'cz': '',
    #'ee': '',
    'es': 'http://www.wikimedia.org.es',
    #'fr': '',
    #'ie': '',
    #'il': '',
    #'in': '',
    #'it': '',
    #'lu': '',
    'mx': 'http://mx.wikimedia.org', 
    #'mt': '',
    #'nl': '',
    'pa': 'http://wlmpanama.org.pa', 
    #'pl': '',
    #'pt': '',
    #'ro': '',
    #'rs': '',
    #'sr': '', 
    #'sk': '', 
    #'ua': '' ,
    'us': 'http://wikimedia.org',
    #'za': '',
}
#generic logo http://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Wikimedia-logo.svg/80px-Wikimedia-logo.svg.png
wmlogourldefault = 'http://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Wikimedia-logo.svg/80px-Wikimedia-logo.svg.png'
wmlogourls = { 
    #'ad': '',
    'ar': 'http://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Wikimedia_Argentina_logo.svg/80px-Wikimedia_Argentina_logo.svg.png', 
    #'at': '',
    'by': 'http://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Wikimedia-logo.svg/80px-Wikimedia-logo.svg.png', 
    'ca': 'http://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Wikimedia_Canada_logo.svg/80px-Wikimedia_Canada_logo.svg.png', 
    'cl': 'http://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Wikimedia_Chile_logo.svg/80px-Wikimedia_Chile_logo.svg.png', 
    #'co': '',
    #'cz': '',
    #'ee': '',
    'es': 'http://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Wikimedia-es-logo.svg/80px-Wikimedia-es-logo.svg.png',
    #'fr': '',
    #'ie': '',
    #'il': '',
    #'in': '',
    #'it': '',
    #'lu': '',
    'mx': 'http://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Wikimedia_Mexico.svg/80px-Wikimedia_Mexico.svg.png', 
    #'mt': '',
    #'nl': '',
    'pa': 'http://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Wikimedia-logo.svg/80px-Wikimedia-logo.svg.png', 
    #'pl': '',
    #'pt': '',
    #'ro': '',
    #'rs': '', 
    #'ru': '',
    #'sk': '', 
    #'ua': '' ,
    'us': 'http://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Wikimedia-logo.svg/80px-Wikimedia-logo.svg.png',
    #'za': '',
}
wlmurls = { 
    'ad': 'http://wikilovesmonuments.cat',
    'ar': 'http://wikilovesmonuments.com.ar', 
    'at': 'http://wikilovesmonuments.at',
    'be': 'http://wikilovesmonuments.be',
    'by': 'http://wikilovesmonuments.by', 
    'ca': 'http://wikilovesmonuments.ca', 
    'ch': 'http://www.wikilovesmonuments.ch', 
    'cl': 'http://www.wikilovesmonuments.cl', 
    'co': 'http://www.wikilovesmonuments.co',
    'cz': 'http://www.wikilovesmonuments.cz',
    'de': 'http://www.wikilovesmonuments.de', 
    'dk': 'http://da.wikipedia.org/wiki/Wikipedia:Wiki_Loves_Monuments_2012', 
    'ee': 'http://wikilovesmonuments.ee',
    'es': 'http://www.wikilm.es',
    'fr': 'http://wikilovesmonuments.fr',
    'gh': 'http://commons.wikimedia.org/wiki/Commons:Wiki_Loves_Monuments_2012_in_Ghana',
    #'ie': '',
    'il': 'http://www.wlm.org.il',
    'in': 'http://www.wikilovesmonuments.in',
    'it': 'http://www.wikilovesmonuments.it',
    'ke': 'http://commons.wikimedia.org/wiki/Commons:Wiki_Loves_Monuments_2012_in_Kenya',
    'li': 'http://www.wikilovesmonuments.li',
    'lu': 'http://wikilovesmonuments.be',
    'mx': 'http://wikilovesmonuments.mx', 
    #'mt': '',
    'nl': 'http://www.wikilovesmonuments.nl',
    #'no': '',
    'pa': 'http://wlmpanama.org.pa', 
    'ph': 'http://www.wikilovesmonuments.ph', 
    'pl': 'http://pl.wikipedia.org/wiki/Wikipedia:Wiki_Lubi_Zabytki',
    #'pt': '',
    'ro': 'http://wikilovesmonuments.ro',
    'rs': 'http://wlm.wikimedia.rs',
    'ru': 'http://wikilovesmonuments.ru',
    'se': 'http://wikilovesmonuments.se', 
    #'sk': '', 
    'ua': 'http://wlm.org.ua' ,
    'us': 'http://wikilovesmonuments.us',
    'za': 'http://www.wikilovesmonuments.co.za',
}
iso3166 = {
    'AD':   u"Andorra",
    
    'AR':   u"Argentina",
    'AR-C': u"Ciudad Autónoma de Buenos Aires",
    'AR-B': u"Buenos Aires",
    'AR-K': u"Catamarca", 
    'AR-H': u"Chaco",
    'AR-U': u"Chubut",
    'AR-X': u"Córdoba",
    'AR-W': u"Corrientes",
    'AR-E': u"Entre Ríos",
    'AR-P': u"Formosa",
    'AR-Y': u"Jujuy",
    'AR-L': u"La Pampa",
    'AR-F': u"La Rioja",
    'AR-M': u"Mendoza",
    'AR-N': u"Misiones",
    'AR-Q': u"Neuquén",
    'AR-R': u"Río Negro",
    'AR-A': u"Salta",
    "AR-J": u"San Juan",
    "AR-D": u"San Luis",
    "AR-Z": u"Santa Cruz",
    "AR-S": u"Santa Fe",
    "AR-G": u"Santiago del Estero",
    "AR-V": u"Tierra del Fuego",
    "AR-T": u"Tucumán",
    
    "AT":   u"Austria",
    "AT-1": u"Burgenland",
    "AT-2": u"Kärnten",
    "AT-3": u"Niederösterreich",
    "AT-4": u"Oberösterreich",
    "AT-5": u"Salzburg",
    "AT-6": u"Steiermark",
    "AT-7": u"Tirol",
    "AT-8": u"Vorarlberg",
    "AT-9": u"Wien",
    
    'CA':    u"Canada",
    'CA-AB': u"Alberta",
    'CA-BC': u"British Columbia",
    'CA-MB': u"Manitoba",
    'CA-NB': u"New Brunswick",
    'CA-NL': u"Newfoundland",
    'CA-NS': u"Nova Scotia",
    'CA-NU': u"Nunavut",
    'CA-ON': u"Ontario",
    'CA-PE': u"Prince Edward Island",
    'CA-QC': u"Quebec",
    'CA-SK': u"Saskatchewan",
    'CA-NT': u"Northwest Territories",
    'CA-YT': u"Yukon Territory",
    
    'CH':    u"Switzerland",
    'CH-AG': u"Aargau",
    'CH-AR': u"Appenzell Ausserrhoden",
    'CH-AI': u"Appenzell Innerrhoden",
    'CH-BL': u"Basel-Landschaft",
    'CH-BS': u"Basel-Stadt",
    'CH-BE': u"Bern",
    'CH-FR': u"Freiburg",
    'CH-GE': u"Genève",
    'CH-GL': u"Glarus",
    'CH-GR': u"Graubünden",
    'CH-JU': u"Jura",
    'CH-LU': u"Luzern",
    'CH-NE': u"Neuchâtel",
    'CH-NW': u"Nidwalden",
    'CH-OW': u"Obwalden",
    'CH-SG': u"Sankt Gallen",
    'CH-SH': u"Schaffhausen",
    'CH-SZ': u"Schwyz",
    'CH-SO': u"Solothurn",
    'CH-TG': u"Thurgau",
    'CH-TI': u"Ticino",
    'CH-UR': u"Uri",
    'CH-VS': u"Wallis",
    'CH-VD': u"Vaud",
    'CH-ZG': u"Zug",
    'CH-ZH': u"Zürich",
    
    'CL':    u"Chile",
    'CL-AI': u"Aisén del General Carlos Ibañez del Campo",
    'CL-AN': u"Antofagasta",
    'CL-AR': u"Araucanía",
    'CL-AP': u"Arica y Parinacota",
    'CL-AT': u"Atacama",
    'CL-BI': u"Bío-Bío",
    'CL-CO': u"Coquimbo",
    'CL-LI': u"Libertador General Bernardo O'Higgins",
    'CL-LL': u"Los Lagos",
    'CL-LR': u"Los Ríos",
    'CL-MA': u"Magallanes",
    'CL-ML': u"Maule",
    'CL-RM': u"Región Metropolitana de Santiago",
    'CL-TA': u"Tarapacá",
    'CL-VS': u"Valparaíso",
    
    'CO': u"Colombia",
    
    'CZ': u"Czech Republic",
    'CZ-JC': u"Jihočeský kraj",
    'CZ-JM': u"Jihomoravský kraj",
    'CZ-KA': u"Karlovarský kraj",
    'CZ-KR': u"Královéhradecký kraj",
    'CZ-LI': u"Liberecký kraj",
    'CZ-MO': u"Moravskoslezský kraj",
    'CZ-PA': u"Pardubický kraj",
    'CZ-PR': u"Praha, hlavní město",
    'CZ-ST': u"Středočeský kraj",
    'CZ-US': u"Ústecký kraj",
    'CZ-VY': u"Vysočina",
    'CZ-ZL': u"Zlínský kraj",
    
    'EE':    u"Estonia",
    'EE-37': u"Harjumaa",
    'EE-39': u"Hiiumaa",
    'EE-44': u"Ida-Virumaa",
    'EE-49': u"Jõgevamaa",
    'EE-51': u"Järvamaa",
    'EE-57': u"Läänemaa",
    'EE-59': u"Lääne-Virumaa",
    'EE-65': u"Põlvamaa",
    'EE-67': u"Pärnumaa",
    'EE-70': u"Raplamaa",
    'EE-74': u"Saaremaa",
    'EE-78': u"Tartumaa",
    'EE-82': u"Valgamaa",
    'EE-84': u"Viljandimaa",
    'EE-86': u"Võrumaa",
    
    'FR':   u"France",
    'FR-A': u"Alsace",
    'FR-B': u"Aquitaine",
    'FR-C': u"Auvergne",
    'FR-P': u"Basse-Normandie",
    'FR-D': u"Bourgogne",
    'FR-E': u"Bretagne",
    'FR-F': u"Centre",
    'FR-G': u"Champagne-Ardenne",
    'FR-H': u"Corse",
    'FR-I': u"Franche-Comté",
    'FR-Q': u"Haute-Normandie",
    'FR-J': u"Île-de-France",
    'FR-K': u"Languedoc-Roussillon",
    'FR-L': u"Limousin",
    'FR-M': u"Lorraine",
    'FR-N': u"Midi-Pyrénées",
    'FR-O': u"Nord-Pas-de-Calais",
    'FR-R': u"Pays de la Loire",
    'FR-S': u"Picardie",
    'FR-T': u"Poitou-Charentes",
    'FR-U': u"Provence-Alpes-Côte d'Azur",
    'FR-V': u"Rhône-Alpes",
    
    'IN':    u"India",
    'IN-AP': u"Andhra Pradesh",
    'IN-AR': u"Arunachal Pradesh",
    'IN-AS': u"Assam",
    'IN-BR': u"Bihar",
    'IN-CT': u"Chhattisgarh",
    'IN-GA': u"Goa",
    'IN-GJ': u"Gujarat",
    'IN-HR': u"Haryana",
    'IN-HP': u"Himachal Pradesh",
    'IN-JK': u"Jammu and Kashmir",
    'IN-JH': u"Jharkhand",
    'IN-KA': u"Karnataka",
    'IN-KL': u"Kerala",
    'IN-MP': u"Madhya Pradesh",
    'IN-MH': u"Maharashtra",
    'IN-MN': u"Manipur",
    'IN-ML': u"Meghalaya",
    'IN-MZ': u"Mizoram",
    'IN-NL': u"Nagaland",
    'IN-OR': u"Orissa",
    'IN-PB': u"Punjab",
    'IN-RJ': u"Rajasthan",
    'IN-SK': u"Sikkim",
    'IN-TN': u"Tamil Nadu",
    'IN-TR': u"Tripura",
    'IN-UT': u"Uttarakhand",
    'IN-UP': u"Uttar Pradesh",
    'IN-WB': u"West Bengal",
    'IN-AN': u"Andaman and Nicobar Islands",
    'IN-CH': u"Chandigarh",
    'IN-DN': u"Dadra and Nagar Haveli",
    'IN-DD': u"Daman and Diu",
    'IN-DL': u"Delhi",
    'IN-LD': u"Lakshadweep",
    'IN-PY': u"Pondicherry (Puducherry)",
    
    'IT': u"Italy",
    
    'LU': u"Luxembourg",
    
    'MT': u"Malta",
    
    'NL':    u"Netherlands",
    'NL-DR': u"Drenthe",
    'NL-FL': u"Flevoland",
    'NL-FR': u"Fryslân",
    'NL-GE': u"Gelderland",
    'NL-GR': u"Groningen",
    'NL-LI': u"Limburg",
    'NL-NB': u"Noord-Brabant",
    'NL-NH': u"Noord-Holland",
    'NL-OV': u"Overijssel",
    'NL-UT': u"Utrecht",
    'NL-ZE': u"Zeeland",
    'NL-ZH': u"Zuid-Holland",

    'PA': u"Panamá", 
    
    'PL':    u"Poland", 
    'PL-DS': u"Dolnośląskie", 
    'PL-KP': u"Kujawsko-pomorskie", 
    'PL-LU': u"Lubelskie", 
    'PL-LB': u"Lubuskie", 
    'PL-LD': u"Łódzkie", 
    'PL-MA': u"Małopolskie", 
    'PL-MZ': u"Mazowieckie", 
    'PL-OP': u"Opolskie", 
    'PL-PK': u"Podkarpackie", 
    'PL-PD': u"Podlaskie", 
    'PL-PM': u"Pomorskie", 
    'PL-SL': u"Śląskie", 
    'PL-SK': u"Świętokrzyskie", 
    'PL-WN': u"Warmińsko-mazurskie", 
    'PL-WP': u"Wielkopolskie", 
    'PL-ZP': u"Zachodniopomorskie", 

    'PT':    u"Portugal",
    'PT-01': u"Aveiro",
    'PT-02': u"Beja",
    'PT-03': u"Braga",
    'PT-04': u"Bragança",
    'PT-05': u"Branco",
    'PT-06': u"Coimbra",
    'PT-07': u"Évora",
    'PT-08': u"Faro",
    'PT-09': u"Guarda",
    'PT-10': u"Leiria",
    'PT-11': u"Lisboa",
    'PT-12': u"Portalegre",
    'PT-13': u"Porto",
    'PT-14': u"Santarém",
    'PT-15': u"Setúbal",
    'PT-16': u"Viana do Castelo",
    'PT-17': u"Vila Real",
    'PT-18': u"Viseu",
    'PT-20': u"Região Autónoma dos Açores",
    'PT-30': u"Região Autónoma da Madeira",
    
    'RO':    u"Romania",
    'RO-AB': u"Alba",
    'RO-AR': u"Arad",
    'RO-AG': u"Argeș",
    'RO-BC': u"Bacău",
    'RO-BH': u"Bihor",
    'RO-BN': u"Bistrița-Năsăud",
    'RO-BT': u"Botoșani",
    'RO-BV': u"Brașov",
    'RO-BR': u"Brăila",
    'RO-BZ': u"Buzău",
    'RO-CS': u"Caraș-Severin",
    'RO-CL': u"Călărași",
    'RO-CJ': u"Cluj",
    'RO-CT': u"Constanța",
    'RO-CV': u"Covasna",
    'RO-DB': u"Dâmbovița",
    'RO-DJ': u"Dolj",
    'RO-GL': u"Galați",
    'RO-GR': u"Giurgiu",
    'RO-GJ': u"Gorj",
    'RO-HR': u"Harghita",
    'RO-HD': u"Hunedoara",
    'RO-IL': u"Ialomița",
    'RO-IS': u"Iași",
    'RO-IF': u"Ilfov",
    'RO-MM': u"Maramureș",
    'RO-MH': u"Mehedinți",
    'RO-MS': u"Mureș",
    'RO-NT': u"Neamț",
    'RO-OT': u"Olt",
    'RO-PH': u"Prahova",
    'RO-SM': u"Satu Mare",
    'RO-SJ': u"Sălaj",
    'RO-SB': u"Sibiu",
    'RO-SV': u"Suceava",
    'RO-TR': u"Teleorman",
    'RO-TM': u"Timiș",
    'RO-TL': u"Tulcea",
    'RO-VS': u"Vaslui",
    'RO-VL': u"Vâlcea",
    'RO-VN': u"Vrancea",
    'RO-B': u"București",
    
    'RU': u"Russia",
    
    'SK': u"Slovakia",
    'SK-BC': u"Banskobystrický kraj",
    'SK-BL': u"Bratislavský kraj",
    'SK-KI': u"Košický kraj",
    'SK-NI': u"Nitriansky kraj",
    'SK-PV': u"Prešovský kraj",
    'SK-TC': u"Trenčiansky kraj",
    'SK-TA': u"Trnavský kraj",
    'SK-ZI': u"Žilinský kraj",
    
    'RS': u"Serbia",
    
    'UA': u"Ukraine",
    'UA-': u"",
    
    'US':    u"United States",
    'US-AL': u"Alabama",
    'US-AK': u"Alaska",
    'US-AZ': u"Arizona",
    'US-AR': u"Arkansas",
    'US-CA': u"California",
    'US-CO': u"Colorado",
    'US-CT': u"Connecticut",
    'US-DE': u"Delaware",
    'US-FL': u"Florida",
    'US-GA': u"Georgia",
    'US-HI': u"Hawaii",
    'US-ID': u"Idaho",
    'US-IL': u"Illinois",
    'US-IN': u"Indiana",
    'US-IA': u"Iowa",
    'US-KS': u"Kansas",
    'US-KY': u"Kentucky",
    'US-LA': u"Louisiana",
    'US-ME': u"Maine",
    'US-MD': u"Maryland",
    'US-MA': u"Massachusetts",
    'US-MI': u"Michigan",
    'US-MN': u"Minnesota",
    'US-MS': u"Mississippi",
    'US-MO': u"Missouri",
    'US-MT': u"Montana",
    'US-NE': u"Nebraska",
    'US-NV': u"Nevada",
    'US-NH': u"New Hampshire",
    'US-NJ': u"New Jersey",
    'US-NM': u"New Mexico",
    'US-NY': u"New York",
    'US-NC': u"North Carolina",
    'US-ND': u"North Dakota",
    'US-OH': u"Ohio",
    'US-OK': u"Oklahoma",
    'US-OR': u"Oregon",
    'US-PA': u"Pennsylvania",
    'US-RI': u"Rhode Island",
    'US-SC': u"South Carolina",
    'US-SD': u"South Dakota",
    'US-TN': u"Tennessee",
    'US-TX': u"Texas",
    'US-UT': u"Utah",
    'US-VT': u"Vermont",
    'US-VA': u"Virginia",
    'US-WA': u"Washington",
    'US-WV': u"West Virginia",
    'US-WI': u"Wisconsin",
    'US-WY': u"Wyoming",
    'US-DC': u"District of Columbia",
    'US-AS': u"American Samoa",
    'US-GU': u"Guam",
    'US-MP': u"Northern Mariana Islands",
    'US-PR': u"Puerto Rico",
    'US-UM': u"United States Minor Outlying Islands",
    'US-VI': u"Virgin Islands, U.S.",
    
    'ZA':    u"South Africa",
    'ZA-EC': u"Eastern Cape",
    'ZA-FS': u"Free State",
    'ZA-GP': u"Gauteng",
    'ZA-ZN': u"KwaZulu-Natal",
    'ZA-LP': u"Limpopo",
    'ZA-MP': u"Mpumalanga",
    'ZA-NC': u"Northern Cape",
    'ZA-NW': u"North West",
    'ZA-WC': u"Western Cape",
}

def placenamesconvert(country, i):
    if i == 'other':
        return u'Other in %s' % (countrynames[country])
    ii = i.upper()
    if iso3166.has_key(ii):
        return iso3166[ii]
    return i

def removebrackets(t):
    t = re.sub(ur"(?im)\[\[[^\|\]]*?\|([^\|\]]*?)\]\]", ur"\1", t)
    t = re.sub(ur"(?im)\[\[([^\|\]]*?)\]\]", ur"\1", t)
    return t

def main():
    for country in ['ch']:# countrynames.keys():
        print 'Loading', country
        country_ = re.sub(' ', '', countrynames[country].lower())
        if not os.path.exists('%s/%s/' % (path, country_)):
            os.makedirs('%s/%s/' % (path, country_))
        adm0 = country
        
        #loading monuments from database
        conn.query("SELECT * from monuments_all where country='%s';" % (country))
        r=conn.use_result()
        row=r.fetch_row(maxrows=1, how=1)
        missingcoordinates = 0
        missingimages = 0
        monuments = {}
        while row:
            #print row[0]
            monuments[row[0]['id']] = {
                'id': unicode(row[0]['id'], codification),
                'lang': row[0]['lang'],
                'registrant_url': row[0]['registrant_url'],
                'monument_article': unicode(row[0]['monument_article'], codification),
                'name': removebrackets(unicode(row[0]['name'], codification)),
                'municipality': removebrackets(unicode(row[0]['municipality'], codification)),
                'adm0': row[0]['adm0'] and row[0]['adm0'].lower() or '', 
                'adm1': row[0]['adm1'] and row[0]['adm1'].lower() or '', 
                'adm2': row[0]['adm2'] and row[0]['adm2'].lower() or '', 
                'adm3': row[0]['adm3'] and row[0]['adm3'].lower() or '', 
                'adm4': row[0]['adm4'] and row[0]['adm4'].lower() or '', 
                'address': removebrackets(unicode(row[0]['address'], codification)), 
                'lat': row[0]['lat'] and row[0]['lat'] != '0' and row[0]['lat'] or 0,  
                'lon': row[0]['lon'] and row[0]['lon'] != '0' and row[0]['lon'] or 0, 
                'image': row[0]['image'] and unicode(row[0]['image'], codification) or '', 
            }
            if re.search(ur"(?im)(falta[_ ]imagen|\.svg|missing[\- ]monuments[\- ]image|Wiki[_ ]Loves[_ ]Monuments[_ ]Logo|insert[_ ]image[_ ]here)", monuments[row[0]['id']]['image']):
                monuments[row[0]['id']]['image'] = ''
            row=r.fetch_row(maxrows=1, how=1)
        
        #total, missingimages and missingcoordinates
        total = len(monuments.keys())
        for k, props in monuments.items():
            if not props['image']:
                missingimages += 1
            if not props['lat'] or not props['lon']:
                missingcoordinates += 1
        
        adm = 0
        if len(monuments.keys()) >= 1000:
            adm = 1
        
        if adm:
            admins = list(set([v['adm%s' % (adm)] for k, v in monuments.items()]))
        else:
            admins = [country]
        
        if '' in admins:
            admins.remove('')
            admins.append('other')
        admins.sort()
        
        for admin in admins:
            print 'Generating', country, admin
            
            imageyesurl = u'http://maps.google.com/mapfiles/kml/paddle/red-stars.png'
            imagenourl = u'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
            
            #admin kml
            output = u"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>Wiki Loves Monuments</name>
<description>A map with missing images by location</description>
<Style id="y">
  <IconStyle>
    <Icon>
      <href>%s</href>
    </Icon>
  </IconStyle>
</Style>
<Style id="n">
  <IconStyle>
    <Icon>
      <href>%s</href>
    </Icon>
  </IconStyle>
</Style>
""" % (imageyesurl, imagenourl)
            
            imagesize = '150px'
            errors = 0
            for id, props in monuments.items():
                if props['lat'] == 0 and props['lon'] == 0:
                    continue
                
                if adm: #if adm is > 0 then there are subdivisons, else all points in the same kml
                    if (props['adm%s' % (adm)] != admin) or (admin == 'other' and props['adm%s' % (adm)] != ''):
                        continue
                
                try:
                    uploadlink = u'http://commons.wikimedia.org/w/index.php?title=Special:UploadWizard&campaign=wlm-%s&id=%s&lat=%s&lon=%s' % (country, id, props['lat'], props['lon'])
                except:
                    errors += 1
                    continue
                
                if props['image']:
                    imagefilename = re.sub(' ', '_', props['image'])
                    m5 = md5.new(imagefilename.encode('utf-8')).hexdigest()
                    thumburl = u'http://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%s-%s' % (m5[0], m5[:2], imagefilename, imagesize, imagefilename)
                    commonspage = u'http://commons.wikimedia.org/wiki/File:%s' % (props['image'])
                else:
                    thumburl = u'http://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Image_upload-tango.svg/%s-Image_upload-tango.svg.png' % (imagesize)
                    commonspage = uploadlink

                output += u"""<Placemark>
<description>
<![CDATA[
<b>%s</b><br/>
(%s, ID: %s)<br/>
<a href="%s"><img src="%s" title="%s" /></a><br/>
<span style="font-size:150%%;border:2px solid black;background-color:pink;padding:3px;">
<a href="%s"><b>Upload!</b></a></span>
]]>
</description>
<styleUrl>#%s</styleUrl>
<Point>
<coordinates>%s,%s</coordinates>
</Point>
</Placemark>
""" % (props['monument_article'] and ('<a href="http://%s.wikipedia.org/wiki/%s">%s</a>' % (props['lang'], props['monument_article'], props['name'])) or props['name'], props['municipality'], id, commonspage, thumburl, props['image'] and '' or u"Upload!", uploadlink, props['image'] and 'y' or 'n', props['lon'], props['lat'])
            
            output += u"""
</Document>
</kml>"""
            print 'Errors', country, errors
            f = open('%s/%s/wlm-%s.kml' % (path, country_, admin), 'w')
            f.write(output.encode(codification))
            f.close()
        
        #country html
        countriessort = countrynames.keys()
        countriessort.sort()
        moremaps = u', '.join([u'<a href="../%s">%s</a>' % (re.sub(' ', '', countrynames[cc].lower()), countrynames[cc]) for cc in countriessort])
        output = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <title>Wiki Loves Monuments</title>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <link rel="stylesheet" type="text/css" href="../wlm.css" />
        <script language="javascript">
        function showHide(id){
            if (document.getElementById(id).style.display == 'none') {
                document.getElementById(id).style.display = 'block';
            }else{
                document.getElementById(id).style.display = 'none';
            }
        }
        </script>
        </head>
        
        <?php
        $places = array(%s );
        $place= "%s";
        if (isset($_GET['place']))
        {
            $temp = $_GET['place'];
            if (in_array($temp, $places))
                $place = $temp;
        }
        ?>
        
        <body style="background-image: url('../images/bg_stripes.png'); ">
        <center>
        <div id="page">
        <table width=99%% style="text-align: center;">
        <tr>
        <td>
        <a href="%s"><img src="%s" title="Wikimedia %s" /></a>
        </td>
        <td>
        <center>
        <big><big><big><b><a href="%s">Wiki <i>Loves</i> Monuments 2012, %s</a></b></big></big></big>
        <br/>
        There are <b>%d monuments</b> and <!--%d with coordinates (%.1f%%) and %d with images (%.1f%%)-->%d of them (%.1f%%) need images! Get your camera and take photos, thanks!<br/><b>Legend:</b> with image <img src="%s" width=20px title="with image" alt="with image"/>, without image <img src="%s" width=20px title="without image" alt="without image"/> - See <b><a href="../stats.php">detailed statistics</a></b> about the contest - <b>Share:</b> 
        <a href="http://twitter.com/home?status=Find+monuments+near+to+you+in+%s+http://toolserver.org/~emijrp/wlm/%s+Take+photographs+and+upload+them+to+%%23WikiLovesMonuments+:))" target="_blank"><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Twitter_Logo_Mini.svg/18px-Twitter_Logo_Mini.svg.png" title="Share on Twitter!" /></a>&nbsp;
        <a href="http://www.facebook.com/sharer/sharer.php?u=http://toolserver.org/~emijrp/wlm/%s" target="_blank"><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Facebook_Logo_Mini.svg/16px-Facebook_Logo_Mini.svg.png" title="Share on Facebook!" /></a>&nbsp;
        <a href="http://identi.ca/notice/new?status_textarea=Find+monuments+near+to+you+in+%s+http://toolserver.org/~emijrp/wlm/%s+Take+photographs+and+upload+them+to+%%23WikiLovesMonuments+:))" target="_blank"><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Identica_share_button.png/18px-Identica_share_button.png" title="Share on Identi.ca!" /></a>
        </center>
        </td>
        <td>
        <a href="%s"><img src="http://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/LUSITANA_WLM_2011_d.svg/80px-LUSITANA_WLM_2011_d.svg.png" title="Wiki Loves Monuments 2012" /></a>
        </td>
        </tr>
        <tr>
        <td colspan=3>
        <!-- choose a place --><div class="menu">%s</div>
        <table width=100%%>
        <tr>
        <td width=310px>
        <!-- twitter widget -->
        <script charset="utf-8" src="http://widgets.twimg.com/j/2/widget.js"></script>
        <script>
        new TWTR.Widget({
          version: 2,
          type: 'search',
          search: 'wikilovesmonuments OR "wiki loves monuments" OR #wlm',
          interval: 4000,
          title: 'Wiki Loves Monuments 2012',
          subject: '',
          width: 300,
          height: 375,
          theme: {
            shell: {
              background: '#8ec1da',
              color: '#ffffff'
            },
            tweets: {
              background: '#ffffff',
              color: '#444444',
              links: '#1985b5'
            }
          },
          features: {
            scrollbar: false,
            loop: true,
            live: true,
            behavior: 'default'
          }
        }).render().start();
        </script>
        </td>
        <td>
        <!-- map -->
        <iframe width="99%%" height="450" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://maps.google.com/maps?f=q&amp;source=s_q&amp;hl=es&amp;geocode=&amp;q=http:%%2F%%2Ftoolserver.org%%2F~emijrp%%2Fwlm%%2F%s%%2Fwlm-<?php echo $place; ?>.kml%%3Fusecache%%3D0&amp;output=embed"></iframe>
        </td>
        </tr>
        </table>
        
        <!-- more maps --><div class="menu"><b>More maps:</b> %s</div>
        <br/>
        <i>Last update: %s (UTC). Developed by <a href="http://toolserver.org/~emijrp/">emijrp</a> using <a href="http://wlm.wikimedia.org/api/api.php">erfgoed database</a>. Visits: <?php include ("../../visits.php"); ?></i>
        
        <br/>
        </td>
        </tr>
        </table>
        </div>
        </center>
        
        </body>
        </html>
        """ % (u', '.join([u'"%s"' % (i) for i in admins]), capitals.has_key(country) and capitals[country] or admins[0], wmurls.has_key(country) and wmurls[country] or '', wmlogourls.has_key(country) and wmlogourls[country] or wmlogourldefault, countrynames[country], wlmurls.has_key(country) and wlmurls[country] or '', countrynames[country], total, total-missingcoordinates, total and (total-missingcoordinates)/(total/100.0) or 0, total-missingimages, total and (total-missingimages)/(total/100.0) or 0, missingimages, total and (missingimages)/(total/100.0) or 0, imageyesurl, imagenourl, countrynames[country], country_, country_, countrynames[country], country_, wlmurls.has_key(country) and wlmurls[country] or '', len(admins) > 1 and u'<b>Choose a place:</b> %s' % (u', '.join([u'<a href="index.php?place=%s">%s</a>' % (i, placenamesconvert(country, i)) for i in admins])) or '', country_, moremaps, datetime.datetime.now())

        f = open('%s/%s/index.php' % (path, country_), 'w')
        f.write(output.encode('utf-8'))
        f.close()
    
if __name__ == "__main__":
    main()
