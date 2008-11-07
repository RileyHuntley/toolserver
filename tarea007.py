# -*- coding: utf-8 -*-

import wikipedia,re,urllib

wikisite=wikipedia.Site("es", "wikipedia")
newssite=wikipedia.Site("es", "wikinews")

for tema in ['Afganistán', 'Albania', 'Alemania', 'Andorra', 'Angola', 'Arabia Saudita', 'Argelia', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaiyán', 'Bahamas', 'Bahréin', 'Bangladesh', 'Belice', 'Benín', 'Birmania', 'Bolivia', 'Bosnia-Herzegovina', 'Brasil', 'Brunéi', 'Burkina Faso', 'Burundi', 'Bélgica', 'Camboya', 'Camerún', 'Canadá', 'Chad', 'Chile', 'China', 'Chipre', 'Colombia', 'Comoras', 'Corea del Norte', 'Corea del Sur', 'Costa Rica', 'Costa de Marfil', 'Croacia', 'Cuba', 'Deportes', 'Dinamarca', 'Dominica', 'Ecuador', 'Egipto', 'El Salvador', 'Emiratos Árabes Unidos', 'Eritrea', 'Escocia', 'Eslovaquia', 'Eslovenia', 'España', 'Estados Unidos', 'Europa', 'Estonia', 'Etiopía', 'Filipinas', 'Finlandia', 'Fiyi', 'Francia', 'Gales', 'Georgia', 'Ghana', 'Grecia', 'Guatemala', 'Guinea', 'Guinea Ecuatorial', 'Guinea-Bissau', 'Guyana', 'Haití', 'Honduras', 'Hungría', 'India', 'Indonesia', 'Inglaterra', 'Iraq', 'Irlanda', 'Irlanda del Norte', 'Irán', 'Islandia', 'Islas Marshall', 'Islas Salomón', 'Israel', 'Italia', 'Jamaica', 'Japón', 'Jordania', 'Judicial', 'Kenia', 'Kosovo', 'Kuwait', 'Letonia', 'Liberia', 'Libia', 'Liechtenstein', 'Lituania', 'Luxemburgo', 'Líbano', 'Macedonia', 'Madagascar', 'Malasia', 'Malta', 'Malí', 'Marruecos', 'Martinica', 'Mauricio', 'Mauritania', 'Micronesia', 'Montenegro', 'Mozambique', 'México', 'Namibia', 'Nauru', 'Nepal', 'Nicaragua', 'Nigeria', 'Noruega', 'Nueva Zelanda', 'Níger', 'Pakistán', 'Palau', 'Palestina', 'Panamá', 'Paraguay', 'Países Bajos', 'Perú', 'Polonia', 'Portugal', 'Puerto Rico', 'Qatar', 'Reino Unido', 'República Centroafricana', 'República Checa', 'República Democrática del Congo', 'República Dominicana', 'República del Congo', 'Ruanda', 'Rumania', 'Rusia', 'Samoa', 'San Marino', 'Senegal', 'Serbia', 'Sierra Leona', 'Singapur', 'Siria', 'Somalia', 'Sri Lanka', 'Sudáfrica', 'Sudán', 'Suecia', 'Suiza', 'Surinam', 'Tailandia', 'Taiwán', 'Tanzania', 'Tayikistán', 'Tecnología', 'Timor Oriental', 'Todas', 'Togo', 'Tonga', 'Turquía', 'Túnez', 'Ucrania', 'Uganda', 'Uruguay', 'Vanuatu', 'Vaticano', 'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabue']:
	url=u"/w/index.php?action=purge&title=Plantilla:ExportadorNoticias/%s" % urllib.quote(tema)
	data=newssite.getUrl(url)
	trozos=data.split("start content")
	trozos=trozos[1].split("end content")
	data=trozos[0]
	
	m=re.compile(ur"<li>(\d{1,2} ... 200\d): <a href=[^>]*>([^<]*?)</a></li>").finditer(data)
	
	noticias=u"<noinclude>{{ImportadorNoticias/Advertencia}}</noinclude>"
	for i in m:
		fecha=i.group(1)
		noticia=i.group(2)
		noticias+="\n* %s: [[n:%s|%s]]" % (fecha, noticia, noticia)
	
	wikipedia.output(u"----------------------------------------\n%s" % noticias)
	page=wikipedia.Page(wikisite, u"Plantilla:ImportadorNoticias/%s" % urllib.quote(tema))
	page.put(noticias, u"BOT - Actualizando plantilla")

