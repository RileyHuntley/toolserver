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

import os

langs=[u'aa', u'ab', u'af', u'ak', u'als', u'am', u'an', u'ang', u'ar', u'arc', u'arz', u'as', u'ast', u'av', u'ay', u'az', u'ba', u'bar', u'bat-smg', u'bcl', u'be', u'be-x-old', u'bg', u'bh', u'bi', u'bm', u'bn', u'bo', u'bpy', u'br', u'bs', u'bug', u'bxr', u'ca', u'cbk-zam', u'cdo', u'ce', u'ceb', u'ch', u'cho', u'chr', u'chy', u'closed-zh-tw', u'co', u'cr', u'crh', u'cs', u'csb', u'cu', u'cv', u'cy', u'cz', u'da', u'de', u'diq', u'dk', u'dsb', u'dv', u'dz', u'ee', u'el', u'eml', u'en', u'eo', u'epo', u'es', u'et', u'eu', u'ext', u'fa', u'ff', u'fi', u'fiu-vro', u'fj', u'fo', u'fr', u'frp', u'fur', u'fy', u'ga', u'gan', u'gd', u'gl', u'glk', u'gn', u'got', u'gu', u'gv', u'ha', u'hak', u'haw', u'he', u'hi', u'hif', u'ho', u'hr', u'hsb', u'ht', u'hu', u'hy', u'hz', u'ia', u'id', u'ie', u'ig', u'ii', u'ik', u'ilo', u'io', u'is', u'it', u'iu', u'ja', u'jbo', u'jp', u'jv', u'ka', u'kaa', u'kab', u'kg', u'ki', u'kj', u'kk', u'kl', u'km', u'kn', u'ko', u'kr', u'ks', u'ksh', u'ku', u'kv', u'kw', u'ky', u'la', u'lad', u'lb', u'lbe', u'lg', u'li', u'lij', u'lmo', u'ln', u'lo', u'lt', u'lv', u'map-bms', u'mdf', u'mg', u'mh', u'mi', u'minnan', u'mk', u'ml', u'mn', u'mo', u'mr', u'ms', u'mt', u'mus', u'my', u'myv', u'mzn', u'na', u'nah', u'nan', u'nap', u'nb', u'nds', u'nds-nl', u'ne', u'new', u'ng', u'nl', u'nn', u'no', u'nomcom', u'nov', u'nrm', u'nv', u'ny', u'oc', u'om', u'or', u'os', u'pa', u'pag', u'pam', u'pap', u'pdc', u'pi', u'pih', u'pl', u'pms', u'ps', u'pt', u'qu', u'rm', u'rmy', u'rn', u'ro', u'roa-rup', u'roa-tara', u'ru', u'rw', u'sa', u'sah', u'sc', u'scn', u'sco', u'sd', u'se', u'sg', u'sh', u'si', u'simple', u'sk', u'sl', u'sm', u'sn', u'so', u'sq', u'sr', u'srn', u'ss', u'st', u'stq', u'su', u'sv', u'sw', u'szl', u'ta', u'te', u'tet', u'tg', u'th', u'ti', u'tk', u'tl', u'tn', u'to', u'tokipona', u'tp', u'tpi', u'tr', u'ts', u'tt', u'tum', u'tw', u'ty', u'udm', u'ug', u'uk', u'ur', u'uz', u've', u'vec', u'vi', u'vls', u'vo', u'wa', u'war', u'wo', u'wuu', u'xal', u'xh', u'yi', u'yo', u'za', u'zea', u'zh', u'zh-cfr', u'zh-classical', u'zh-min-nan', u'zh-yue', u'zu', ]

for lang in langs:
	os.system('python stubmetahistory-fetch.py %s' % lang)

