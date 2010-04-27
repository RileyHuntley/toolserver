#!/usr/bin/env python2.5
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

import wikipedia, re, os

for lang in ['ca', 'en', 'de', 'it', 'ja', 'gl', 'eu', 'pt', 'fr']:
    os.system('mysql -h %swiki-p.db.toolserver.org -e "use %swiki_p;select page_title, count(*) as iws from langlinks, page where ll_from not in (select ll_from from langlinks where ll_lang=\'es\') and page_id=ll_from and page_namespace=0 group by ll_from order by iws desc limit 1000" > /home/emijrp/public_html/nos_faltan/%swiki-nosfaltan.txt' % (lang, lang, lang))
 
