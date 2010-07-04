# -*- coding: utf-8 -*-

# Copyright (C) 2009 emijrp
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

import wikipedia,re,urllib,sys

langs=['pt', 'es', 'fr']

if len(sys.argv)>=2:
    langs=[sys.argv[1]]

impdic={
'default': 'NewsImporter',
'es': 'ImportadorNoticias',
}

expdic={
'default': 'NewsExporter',
'es': 'ExportadorNoticias',
}

advdic={
'default': 'Warning',
'es': 'Advertencia',
}

tempdic={
#no poner u'', sino no funciona. Luego con urllib.quote se soluciona
'es': 'Plantilla',
'fr': 'Modèle',
'pt': 'Predefinição',
}

temas={
'es': ['África', 'Afganistán', 'Albania', 'Alemania', 'Andorra', 
       'Angola', 'Antártida', 'Arabia Saudita', 'Argelia', 'Argentina', 
       'Armenia', 'Asia', 'Astronomía', 'Australia', 'Austria', 
       'Azerbaiyán', 'Ártico', 'Bahamas', 'Bahréin', 'Baloncesto', 'Bangladesh', 'Béisbol',
       'Belice', 'Benín', 'Birmania', 'Bolivia', 'Bosnia-Herzegovina', 
       'Botsuana', 'Brasil', 'Brunéi', 'Buenos Aires', 'Burkina Faso', 
       'Burundi', 'Bélgica', 'Camboya', 'Camerún', 'Canadá', 'Chad', 
       'Chile', 'China', 'Chipre', 'Ciencia y tecnología', 'Colombia', 
       'Comoras', 'Corea del Norte', 'Corea del Sur', 'Costa Rica', 
       'Costa de Marfil', 'Croacia', 'Cuba', 'Deportes', 'Dinamarca', 
       'Dominica', 'Ecología', 'Ecuador', 'Egipto', 'Egiptología', 
       'El Salvador', 'Emiratos Árabes Unidos', 'Eritrea', 'Escocia', 
       'Eslovaquia', 'Eslovenia', 'España', 'Estados Unidos', 'Europa', 
       'Estonia', 'Etiopía', 'Filipinas', 'Finlandia', 'Fiyi', 
       'Fórmula 1', 'Francia', 'Fútbol', 'Gabón', 'Gales', 'Gambia', 'Georgia', 
       'Ghana', 'Grecia', 'Guatemala', 'Guinea', 'Guinea Ecuatorial', 
       'Guinea-Bissau', 'Guyana', 'Haití', 'Honduras', 'Hungría', 
       'India', 'Indonesia', 'Informática', 'Inglaterra', 'Iraq', 
       'Irlanda', 'Irlanda del Norte', 'Irán', 'Islandia', 
       'Islas Marshall', 'Islas Salomón', 'Israel', 'Italia', 
       'Jamaica', 'Japón', 'Jordania', 'Judicial', 'Kenia', 
       'Kosovo', 'Kuwait', 'Lesoto', 'Letonia', 'Liberia', 
       'Libia', 'Liechtenstein', 'Linux', 'Lituania', 'Luxemburgo', 
       'Líbano', 'Macedonia', 'Madagascar', 'Malasia', 'Malaui', 
       'Malta', 'Malí', 'Marruecos', 'Martinica', 'Mauricio', 
       'Mauritania', 'México, D. F.', 'México y Centroamérica', 
       'Micronesia', 'Montenegro', 'Mozambique', 'México', 
       'México y Centroamérica', 'Namibia', 'Nauru', 'Nepal', 
       'Nicaragua', 'Nigeria', 'Norteamérica', 'Noruega', 
       'Nueva Zelanda', 'Níger', 'OTAN', 'Oceanía', 'Pakistán', 
       'Palau', 'Palestina', 'Panamá', 'Paraguay', 'Países Bajos', 
       'Perú', 'Polonia', 'Portugal', 
       'Programas y misiones espaciales', 'Provincia de Buenos Aires', 
       'Provincia de Córdoba (Argentina)‎', 'Provincia de Corrientes‎', 
       'Provincia de Entre Ríos‎', 'Provincia de Mendoza', 
       'Provincia de Misiones‎', 'Provincia de Santa Fe‎', 
       'Provincia del Neuquén‎', 'Puerto Rico', 'Qatar', 'Reino Unido', 
       'República Centroafricana', 'República Checa', 
       'República Democrática del Congo', 'República Dominicana', 
       'República del Congo', 'Ruanda', 'Rugby', 'Rumania', 'Rusia', 'Samoa', 
       'San Marino', 'Santo Tomé y Príncipe', 'Senegal', 'Serbia', 
       'Seychelles', 'Sierra Leona', 'Singapur', 'Siria', 
       'Software libre', 'Somalia', 'Sri Lanka', 'Suazilandia', 
       'Sudamérica', 'Sudáfrica', 'Sudán', 'Suecia', 'Suiza', 
       'Surinam', 'Tailandia', 'Taiwán', 'Tanzania', 'Tayikistán', 
       'Tecnología', 'Tenis', 'Timor Oriental', 'Todas', 'Togo', 'Tonga', 
       'Turkmenistán', 'Turquía', 'Túnez', 'Ucrania', 'Uganda', 'Uruguay', 'Vanuatu', 
       'Vaticano', 'Venezuela', 'Videojuegos', 'Vietnam', 'Yemen', 
       'Yibuti', 'Zambia', 'Zimbabue'],
'fr': ['All'],
'pt': ['All', 'África', 'Angola', 'Brasil', 'Cabo Verde', 'Guiné-Bissau', 'Moçambique', 'Portugal', 'São Tomé e Príncipe', 'Timor-Leste'],
}

for lang in langs:
    wikisite=wikipedia.Site(lang, 'wikipedia')
    newssite=wikipedia.Site(lang, 'wikinews')
    wikipedia.Page(newssite, u'User:BOTijo/Sandbox').put(u'1', u'BOT')
    for tema in temas[lang]:
        exportador=u''
        if expdic.has_key(lang):
            exportador=expdic[lang]
        else:
            exportador=expdic['default']
        importador=u''
        if impdic.has_key(lang):
            importador=impdic[lang]
        else:
            importador=impdic['default']
        advertencia=u''
        if advdic.has_key(lang):
            advertencia=advdic[lang]
        else:
            advertencia=advdic['default']
        
        url=u"/w/index.php?action=purge&title=%s:%s/%s" % (urllib.quote(tempdic[lang]), exportador, urllib.quote(tema))
        #url=u"/w/index.php?title=Template:%s/%s" % (exportador, urllib.quote(tema))
        data=newssite.getUrl(url)
        trozos=data.split("<!-- start content -->") #(bodytext|content|start content)
        trozos=trozos[1].split("<!-- end content -->") #(/bodytext|/content|end content)
        data=trozos[0]
        
        #wikipedia.output(data)
        m=re.compile(ur"<li>(\d{1,2}.*?20\d\d): <a href=[^>]*>([^<]*?)</a></li>").finditer(data)
        
        noticias=u"<noinclude>{{%s/%s}}</noinclude>" % (importador, advertencia)
        for i in m:
            fecha=i.group(1)
            noticia=i.group(2)
            noticias+="\n* %s: [[n:%s|%s]]" % (fecha, noticia, noticia)
        
        #wikipedia.output(u"----------------------------------------\n%s" % noticias)
        page=wikipedia.Page(wikisite, u'Template:%s/%s' % (importador, urllib.quote(tema)))
        
        if page.exists():
            if noticias!=page.get():
                page.put(noticias, 'BOT - Updating template from [[:n:|Wikinews]]')
        else:
            page.put(noticias, 'BOT - Updating template from [[:n:|Wikinews]]')

