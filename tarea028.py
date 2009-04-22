#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
 
import wikipedia, re, os

for lang in ['ca', 'en', 'de', 'it', 'ja', 'gl', 'eu', 'pt', 'fr']:
	os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title, count(*) as iws from langlinks, page where ll_from not in (select ll_from from langlinks where ll_lang=\'es\') and page_id=ll_from and page_namespace=0 group by ll_from order by iws desc limit 1000" > /home/emijrp/public_html/nos_faltan/%swiki-nosfaltan.txt' % (lang, lang, lang))
 
