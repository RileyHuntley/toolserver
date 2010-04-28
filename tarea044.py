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

""" Update BOTijo userpages in all languages """

import re
import sys
import wikipedia
import time, os
import tarea000
import MySQLdb

def main():
    family='wikipedia'
    for lang in tarea000.getLangsByFamily(family):
        try:
            if lang=='en-simple':
                lang='simple'
            site=wikipedia.Site(lang, family)
            tarea000.insertBOTijoInfo(site)
        except:
            print "Hubo un error en: ", lang        

if __name__ == "__main__":
    main()
    
