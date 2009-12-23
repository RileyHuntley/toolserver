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

## @package updatefroms23
# Copy some stats from s23.org and paste in a page in Wikipedia for log purposes

import getopt
import sys
import wikipedia
import re
import urllib

def main():
	"""Copy some stats from s23.org and paste in a page in Wikipedia for log purposes
	"""
	try:
		opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
	except getopt.error, msg:
		print msg
		print "for help use --help"
		sys.exit(2)
	for o, a in opts:
		if o in ("-h", "--help"):
		    print main.__doc__
		    sys.exit(0)

	## @var url
	# URL to statistics page
	url='http://s23.org/wikistats/wikipedias_wiki.php'
	f=urllib.urlopen(url, 'r')
	text=f.read()
	text=re.sub(ur'(?im)[\n\r]*</?pre>[\n\r]*', ur'', text) #cleaning...
	text=u'Lista de Wikipedias extraida de %s\n\n%s' % (url, text)
	## @var p
	# Page where to save
	p=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'User:Emijrp/Lista de Wikipedias')
	p.put(text, u'BOT - Updating from %s' % url)
	f.close()

if __name__ == "__main__":
    main()

