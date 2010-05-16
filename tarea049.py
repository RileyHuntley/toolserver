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

""" Bot searches for titles with endashes (–) and creates a redirect from hyphens (-) """

import MySQLdb
import re
import sets

import wikipedia

projects = [
["en", "wikipedia", "sql-s1", "enwiki_p", u" {{R from modification}}", u"Creating redirect to"],
["es", "wikipedia", "sql-s3", "eswiki_p", u"", u"Creando redirección hacia"],
]

def main():
    """ Bot searches for titles with endashes and creates a redirect from hyphens """

    for lang, family, host, db, footer, summary in projects:
        wiki = wikipedia.Site(lang, family)
        conn = MySQLdb.connect(host=host, db=db, read_default_file='~/.my.cnf', use_unicode=True)
        cursor = conn.cursor()
        cursor.execute("SELECT page_title from page where page_namespace=0 and page_title regexp \".*[–-].*\";")
        row = cursor.fetchone()
        endashes = sets.Set()
        hyphens = sets.Set()
        while row:
            pagetitle = re.sub(ur"_", ur" ", unicode(row[0], "utf-8"))
            if re.search(ur"–", pagetitle) and not re.search(ur"[-\(\)]", pagetitle): #descartamos las que tienen paréntesis, (cación) (desambiguación)...
                endashes.add(pagetitle)
            if not re.search(ur"–", pagetitle) and re.search(ur"-", pagetitle):
                hyphens.add(pagetitle)
            row = cursor.fetchone()    
        cursor.close()
        conn.close()

        print len(endashes), "endashes"

        for pagetitle in endashes:
            pagetitle_ = re.sub(ur"–", ur"-", pagetitle)
            #if re.sub(ur"[\–\-]", ur" ", pagetitle)!=re.sub(ur"[\–\-]", ur" ", pagetitle_): #lo pongo o no? #fix
            #    footer=""
            if pagetitle_ not in hyphens:
                #creamos
                redirect = wikipedia.Page(wiki, pagetitle_)
                if not redirect.exists():
                    target = wikipedia.Page(wiki, pagetitle)
                    if target.exists():
                        if target.isRedirectPage():
                            target = target.getRedirectTarget()
                            if target.exists() and not target.isRedirectPage():
                                redirect.put(ur"#REDIRECT [[%s]]%s" % (target.title(), footer), u"BOT - %s [[%s]]" % (summary, target.title()))
                                print ur"#REDIRECT [[%s]]%s" % (target.title(), footer)
                            else:
                                pass #demasiadas redirecciones anidadas
                        else:
                            redirect.put(ur"#REDIRECT [[%s]]%s" % (target.title(), footer), u"BOT - %s [[%s]]" % (summary, target.title()))
                            print ur"#REDIRECT [[%s]]%s" % (target.title(), footer)
                
if __name__ == "__main__":
    main()
