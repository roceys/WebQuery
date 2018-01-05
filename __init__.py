# -*- coding: utf-8 -*-
# Copyright: kuangkuang <upday7@163.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Project : WebQuery
Created: 12/24/2017
"""
import json
import random
import re
from functools import partial
from uuid import uuid4

import aqt.models
from PyQt5.QtCore import QUrl, QRect, QSize, Qt, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtGui import QImage
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWidgets import *
from anki.hooks import addHook
# noinspection PyArgumentList
from anki.lang import _
from aqt import mw, os, QWebEngineSettings
from aqt.utils import openHelp
from aqt.utils import restoreGeom
from aqt.utils import tooltip

# region Bytes
items_bytes = bytearray(
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f'
    b'\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00\tpHYs\x00\x00\x0b\x13'
    b'\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00MIDAT8\x8d\xd5\x91\xc1\t\xc00\x0c\xc4TO'
    b'\x96\rL6\xf2F\x877\xc8d\xa6\xafB\x9f!P\xd2\xe8\x7fpB\xb0\x9b\x0b\xa0\xf7\x1e\x92\xc2\xdd'
    b'\x9b\x99\xb5\xd9\xb1\xa4\xb0\xaf\x9eM\xb3\xa4PU#3\x07\xc0\xa1\n\x0f\x87Vx\x17\x80?T\xd8'
    b'\xcf\r\xa5\x9e(\r0\x19&\xcc\x00\x00\x00\x00IEND\xaeB`\x82')

gear_bytes = bytearray(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80'
                       b'\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00\x15\x90IDATx\xda\xed'
                       b']\x0b\xb4UU\xd5^\xe7\xdcs\xce}\x1d\xce\xe5>\xb8p\xdf\x17'
                       b'\x01/\x0f\x81\xab\xa2@!\x9aO|D\xa2A*)\xbe\xfe\xfel\x98\x8d\x1c\x95'
                       b'e\xd9hXV2\xf8\xfbIt\xa8\xa5e\x1a\x91f\xf2\xf2\xf5\xf7k\xfd\x7fc'
                       b'\xf4\xf0\x81f\xc5C\x01\x1f\x84\x9a\x86\xa6\x88 \x08\x97'
                       b'\xe6\xe4\xac}Yw\xb3\xcf^s\xef5\xd7\xde;<g\x8c9\x80{9s\xcf'
                       b'5\xbf\xb9\xd7c\xceo\xad%\xc4\xc1\xf9\x19\x07r?\xc8v\x90\xbd'
                       b'\x86\xf2.\xc8J\x901\xa2\xfc9\xf0s\xe2\x89\xc7\xa5@\xd2\x8a\xa4'
                       b'b\xd67\x1e\xe4\x1d\x06\xe0\xdd\xf26\x06A\x02\xdbkU\x9f\xeea'
                       b'\x15nI\x80\xbe\x07\x1d\xd0R\xa9\xd4\x01b\x12\x04\xf0'
                       b'\xfd\x07\x13\xd8^k\xfatQ\x96\x01\xc9*\x92\t\x1bm\x8c\xfajAvY\x02'
                       b"\x7f\x9f\xb4\xb4\x0c\xcb'\xa8\xbdV\xf4Q\x1e\x86\x0f\xc8)\x9254"
                       b'\x9eK\xdf\x0c\x07\xact:\xdd/\x1c\xe0;\xbar\xb9\xdc\xc9\tj/\xbb>\xca'
                       b'\xc3*A\xaa\x14\xa944\x9eM_*%\x16\xa8\xc0;b\x02\xbe[WEE\xc5w\x92\xd2'
                       b'^n}\x94\x87\xe1\x03\xaa\x15\xa924\x9eU\x1f\x80\xf3\x8cM\xf0'
                       b'\xa5\xbe\xdf\x1f\x8c\xfe\xd3=\x0cg\x935 \xb5\x8a\xe0\xbf\xd3I\xd1'
                       b'\xd7\xdc<\xa4\x13\x02`\xef~1\x03\x1f\xbf_B\xdfn\x90\xc2\xc1'
                       b'\xe4?\xca\xc3\xf0\x01yEj\r\x8dg\xd7W]]u\x81\n\x98\x07\xa8o\x82'
                       b'hg\xc5\r\r\xf5\x95\xf0\xfdm\x03\xc1?@\xdf\x19\x07\x8b\xff\xa8'
                       b'\x0f+(\x9274>oC\x1fL\xce~\x9c\xc9\x14\xc1\x82\xb9\x80W\x00\xfc\x92'
                       b'\xaa/\x9b\xcd\xfe\nu\xf9\xe8\xfb^\xdc\xed\xe5\xd0G\x19cj\x94'
                       b'\x07\xd6\xc9?M\x8cw\xf4\xd4q\xeb\xcbf3/ `>3\xfe\xcb\xa8\xfa\xaa'
                       b'\xaa\xaa\xbe\x9a\xc9d\xf6\xfa\xe8{&\xee\xf6\x9a\xeas0\xd6M0'
                       b'j]\x11\x17\xda\xf8\xb1c{\x9a\x87\x0f\xef\xea:\xee\xb8i\x83\xb9'
                       b'\x9d\x01\xe3\xff\x04\r\xf8(\xa3\xa8\xfa\xea\xeb\x07\x1fC'
                       b'\xd0\xd7l\x01,\x04\xa4\t\xa4\xdar0\xa5d\xa2(\xed\xb7\xb4\xa8'
                       b'v\x8d5\xa1\x1e\x06of7t\xa9\xf7\xc3\x1b\xb5\xbb\xf8Ve^\x83\x7f?\xdc'
                       b'\xd1\xd1\x96\xe5z\x13`\xfc\xbf\\\x03\xd6&\xe9\\\x92\xbei\xd3\xa6'
                       b'\x0c\x06}oh&\x8as\x18\xc1\xc7\xb9\xc9\xa7A^R&\x9aKA\xda-\x81'
                       b'\x9f\xf1\x0c\x00%\xa9P\xa5\x04@\xe8\t\x06\x80\xdd\x03\xf2\xb2\x04~'
                       b'\xafG\xb7\xfaa\x8en\x10\xf4\xdd\xad\x01\xebG!\xc0\xbaW\xa3\xf3'
                       b"V&\xf0\xa7\x83\xfc\xa9T\x02\xaa\xae\xae0\x9d\x19|'S\xe8\x19"
                       b'\x00\x19\x99Ir\x02\xa0\xc6"\xf8\x8e\xfc\x14\xa45,\xf8#F\x0c'
                       b'\xcf\xc0\xaf_\xd7\x8057\x04X\x97itn0\x04\xbf\x03\xe4\xe7'
                       b'~\xd9\xc7\xe2D4\xb3\xb7\xb9\xb9\xa9\x97\t\xfcJ%SX1`\x0e \x7f\x90'
                       b'U\x02\xa0*\x02\xf0\x1d\xd9\x06r\x15He\x887u"a]?,\x04X=\x04\xbd]!'
                       b'\xc0\xc7\xf1\xfd\xeb\xc2\xa7T\xad\x82\x8f\x02\xc3\xe8\xe6\xa6'
                       b'\xa6\xc6\x89\x86s&\x07\xd3\xfe\x00\xf0\x9a\x148\x01\x10'
                       b':\x9d\x18\x02|U\x9e\x039- XWjt\xfe5\xe4\x9b\x8a\xed\xdf\xac\xd1}Q@}'
                       b'g\x83\xbc\xa8\xab;\xa8\xe0+\xfe\xc3y\xcc\x08\x83\xa4Q\xb5\x12\x00'
                       b'\x19\xaf\xffT\xa1\x8c\x0fq\x80\xaf\n\x929F\x12\x9d\xfb\xa0F\xd7'
                       b'B\x83n\xfaN\rX\x8b\x89\xfa\x0e\x03y\x94Rt*\x01\xbe:\x99\x1d\x11\x10'
                       b'|g\x1e\xe7\x04\xc0\x81\xf8*\x01\x90I\x00\xf8\x8e3vVV\xe6'
                       b'\xfe\xab\xa7gT\x9b\x8fs;\t\xba\xce0\x98\xa0\xcd\xd3\x81\xd5\xde'
                       b'\xde6\xcaG_\x03\xc8"9\xab7\x05?P\x10(I\xa3\xbc\x12\x00\xde=\xbb'
                       b'\x12\x00I\x01\xbf\xdf\x190\xfe\xbdZSSs)\xe4\x0f\xea\xa4s'
                       b'q\xec\xfa\xa8\xec%t\xba\xf6\xe5\xed\r\x96R\x9d\x14\xb0r\xb9\xec'
                       b'C\xb5\xb55\xb3\x95\xa5\xad\xb3\xac\xdb\x12\xb4\xbdD\xff'
                       b'\xf9\x06\x81\xd2\xde\x82\x12\x00U\xbe\x89\x9f\xb0\xd9$\x9b'
                       b'\xe0\xbb\xf4=\t\xbf\xff!\xc8\xf3\x01\xf4\xfd\x8ea\x1d\xbd>\x00X'
                       b'\xb82X\x02\xb2\x8e\xa1\xbd\xba\xefz\x06\x81\xab\xbdN\x00\xd4X\xa9'
                       b'\x12\x06\x04\x1f\x99:\x1f\x93]\xf2\x06fg\x94r\xee7\x19\x92('
                       b'\xb7X\xb4O\xe9\xe9\xb2\xeb\x06\r\xca\x9f\t\xbd\xdd\\\xf8\xf9\xfbD'
                       b'\x1d\x03\x82\xc0#\xd8\x0b\xd6\nE!\xc1w>\xb8\xdc\xfb\x8a(2n\xad9\x17'
                       b"\x1cz*C\x12e\x8ee\xf0\xdf\x86L\xe6\x97'M:\xbcI\xb1\xef,\x90@"
                       b"AP\xa2\xa7\xcb'\x11|\xf5\xd3\x0e\xb2\xd8\x8es3/K\xa7\x9af\xd0\xea@"
                       b'\xdfV\x0b\xe0\xf7\xc1$\xf7\x8e\xce\xce\xf6\x11%\xec#\x07\x01.\x11'
                       b'e\x9e\x80\xadP\xe4\x9b\xdbg\x02\xbf\xbf\xdb\x827\xf5'
                       b'\x14\xe8\x02\xff\xc2\xe8\xdc]\xa0\xf3l\xae*\\uu\xf5%`W\x1f\x97}\xe0'
                       b'\xc3?@\xc1i:\xc1>m\x108/\x0f&\x8b\x80\xb0:\xd6*\xf8\xa8T\x16'
                       b'v\xd8\xc0w\xba\xad\xa9S\x8fn\x00G_\t:\xdf4p\xeev\xb0o\xf9\xe0'
                       b"\xc1u\xc7r\x97`!'\x7f\n\xcc\xf6\xb1\xed\xdb\r\xec\xdb\\SS}\xb1R"
                       b'\x11\xa5\xd8W2\x08\x0e\\\x8d\xe4\x96[\x05\x1fK\xbaJU\x8f\r'
                       b'|\xd5\x19\x95\x95\x95C\xe0\xd77\x81\xec!:\xb6\x0f\xe4\x01\xe0\xeb'
                       b'\x9d\xd3\xd33r\x98\xed\xfa{mm\xed \xf8\xf592\x01\xd5G\xb4\xf1=\xf0'
                       b'\xd3\xb7\x0c\xec; \x08J\x0c\x9b\xbb\x80\xd1Te\x8b\x19T\xe8\xea'
                       b'\xea\x1cN\xec\x06C\x81\xefrF/\xc8o}\x9c\x8a\xbb\x7f\x16\x80'
                       b't\xc7H\xbe\x18.\xd9A\xdb|\xec\xbc\x0f\xfc5\x82\xc1\xbe\xb3\x88'
                       b'\x13\xe6\x82\r\xf0q6Y\x87]\x17\x8c5/\x11\xc6\xc0\x19Ld\x89\x94|\xdb'
                       b"^r\x01\x7f\x1dH}\x82\x987\x8d \xdfu\x05\xc2\xd3 '0\xdaw&\x01"
                       b'\xfc\xf56\xc0\xafU\x1b\x00K\x96\xcf\x12\xc6@L\x84\xe4\x18\x992'
                       b'\x15\xb2G\x98"\x8a\xbb\x7f\x92J\xbb\xaa\x019\x02\xeb'
                       b'\x18\x18\xbc\x8c\xf6a\x05\xf1\x05\xc2j\xe9bN\xf0=9\x812\xdd'
                       b'\xf9\x14a\xdc\xbb\xd22\xad\xe9\x83\xa4\xef\x1a\x02\xf8\x8f'
                       b"\x83\xa4\x83b\xec\x07\xbe\x1f'p\x9a\xa0\xed\xa6\x1dZ\x06\xdfX_"
                       b'\x17\xaen\x08y\x88\xc9\x01_ncN\xe0\xcf\x08Ap[\x19|3}\x00\xf2'
                       b'/\x08\xe0\xff8 \xf8,\x9c\xc0v5\x95[b\x9d\xda\x07\xeb\xe7'
                       b'c\xcb\xe0\x87\xd3\x07K\xdb\x13\x08\xe0o\x15.\xc6\x93\x06|VN'
                       b'\xe0\xd7\xf4\x19\xaa\xecc6\xa8\xe0\x07\xbb\xbea\xc3\x86'
                       b'\xe6\x00\xf0\xd5\x84\xa4\xdb\x95\x01\xc0g\xe7\x04Vy\x95'
                       b'g\xdd\x13\x16\xa8p}\xaa\x0c~0}UU\x95_$\x80\xbf\xd6k\xb5U\xc2'
                       b'>k\x9c\xc0Y\xfa\x0cU\xe6\x15\x08\x82B\x19|\x9a\xbe\xf6\xf6\xd6'
                       b"C\xc0go\x11\x92n'\x11\xed\xb3\xca\t\xc4\xff\xfb\x08!I\xf1\xed2\xf84"
                       b"}X%$\x80\xbf4@\x1e\xc7:'p\x1c\x18\xb9[3a\xd9)\x82\x13\x1a?p\xe0c"
                       b'!k\x7f\xe5\xb1$\xf8\xef\x81\x1cB\xcc\xe0\xda\xe7\x04'
                       b'\xe2\xf7\xa1\x12u\x0ba\xccZV\x06\xbf\xb4\xbec\x8e\x99Z\x8f\x93'
                       b"fB\xad\xe5Z\xa2}\xf69\x81\xce\xc3p\xe3'\x18\xfe\x06\xc1\xf8"
                       b'\x93\xa3v.V1\x81\x1f0\x0b*\x8d\x0b\xa0\xa4\xfb\x00\xd8\xf8\x1c'
                       b'\xd8\xb7EV-Q\xb6\xc8\xf4\xf52Yg8I\xb86hF\x11L0O\xfaO"!\xb4'
                       b'\x86\xe8?\xbb\x9c@\xb73\xa0\x9e\xffyB\xa1\xe8\xcf"\xc0FM'
                       b'\x03\xe7V\xc0:\xfa4x\xa3\x96\x82S\xdf\x0bA\xe6\xd8\x01r\xb7'
                       b'\x0c\xd8\xb4m\xf0\x91\xbd\x84\x0ch\x82}s\x02\xbc<\x05\xdb\x87G'
                       b'\x0cp\xc6\x94)G\xd5\x83\xf1\x14F\xec(\x8b\xe0\xe3\xf2\xe6\\\xb0'
                       b"c-#\x8dk5\xf2\r\xb0}\xb6\x86\x11\x18\xfb\x8f'\xd8\xf7\xbb\x80/O>"
                       b'2\xf0\x15g,!8\xf4\x08K\xe0O\x02Ye\x8b\xc0\t\xbd\xc9Sxv\x80'
                       b'\x8d9\x04\x0cQ3\x08\xf6}?\x8aa\xc9\x04||\xfb6j\x1a\xf1\x8e:\xbe'
                       b'2\x19\x9f\x91c\xf7\x1e\x9b\xd4m){`\x99v=\xe7\xf9\x06\xf8o\x18>\x07'
                       b'\x0b\xfd\xd9\xc6\xeb\xdc\x15\xbf$\x81\x8f\x9f\xd3\tN\xbd'
                       b'\x8e\xd9x\xa4\x90\xfd\x9f\xb0\xcc\xdb\xf7\xd0\x87{\xfd\x9a'
                       b'\x98\xfd7\x9f`\xd7)I\x05\x1f?+5\xc6c\xe1\x82\x93\xc9\x83'
                       b'\xdb\xb3\x9f\x8d\x01|\xf5\x8d\xecd\xf4\xdf\x10]\x81M'
                       b'\xc8\xc3\xae\x92\x08~\x0b\xc1\xb1\xf3\x99\xc1\xff[\x8c\xe0'
                       b'\xab\xcb\xb2N\xc6\xa5\xed\r:\xfb`.\xd2\x1e5\xf8y\xf7\xc3&N<\x0c\xc7'
                       b"{\xa4>}J.\x97t\x8eE\x96o'c\xb7\x1f\xf4\xcd\xc7\xb7\x15\t\x9c\xb3"
                       b'E\xf1Hy\xec\x89\xb2\xb2\x98\xd2 \x7f6\x1b\xbe\xb7\x10tl\x08\x18LkK'
                       b'\r\x07!\xda;\x92\x12\x9c\x90\xcf\xf8\x1f\xa0\xe7]\r,\xe0\x0f+'
                       b'\x1bg\xad\x80\xdf\xcf\tlkk\xe9\x81\xc9\xca\xa5`\x04\x12\x10^'
                       b'\n\xf8f\xdd\xcf8\xe1\xa3\x8e\xf9\x18t\x8b\xe5\xea E\xed\xe9\xb0'
                       b'|\x8d\xcb2\xc8n\xde\x8b;x\x88=\xc9#\xc2u\x10\xa5A{\x1f\t\xd83'
                       b'\xbd&W_\x97\x80ts\x81\x9f\x82\x9d&\xad\x00\xf8\xb9\xe0\x88['
                       b'q\xf3\xa2I\xb7\n\xeb\xe89L\xdd\xd6uD\xf0\x1f\x13E"\xa9\xd10\x07\x07'
                       b'Eb\xf0<Il\xe77\x98&h\xe7\x1b\x0eK\xb8\xf9\xf6V\xd9\xdb5\xf9a'
                       b'\xec\xfe\x19\xa6\x18O\x06\xa5\xd7C\xc3W\x81\xec\xc1\x932\x9dS3'
                       b'\r\xc6\xd4wG\x8f>t(\xd3:\x9f\xb2\xd4[(\xbbw\xae9\x0e\x0e\x137'
                       b'\n\xday\x04\xbd\x0c=]A\x16|86\xce\xe2\xe6\x95\xa7\xe4\xfc\x0bW\x105'
                       b'^\x9c@\x1c\xff\x1e\x90yq\xf5h\xf4~1\xdb\x0b\x97]\xce\x94\xe1\xa3$y'
                       b'\xae\xb6T\xd8\xc1\xb7\xe5\x1aB{\x1f\xc7s\x06\x19\xda'
                       b'\xbb\xc2\xc6\x04\x171N\xa7S\x0f@\xday\xbcc\xd38\xa1\xdc\xb1'
                       b'\xa3^\x8e\xb0\x1f|a2\x9b\xde\x03\xbc\xc0\x13\x19f\xab\xe7\x12\xdf'
                       b"|\x9bU=\x0c\x82E\xba\t\x1a\x9c\x16r!C{'\xe39\x01\xcc\xe0\xab7"
                       b'\xa8\xbc\r\x18\x8f\xc5\x07\xdd\xef\x05~1\x00\xd2F\x0f\x02\x83\xff\t'
                       b'\xce\x98\xc7Q\xd8!\xe4\xf6\x1fc\xee\xf6K}r^s\x02\xf7a\x0fX\xda5'
                       b'M\x17\x83\xef\xe6\x80\xbeW\xb9\xc0WoP)\x8aX.\x9c\xf4\xa3'
                       b"\xf3C\x86\xcb\x16V\x83\x9e\x1b\xa1\xb4y\x9e\xe6\x80'\xf2\x07\xabz"
                       b'\x84\xd9~o\x04\xe0;\x9f#\x85\xb21\xd4\xabg\xca\xe7kgrU\t\x0b\x85'
                       b'A\xa7C\xfay><\xe7\xf7\x82p\xe0\x94\xd0\\~\xa1\xdc\xa1\x84[\xd9\x06v'
                       b'\r!\xc0\x7f\x11\xe4v\x90\xf30\x19d\xa3d*K\xba~\xdd\xe0'
                       b'\xe2\x18\xc8\x1c?\xd7\x8c\xd1K,%\xdd\xea@f\xca\xc2\xd0j\n'
                       b'F\xd8\x93\xfb\xdc\xa1t\xe0\x15k\x1a\x85\xce\x9a\xf3R7-\xc9\x16'
                       b'\x99\x83P\xcf\x9f\x14\x03\x93g\xb2fN\x82=ke\x04L#<f\xf7\x93 '
                       b'w8\x99\xd1\xfd\x98\x8a\xfey\x9c\xcf\x05Z\x03\x03@xo\xf1\xc2'
                       b'\xb1\xe2\nQ<\xf00\n2G\xbf>d\xf2\x102|\xa9\x88\xc1\x17\x98\t\x05'
                       b'\x9b\x9e\xd7\xf4L\xc7G\xdc3\xa1\x1f\xf0\x88\xdb\xcf\x80'
                       b'\x1dK\x01\xf8\xb7\xdc\x01\xe0\x81\xef\xfe\x00(\xf1\xc6g'
                       b'\xa2v\xae\xaa\x0fi\\\x9a\t\xd0\xf7\xe2\xb2\x0f\xc6\xe5[4\xc1y'
                       b'm\x0c=S\xbf>$\xb0\xa8\x01P\x02_\xed\x18\x12\x1b\xf8(E'
                       b'\x0e\x9f\xef\xecwv\\\xf6\xc1,\xfd"Mp\xde\x17\xb3\xff\n\x84'
                       b'\x0b\xb4\xc2\x07@\x14l[I\xe0\xf4\xb3o|\\\xf6\x01;h\x9a&8\xd7\xc6'
                       b'\xec\xbfB\x89\x0b\xb4\xcc\x03 *\xaa\xb5d\xef\xfa\xd9W\x1f\x97}'
                       b'\x1d\x1d\xed\xdd\x9a\xe0|=f\xff\xe5)\xf8\x06\x0e\x80\x88y\xf6\xbb'
                       b'4\xf6e\xe3\xb2O\x1e\xc8\xe4g\xdb\xce\x04\xf8\x8f7\x00b\xd8d'
                       b'\xa1\x0b\x80\\\x8c\xf6\xe5\x82\x06@\x0c\xfe\xe3\x0b\x80\x98'
                       b'v\xd8\xe8\x86\x80\x86\x18\xedk\xd4\xd8\xf6z\x02\xfc\xc7\x13\x001n'
                       b'\xaf\xd2\xed3\x18\x1f\xa3}\xbd\x1a\xdb\xd6$\xc0\x7f\xe6'
                       b'\x01\x10\xf3\xde\xbae\x1a\xfbf\xc7h\xdf9"\x06\x02g@}f\x010dH'
                       b'c\xce\x8b\x13\x18\xe1\xc6\xca\xeb4U\xc7\x851:WG\xe0\xbc6f\xf0s\xc6'
                       b'\x01\x00\xeb\xc8\xadP\x8cy\x10\x08\x88W566L6! \x86t\xc6I\x9a'
                       b'\x92\xf3\xfa\x80g\xefr\xd9\x87i\xd7\x8d\x9a\n\xdc\t\x11\x83\x8f\x7f'
                       b'\xe2\xae\xab/\x80<$\xfcO0\xd5\x07\x80s\x85\xfa\xfe\x82\xc7\xbe'
                       b'\xa4\xc7+\xf0\xbb\xbb@.\x14\xc5\xbb\xefl\xe7\xbaq\x17\xd1\x0e\xbf'
                       b"\xfa;\x128c\xe8\x99\xa6hz\xa6w'L\x18\xd7d\x13||\x19\xc1\x07c"
                       b'0\xf7/\x87\x9b7D\xf0Rq\xe9\xfa\xb1\x93G\xd6p\x02\x91\x9e'
                       b'\x8d\x87;\xcf\xb2\x98\x94\xb9[\xf8\x9f\x92}o\x0c\xfb'
                       b'\xfd\xef\x11\xfe4\xb8{l\x80\x0f\x87G\x8d\x83\x13\xc7?\x03)\xf2'
                       b'%\xf0\x9c\x97\x85\x01a\xc7\t\x80\xed\xa5\xc8\x03!8\x81H\xcc\xc0'
                       b'\x13+\xbf\x03r\x02\x96C\x99\xc6\xc0\x93\x85?A\xb2O\xb2w\xa3'
                       b'\x02\xffh\xa1\xa1\x85\r\x1a4h&\x07\xf8p\x93y\x03\x00>\x0f\nO?\x02'
                       b"\x1e\xdfFNZ\x98C\x08Y\xe9\xfe%#'\xf0\xefP0\xf9\x04\xc3\x9b\x80\xff"
                       b'\x7f\xb5\xa6\xfe\xfe\x84 \x9c\x98\xc5\x00>\xd6\xf8\x9f\x16'
                       b"\xfe\xbb\x88\xd7HJ\x98!\x13*5\x0f\xda\xb8\xcd\x12'\x10\x05W"
                       b'X\x02\xc7\x90\xb7\x84\x15N\xe0>\xb0vs\x8c\xd1\xb8?\x9f@\x90'
                       b'\\D\xe1\x06\x18\x80\x8f\xbao\xd6\xb4\x17I\xa1\x170\xb4\xf7xn'
                       b'B\xa8\x8b\x12\xf6O\xf8\xfbh\xe7y\xa3\xe1\x07\xcbA\xdec\xe0\x04'
                       b"z\xdd\xab\xb7\xd2t\x0c\xc4\xda6\xee\xcf'8\xe3\x1a]\x10\x18\x80"
                       b"\xff\r]{\xc1\xc6'8\x08\xa1\xa0\xe7a\x1b\xe0\x83\xec\x04Y\x01"
                       b'\xc3\xc9\x18\xf5\x81\xfb6\n\x0c\x1d\xda<\x08\xc0\x9a\x01\xdd\xfe|9'
                       b'\x96\xf7\t\x96\x8d\x95\x99\x1d\x1c\xe7\x04\xe2=;\xb8?\x9f\xe0\x8cE'
                       b'\xa5\x86\x03\x83n\xfffB{w\xe3^=S\xf0\xe1F\xf46\xd0\xb5\x93\t|'
                       b'\xdc\xdc\xf38\x00>\x1f\xc85\xa7\xc2\x19\x84uA\xce\t\xac\x97\xb3'
                       b'\xfb\x9b\x08)Y\xdd&\x86s9&hx8\x03\xd1\x19H\xdd>\x92\x01\xfc\xa3'
                       b'tc\xbe\xd3V8\xdd\xf3\xdb\x1c\xb3}\x98\xf4]f\x08\xfe_@\x16\xc2\x9b>'
                       b'\x13J\xd6-\x9c\xe7\x04\xe2\x01\xd1\xf3d\x1e\xe0\x15\x11'
                       b'l\xef\xda\xc3\x1c\x134y2\xc7\xaf\x89\x8e\xc0\x1e\x0c'
                       b'\xd9\xbb\x93\x91\xc3\x170\xc93E\xb7\xd4\x1bx\xc5{\xf6Q\xb9#'
                       b"\xc8x\xa9\x07\xba\xfe? \xf8\x98\x90\xfa\x81LM\xabG\xf4[='\x10\xff/"
                       b'\xee,\xb9\x02\x8c\\A\x98\xb0 \x18\x870M\xd0\x9aD\xe0\xebY'
                       b'3\x1b\x91\xc3\x874.d\xf2 \x99C\xd6\xf3s\xb2\xaa\xd7+\x1dx\x83.\xc3'
                       b'\xe7\x01\xfe\xba\xce\xce\x8e.\x0e\xf0\x87\x0ci:\x82\x08\xfeOE\xf1'
                       b'\x86\x90n\x1f}\xd1\x9d\x13\xd8\xda:l\x0c\xa1\xdb\xfao\xc6\xd99'
                       b'\x1e\xca\xb0I\xf0\x1e\xf6\x10x\x8e\x03c\xeb\xdf`\xee4\x9a+\t'
                       b'\x05A\xfa\x03\x82}\x8dD}\xd1\x9e\x13\x88\xb7hk\x8c\xdf\x16\xc0'
                       b'x\xca\x18\xdd\xe9\xd7\x13\xd8\x07?\xbb\x8e\x13|\xbc\x8a\x9ep/\xe1'
                       b'=\x01\xfc\x17\xed9\x81\xd0\xbd~\x9c\xe0\xdc\xef2\xa7\x8bq8x'
                       b'$\x06\xf0\x1f\xe5\xea\xf6\xf7\xbf@\xb9E\x04\xfbN\x0c\xe0\xbfh\xcf'
                       b'\t\x84\xe5\x0b./\x9e\xd34\x00{\x81<s\xad\xa0B\xae\xd1wG\x00\xfen'
                       b'\x9c\xed\xcbC#\xd9\xc0\xc7\xa5\x1f<g\x87\xc6\x96\xbfz\xe58\x92'
                       b'v`\xd4\xad\x04\xa7N\xb5d\xfc\xe1\xb8?\xdf\xe2\x15\xefOp\xac'
                       b'\xf3\xbdO"I\x7f\x88`\xcfmI\x07\x1f\xa3s\x15\xa1!\x13m1ep)'
                       b'\x86\xfb\xf3\x8bG\xda\xb0\x9d\x10\xba\x06\xd3\xbb\x1c\x19>'
                       b"\x9f\xf6\x8e!\xae\xef+\x92\n>~\xce'4\xe2\x05l\x84m\xa6\x0c\x82\x85["
                       b'\xb4\xe5.\xdd\xed!\xc0\x7f\x17K\xbaX\xd5\xe3(\xec\x10_\x1e\xca'
                       b'n\xdf\xffH*\xf8x\xa9\xf2\xab\x84\x06\xcc\x89\x81&\x85\xeb}\xdc'
                       b'\xa8\x89{\xf5p\xbb\x16\xee\xd8A\xc6\xeeN)\xf8\xf75\x92Tq-2yl'
                       b'\x939J\xe8\x9bA\xf0\xdf?\xb0D\x1c\xfb9\x81\x1e\x0f\xa3\x1cs'
                       b'\xfa\x9b\x80\x199\x9bL\xa3\xa4\xea[\xa9\x1b\x96`\xb5pS\x94\xe0'
                       b'\xd7z\xac-\xdd\x0f\xc3-\xc9\xba\r\x1cX\x94\x98X\x06_\xaboT)_*'
                       b'\x13\xd2\xf7\x81\x9fy\xb4m\xf0=\xef\x0e.qz\xd6C\x841\xf5\xc62\xf8d'
                       b"}\xd7S\xf2\x10\xa6'\x84\x9a\xdc\x1d\xac~>J\x00\x7fKWWGg\x19|"
                       b'\xb2\xbe\x01\xf3\xa9Ry\r\x98\xab\x9ci\xf0r\x1b\xdf\x1d\xecL\xae'
                       b'\xb4\x85\x13\x98\xb4\\Q\x06?\xb0\xbe\x0b\x08I\xad\x8d'
                       b'\x12\x83\xa0\xe0\xb3\xdc\x1d\x8c\x9f\xab\tU\xb8?M\x9dztC\x19'
                       b'\xfc\xc0\x9f4\xf8\xef\x8f\x84\xa4\xd6W\x02\x82\xcfvw'
                       b'\xb0\xef\xe5\xd1N\xe4\xc2!\x91\xa7\x94\xc1\x0f\xa7\xafP(|\x84\x90'
                       b'\xd1\xc4\xd4z\x1b\x11|\xd6\xbb\x83\x7f\xa6\x03\x1f\x96+w\x97\xc17'
                       b'\xd3\x07>\\L\xc8h\xdeE\xd0\xc7zw\xf0tB\xee|[kk\xcb\xe82'
                       b'\xf8f\xfa\xda\xdaZ\x0f\x05_\xbeCHgO\xf5\xd1\xc7zw0~\xf9\x19]'
                       b'\xe1\x04&~_/\x83\xcf\xa3\x0f\xfc\xfa%A\xe3@\xa6K\xe4qX\xef\x0e\xbe'
                       b'L_5\xcbl\xe8\xed\x1d\xdf\xcc\xe5\x0c\xcc\xc5\xe3\xc6T82\xf5'
                       b'\xf8$\xdfB\xde\xdd\xdd\xd9\x01K\xb3\x8f\x88\xe2\xc1\x95YF\xfb\x90'
                       b'\xb6\xf6,!\x08.\xf1\xc8\xe0\xb2r\x02\xf1\xf7\x9btI\x8a|>\xffq.\xe7'
                       b'BAg\x0e$=\x9e\xf5\x18\x03\x9b\x93\x02>2y$\x99\xc3]\xcf\xbfC\xf0'
                       b'\x1dby\x1a!\x006\xb8\xf4\xb1s\x02\x9b\x04\x81y\x03o\xe9\\S\xe765'
                       b'5N\x02\x8a\xd9\xaf4\x13 $p\x8e\x8c\x0b|\xb0\xf1H\xe0\xf0\xfdPC\xe3'
                       b'\xc2\xa3\xf8\x0fg\xb0o6\xa5\x8a\t\xdb\xf8\xebmr\x02\xf1F\x91'
                       b'\xddBO\xbbz\x1f~\x7fV\x18\xe7"3\x0660\xdc\x00\xbav\x05\xa8\xe7\xff'
                       b'\xaf,E\x17l\x83\x0f\x97d\xb7#o\x1fz\xa5\xdf\x06\xb0\x0f\x19'
                       b'\xd1\xb8\xb1\xa4\xd1\x00|\xed)\xe1`\xc7.\x18z\x1bms\x02\x97'
                       b'\t\x1a\xed*P\x10 \x9d\x0c\xa2\x177D\xbcf\xc0\xe4\xc1\xd2.'
                       b'\xde\x7f0\x9d\x1b|\x18\xdb\xa7\xcb\xedZ&;v\xde\x14\xc5\xbd\xfc'
                       b'\x19\x0b\xe0c}`i\x14\x9c\xc0\x0ex\xd8&"\xed\x8a\x14\x04H'
                       b'\x87\x82\x89\xe3*F\x1aW\x1f\xden\xc6\x08\xfe\xd9x\xf3\t\xa3}'
                       b'\xcf\xc0!\xd8\xa7r\x82\x0f6mR\x96\xddvK\xc40\xf6M\x04\xc06\x13\x9d'
                       b'\xe1\x17\x04\xad\xf0\xbd\xbb,q\xf8\xb6\x1ez\xe8\xc8vSg@&\xb3\x06tm'
                       b'\xb1\xc11\xc4\x83-\xf0\xc0\x07\x0e\xf0\x81\x9e>>RfPssSo1\x08'
                       b'H\xcep\x07\x01n\xb6\xbc\n\xbe\xf7\x8eM\xeavmm\xed\\\xd31\x1fV!'
                       b'\x1f\xb3{#\xe9\xbe\t\xe4\xd7\\E\x9dd\x83\xef\x08\xf6\x048\x1c'
                       b'\x10\x1d\xe0\x04\x01\x96\x8f\xd7Gq\xdd+\xdewh~$|\xe5\xc2'
                       b'\x88\xae\xa3\xc5\xca\xde\xcc\x7f\x1b\xf0\x95\x87\x8d\x10\x84-'
                       b'Z\xc2|\xd3\xc6\x9fE\x91\x16\xbd&\x80\xbe5\xa6\xed\x85\x89\xd5\xd3'
                       b'\x01\xc0_#\x97\xa6\x7f\x14\xd67\xa9D\x0b\xbe\x8e\x13H\x0e\x82\x10'
                       b"\xce\xc0+j.V\xd2\x9c\xf8'\x1e\x1dw/Q_KX\xf0!\xb3\xd7\r\xfa"
                       b'\xfa\x08`\xfdB\xda\x94R\x12f\xb8\xd1t\xf3\xc1\x00>\x85\x13H'
                       b'\n\x82\x80\xce\xc0!c\x81(^\x92\xe4\xf9\x81$L3A\xdf\xdc\xb0=\x1d\xec'
                       b'\x058\x9f\x00V\xc9\x8c$\xa6\xad\xc1\xc6\x05\\\x87=D\r>\x95'
                       b'\x13H\n\x82\x80\xe0#\xc7p4\x05,\x18\xe7\xef\xd1\xe8\xbb=\xec'
                       b'0\x07\xbao\xd7\x80\xb5\x8c:a&l\x9c\x8d\x1c|.N\xa06\x08\x02\x80\xbf'
                       b'\x1e\xe4\x0c\x11\xe0\x8c\x1f\xc8\xca]\xae\t\xa6\x17E\xc83\x83@\x9f'
                       b'n\x9f\xe3\xe5A\xf4A>\xe1tbQ\xc7*\xf8\x9c\x9c@m\x10\x10\xc1\xc7|'
                       b'\xf9\x97\x04\xe1\x9a5\xb7s\x9b\x9b\x87L \xbcY\x87\x04\x05\x1f\x96'
                       b'\xb8\xdd\x04p\xc6\x84\xc8\xedce\xef\x8bB\xb9\xae7\x06\xf0\xd98'
                       b'\x81\xbeA@\xcc\x18\xfe\x84:Q\xf3yS\x9f\x17\x84\xedT\x01\xc1'
                       b'\xbaH\xa3\xf3ew\xcf\x120\xfd\x8cm\xbe3\x06\xf0\xd98\x81\xa6'
                       b'\x19C<\x85l2\xd3R\xf46\rXKB\xbc\xa9\x8b5:\xefd*<\xe1\xae\xe0U\x11'
                       b'\x81\xcf\xca\t$\x81\xd5\xd22l,L\xa6\x96\x03\xf8\xbb$\xf88\x06^\xe8f'
                       b'\xaf\x18\x96t\xcf\x13\xfa\xdbNS\x01\xf4\xe1\xff\xfd\xbb'
                       b'F\xe7\x05\x8cU\xc7\n\xd9Km\x94\xe0\xef\x84\xfc\xc3}mm-=\x8c%lVN``'
                       b'\xb0\xe4\x81L\x05.}.g\xb4\x10\xc6\xd3\xc3\x02\xe8;\x8c\xa0\xaf'
                       b'\xcdF\xc9\x19\xeb\xf9\xae\x92.\x07\xf8\xac\x9c\xc0\xd8\x98'
                       b'7\x1a}\xba\xad\xd5\x9f\x0b\xa0\xefs\x1a]k\x13\xd0\xde y\x1cVN`\x12'
                       b'\xc1\xc7\xcf"\xcd\x84jE\x00}+5\x01p\xe3\xbf\t\xf8V\xcf\t\xf4zX'
                       b'\xc1\xc5EKG\xa8oVi\xf0\x8b7\x9f\x1cu\xd4\x11\r\x04}Y\xdd\x12\r'
                       b'\xd6\xf3\xb3\x12\xd0^\xaa\xbeH\xce\tT\xf3\x05y\x13\x1a\x92\x81>'
                       b'\xbc>\xce\xf3lc\xf5\xde\x03GD\xb8sw\xf7ms\x07\x12hk\x02\xda\x1b'
                       b'D\x9f\xd5s\x02k\x94q\xa6\xd6t\xe9h\xa8\xefIQ\xe2\xda\x9b'
                       b'\xfd\x926\x01\x1fu<\x91\xa0\xf6Z\xd5GYW:\xf9\x82je\x92\x91\x8aQ'
                       b'\xdf|\xe1}D\xba\xf1\x11\xf8\x8e><u;A\xed\xb5\xa6\x8f\x9aT\xa8R\xa4'
                       b'\xd2\xd0x\x0e}3l\x82\x8f\x02\x04\x91\x19\tj\xaf\x15}\xd4tbN\x91\xac'
                       b'\xa1\xf1\\\xfa\xf0\x00\xca\xf7\xdd7\x9f\x98\\\xb4 \x06'
                       b'\xde\xa4\xb2\xa3\xb3\xb3\xbd\x90\xa0\xf6\xb2\xeb\xa3\x16\x12\xb2'
                       b'\x8ad\x0c\x8dg\xd5\x07\xf7\xec<\xec\xba\x17\xc7\x18|G \x00\x96'
                       b'&\xad\xbd\x9c\xfa(\x0f\xacpK\xd2\xf4\xc1\x18=\x01\xc0\xda\xca\r'
                       b'>\xde\xb1\x03\xbaG\x1f\xcc\xfe\xa3D[Z\x91TR\xf5\xc1g\x1c'
                       b'\xac\xfdW\x08\x9f\x03,\x02\xc86\x00\x7f\xa9z\xc1\xd2'
                       b'\xc1\xe4\xbf\x7f\x01J"/\x0e\xfeK9y\x00\x00\x00\x00IEND\xaeB`\x82')

# endregion

# region Globals
this_addon_folder = os.path.split(__file__)[0]
webq_model_config_json_file = os.path.join(this_addon_folder, "web_query_model_config.json")


# endregion

# region Meta classes

# noinspection PyPep8Naming
class _MetaConfigObj(type):
    """
    Meta class for reading/saving config.json for anki addon
    """
    metas = {}

    class StoreLocation:
        Profile = 0
        AddonFolder = 1
        MediaFolder = 3

    # noinspection PyArgumentList
    def __new__(mcs, name, bases, attributes):

        config_dict = {k: attributes[k] for k in attributes.keys() if not k.startswith("_") and k != "Meta"}
        attributes['config_dict'] = config_dict

        for k in config_dict.keys():
            attributes.pop(k)
        c = super(_MetaConfigObj, mcs).__new__(mcs, name, bases, attributes)

        # region Meta properties
        # meta class
        meta = attributes.get('Meta', type("Meta", (), {}))
        # meta values
        setattr(meta, "config_dict", config_dict)
        setattr(meta, "__StoreLocation__", getattr(meta, "__StoreLocation__", 0))
        setattr(meta, "__config_file__", getattr(meta, "__config_file__", "config.json"))

        _MetaConfigObj.metas[c.__name__] = meta
        # endregion

        if not config_dict:
            return c

        mcs.attributes = attributes  # attributes that is the configuration items

        setattr(c, "media_json_file", mcs.MediaConfigJsonFile("_{}_{}".format(_MetaConfigObj.AddonModelName(),
                                                                              _MetaConfigObj.metas[
                                                                                  name].__config_file__).lower()))

        return c

    def __getattr__(cls, item):
        if item == "meta":
            return _MetaConfigObj.metas[cls.__name__]
        else:
            load_config = lambda: cls.get_config(cls.metas[cls.__name__].__StoreLocation__)
            config_obj = load_config()
            return config_obj.get(item)

    def __setattr__(cls, key, value):
        """
        when user set values to addon config obj class, will be passed to anki's addon manager and be saved.
        :param key:
        :param value:
        :return:
        """
        try:
            config_obj = cls.get_config(cls.metas[cls.__name__].__StoreLocation__)
            config_obj[key] = value
            store_location = cls.metas[cls.__name__].__StoreLocation__
            if store_location == cls.StoreLocation.AddonFolder:
                if cls.IsAnki21:
                    mw.addonManager.writeConfig(cls.AddonModelName, config_obj)
                else:
                    with open(cls.ConfigJsonFile(), "w") as f:
                        json.dump(config_obj, f)
            elif store_location == cls.StoreLocation.MediaFolder:
                with open(cls.media_json_file, "w") as f:
                    json.dump(config_obj, f)
            elif store_location == _MetaConfigObj.StoreLocation.Profile:
                if _MetaConfigObj.IsAnki21():
                    mw.pm.profile.update(config_obj)
                else:
                    mw.pm.meta.update(config_obj)
        except:
            super(_MetaConfigObj, cls).__setattr__(key, value)

    def get_config(cls, store_location):
        """

        :param store_location:
        :rtype: dict
        """

        def _get_json_dict(json_file):
            if not os.path.isfile(json_file):
                with open(json_file, "w") as f:
                    json.dump(cls.config_dict, f)
            with open(json_file, 'r') as ff:
                return json.load(ff)

        disk_config_obj = {}
        if store_location == _MetaConfigObj.StoreLocation.Profile:
            if _MetaConfigObj.IsAnki21():
                disk_config_obj = mw.pm.profile
            else:
                disk_config_obj = mw.pm.meta
        elif store_location == _MetaConfigObj.StoreLocation.AddonFolder:
            # ensure json file
            obj = _get_json_dict(_MetaConfigObj.ConfigJsonFile())

            if _MetaConfigObj.IsAnki21():
                disk_config_obj = mw.addonManager.getConfig(_MetaConfigObj.AddonModelName())
            else:
                disk_config_obj = obj
        elif store_location == _MetaConfigObj.StoreLocation.MediaFolder:
            disk_config_obj = _get_json_dict(cls.media_json_file)
        cls.config_dict.update(disk_config_obj)
        return cls.config_dict

    @staticmethod
    def IsAnki21():
        from anki import version
        return eval(version[:3]) >= 2.1

    @staticmethod
    def ConfigJsonFile():
        return os.path.join(_MetaConfigObj.AddonsFolder(), "config.json")

    @staticmethod
    def MediaConfigJsonFile(file_nm):
        return os.path.join(_MetaConfigObj.MediaFolder(), file_nm)

    @staticmethod
    def AddonsFolder():
        if _MetaConfigObj.IsAnki21():
            _ = os.path.join(mw.addonManager.addonsFolder(), _MetaConfigObj.AddonModelName())
        else:
            _ = os.path.join(mw.pm.addonFolder(), _MetaConfigObj.AddonModelName())
        if aqt.isWin:
            _ = _.encode(aqt.sys.getfilesystemencoding()).decode("utf-8")
        return _.lower()

    @staticmethod
    def AddonModelName():
        return __name__.split(".")[0]

    @staticmethod
    def MediaFolder():
        try:
            return os.path.join(mw.pm.profileFolder(), "collection.media")
        except:
            return ''


# endregion

# region Default Configuration Objects
class SyncConfig(metaclass=_MetaConfigObj):
    class Meta:
        __StoreLocation__ = _MetaConfigObj.StoreLocation.MediaFolder

    doc_size = (405, 808)
    image_field_map = {}
    qry_field_map = {}
    visible = True
    append_mode = False
    auto_save = False


class UserConfig(metaclass=_MetaConfigObj):
    class Meta:
        __StoreLocation__ = _MetaConfigObj.StoreLocation.MediaFolder
        __config_file__ = "user_cfg.json"

    load_on_question = True
    image_quality = 50
    provider_urls = [
        ("Bing", "https://www.bing.com/images/search?q=%s"),
        ("Wiki", "https://en.wikipedia.org/wiki/?search=%s"),
    ]
    preload = True


class ProfileConfig(metaclass=_MetaConfigObj):
    class Meta:
        __StoreLocation__ = _MetaConfigObj.StoreLocation.Profile

    is_first_webq_run = True


# endregion


class _ImageLabel(QLabel):
    cropMode = True
    mouse_released = pyqtSignal()
    canceled = pyqtSignal(bool)

    def __init__(self):
        super(_ImageLabel, self).__init__()
        self._image = None

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, img):
        self._image = img
        self.setPixmap(QPixmap.fromImage(img))

    def mouseReleaseEvent(self, event):
        self.crop()
        self.mouse_released.emit()

    def mousePressEvent(self, event):
        """

        :type event: QMouseEvent
        :return:
        """
        if event.button() == Qt.LeftButton:
            print("ImageHolder: " + str(event.pos()))
            self.mousePressPoint = event.pos()
            if self.cropMode:
                if hasattr(self, "currentQRubberBand"):
                    self.currentQRubberBand.hide()
                self.currentQRubberBand = QRubberBand(QRubberBand.Rectangle, self)
                self.currentQRubberBand.setGeometry(QRect(self.mousePressPoint, QSize()))
                self.currentQRubberBand.show()
        else:
            if self.currentQRubberBand:
                self.currentQRubberBand.hide()
            self.canceled.emit(True)

    def mouseMoveEvent(self, event):
        # print("mouseMove: " + str(event.pos()))
        if self.cropMode:
            self.currentQRubberBand.setGeometry(QRect(self.mousePressPoint, event.pos()).normalized())

    def paintEvent(self, event):
        if not self.image:
            return

        self.painter = QPainter(self)
        self.painter.setPen(QPen(QBrush(QColor(255, 241, 18, 100)), 15, Qt.SolidLine, Qt.RoundCap))
        self.painter.drawImage(0, 0, self.image)
        self.painter.end()

    def crop(self):
        rect = self.currentQRubberBand.geometry()
        self.image = self.image.copy(rect)
        self.setMinimumSize(self.image.size())
        self.resize(self.image.size())
        # QApplication.restoreOverrideCursor()
        self.currentQRubberBand.hide()
        self.repaint()


class _Page(QWebEnginePage):
    def __init__(self, parent, keyword=None, provider_url=''):
        super(_Page, self).__init__(parent)
        self.clicked_img_url = None
        self.keyword = keyword
        self.provider_url = provider_url

        # profile set
        self.profile.setHttpUserAgent(self.agent)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)

        # attribute
        self.settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        self.settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        self.settings.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, True)

    @property
    def agent(self):
        return 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X) ' \
               'AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A93 '

    # noinspection PyArgumentList
    def get_url(self):
        return QUrl(self.provider_url % self.keyword)

    def load(self, keyword):
        self.keyword = keyword
        if not keyword:
            url = QUrl('about:blank')
        else:
            url = self.get_url()
        super(_Page, self).load(url)

    @property
    def profile(self):
        """

        :rtype: QWebEngineProfile
        """
        return super(_Page, self).profile()

    @property
    def settings(self):
        return super(_Page, self).settings()


class _WebView(QWebEngineView):

    def __init__(self, parent):
        super(_WebView, self).__init__(parent)
        self.qry_page = None

    def add_query_page(self, page):
        if not self.qry_page:
            self.qry_page = page
            self.setPage(self.qry_page)

    def load_page(self):
        if self.qry_page:
            self.qry_page.load()


# noinspection PyMethodMayBeStatic,PyAttributeOutsideInit
class CaptureOptionButton(QPushButton):
    field_changed = pyqtSignal(int)
    query_field_change = pyqtSignal(int)

    def __init__(self, parent, icon=None):
        if icon:
            super(CaptureOptionButton, self).__init__(icon, "", parent)
        else:
            super(CaptureOptionButton, self).__init__("Options", parent)
        self.fld_names = []
        self.selected_index = 1

        # set style
        # self.setFlat(True)
        self.setToolTip("Capture Options")

        # setup menu
        self.menu = QMenu(self)

        # init objects before setting up
        self.field_menu = None
        self.field_action_grp = None
        self.qry_field_menu = None
        self.qry_field_action_grp = None

        # setup option actions
        self.setup_option_actions()
        self.setup_image_field([])
        self.setup_query_field([])

        # add menu to button
        self.setMenu(self.menu)

        self.setText("Options")

    def setup_query_field(self, fld_names, selected_index=0):
        self.query_fld_names = fld_names
        if not self.qry_field_menu:
            pix = QPixmap()
            pix.loadFromData(items_bytes)
            icon = QIcon(pix)
            self.qry_field_menu = QMenu("Query Field", self.menu)
            self.qry_field_menu.setIcon(icon)
        if not self.qry_field_action_grp:
            self.qry_field_action_grp = QActionGroup(self.qry_field_menu)
            self.qry_field_action_grp.triggered.connect(self.qry_field_action_triggered)
        if self.query_fld_names:
            list(map(
                self.qry_field_action_grp.removeAction,
                self.qry_field_action_grp.actions()
            ))
            added_actions = list(map(
                self.qry_field_action_grp.addAction,
                self.query_fld_names
            ))
            if added_actions:
                list(map(lambda action: action.setCheckable(True), added_actions))
                selected_action = added_actions[selected_index]
                selected_action.setChecked(True)

        self.qry_field_menu.addActions(self.qry_field_action_grp.actions())
        self.menu.addSeparator().setText("Fields")
        self.menu.addMenu(self.qry_field_menu)

    def setup_image_field(self, fld_names, selected_index=1):
        self.fld_names = fld_names
        if not self.field_menu:
            pix = QPixmap()
            pix.loadFromData(items_bytes)
            icon = QIcon(pix)
            self.field_menu = QMenu("Image Field", self.menu)
            self.field_menu.setIcon(icon)
        if not self.field_action_grp:
            self.field_action_grp = QActionGroup(self.field_menu)
            self.field_action_grp.triggered.connect(self.field_action_triggered)
        if self.fld_names:
            list(map(
                self.field_action_grp.removeAction,
                self.field_action_grp.actions()
            ))
            added_actions = list(map(
                self.field_action_grp.addAction,
                self.fld_names
            ))
            if added_actions:
                list(map(lambda action: action.setCheckable(True), added_actions))
                selected_action = added_actions[selected_index]
                selected_action.setChecked(True)
                self.selected_index = selected_index

        self.field_menu.addActions(self.field_action_grp.actions())
        self.menu.addSeparator().setText("Fields")
        self.menu.addMenu(self.field_menu)

    def setup_option_actions(self):
        # setup actions
        self.action_append_mode = QAction("Append Mode", self.menu)
        self.action_append_mode.setCheckable(True)
        self.action_append_mode.setToolTip("Append Mode: Check this if you need captured image to be APPENDED "
                                           "to field instead of overwriting it")
        self.action_append_mode.setChecked(SyncConfig.append_mode)

        self.action_auto_save = QAction("Auto-Save", self.menu)
        self.action_auto_save.setCheckable(True)
        self.action_auto_save.setToolTip("Auto-Save: If this is checked, image will be saved "
                                         "immediately once completed cropping.")
        self.action_auto_save.setChecked(SyncConfig.auto_save)

        self.action_open_user_cfg = QAction("Config", self.menu)
        pix = QPixmap()
        pix.loadFromData(gear_bytes)
        self.action_open_user_cfg.setIcon(QIcon(pix))

        # bind action slots
        self.action_append_mode.toggled.connect(self.on_append_mode)
        self.action_auto_save.toggled.connect(self.on_auto_save)
        self.action_open_user_cfg.triggered.connect(lambda: os.startfile(UserConfig.media_json_file))

        # add actions to menu
        self.menu.addActions([
            ac for ac in map(lambda nm: getattr(self, nm),
                             [att for att in dir(self) if att.startswith("action_")])
        ])

    def qry_field_action_triggered(self, action):
        """

        :type action: QAction
        :return:
        """
        self.qry_selected_index = self.qry_field_action_grp.actions().index(action)
        action.setChecked(True)
        self.query_field_change.emit(self.qry_selected_index)

    def field_action_triggered(self, action):
        """

        :type action: QAction
        :return:
        """
        self.selected_index = self.field_action_grp.actions().index(action)
        action.setChecked(True)
        self.field_changed.emit(self.selected_index)

    @staticmethod
    def on_append_mode(checked):
        SyncConfig.append_mode = True if checked else False

    @staticmethod
    def on_auto_save(checked):
        SyncConfig.auto_save = True if checked else False


class ResizeButton(QPushButton):
    def __init__(self, parent, dock_widget):
        super(ResizeButton, self).__init__("<>", parent)
        self.start_resize = False
        self.dock_widget = dock_widget
        self.setFixedWidth(10)
        self.setToolTip("Press to change the width of this dock!")

    def mouseReleaseEvent(self, evt):
        self.start_resize = False

    def mousePressEvent(self, evt):
        self.start_resize = True

    def mouseMoveEvent(self, evt):
        if self.start_resize:
            new_width = QApplication.desktop().rect().right() - QCursor().pos().x()
            self.dock_widget.setFixedWidth(new_width)
            doc_size = (new_width, self.dock_widget.height())
            SyncConfig.doc_size = doc_size
            self.dock_widget.resize(QSize(new_width, self.dock_widget.height()))
        evt.accept()


class WebQueryWidget(QWidget):
    img_saving = pyqtSignal(QImage)
    capturing = pyqtSignal()
    viewing = pyqtSignal()

    def add_query_page(self, page):
        self._view.add_query_page(page)

        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, True)
        self.show_grp(self.capture_grp, False)

    def reload(self):
        self._view.reload()

    def __init__(self, parent):
        super(WebQueryWidget, self).__init__(parent)

        # all widgets
        self._view = _WebView(self)
        self.lable_img_capture = _ImageLabel()
        self.lable_img_capture.mouse_released.connect(self.cropped)
        self.lable_img_capture.canceled.connect(self.crop_canceled)

        self.loading_lb = QLabel()
        self.capture_button = QPushButton('Capture (C)', self)
        self.capture_button.setShortcut(QKeySequence(Qt.Key_C))
        self.capture_button.clicked.connect(self.on_capture)

        self.return_button = QPushButton('Return', self)
        self.return_button.setMaximumWidth(100)
        self.return_button.setShortcut(QKeySequence("ALT+Q"))
        self.return_button.clicked.connect(self.on_view)

        # region Save Image Button and Combo Group
        self.save_img_button = QPushButton('Save (C)', self)
        self.save_img_button.setShortcut(QKeySequence(Qt.Key_C))
        self.save_img_button.setShortcutEnabled(Qt.Key_C, False)
        self.save_img_button.clicked.connect(self.save_img)

        dock_widget = self.parent()
        assert isinstance(dock_widget, QDockWidget)
        dock_widget.setFixedWidth(SyncConfig.doc_size[0])
        self.resize_btn = ResizeButton(self, dock_widget)

        self.capture_option_btn = CaptureOptionButton(self)
        self.capture_option_btn.setMaximumWidth(100)
        self.img_btn_grp_ly = QHBoxLayout()
        self.img_btn_grp_ly.addWidget(self.resize_btn)
        self.img_btn_grp_ly.addSpacing(5)
        self.img_btn_grp_ly.addWidget(self.capture_option_btn)
        self.img_btn_grp_ly.addWidget(self.return_button)
        self.img_btn_grp_ly.addWidget(self.save_img_button)
        self.img_btn_grp_ly.addWidget(self.capture_button)

        # endregion

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.loading_lb, alignment=Qt.AlignCenter)
        self.layout.addWidget(self._view)
        self.layout.addWidget(self.lable_img_capture, alignment=Qt.AlignCenter)
        self.layout.addItem(self.img_btn_grp_ly)

        # widget groups
        self.loading_grp = [self.loading_lb]
        self.view_grp = [self._view, self.capture_button, self.capture_option_btn]
        self.capture_grp = [self.lable_img_capture, self.return_button, self.save_img_button, ]

        # Visible
        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, False)
        self.show_grp(self.capture_grp, False)

        # other slots
        self._view.loadStarted.connect(self.loading_started)
        self._view.loadFinished.connect(self.load_completed)

        self.setLayout(self.layout)

        # variable
        self._loading_url = ''

    def loading_started(self):
        loading_gif_dir = os.path.join(this_addon_folder, "loading_gif")
        if os.path.isdir(loading_gif_dir):
            gifs = [f for f in os.listdir(loading_gif_dir) if os.path.isfile(os.path.join(loading_gif_dir, f))
                    and f.upper().strip().endswith(".GIF")]
        else:
            gifs = []
        if gifs:
            gif = random.choice(gifs)
            gif = os.path.join(loading_gif_dir, gif)
        else:
            gif = os.path.join(this_addon_folder, "loading.gif")
        if os.path.isfile(gif):
            mv = QMovie(gif)
            self.loading_lb.setMovie(mv)
            mv.start()

        self.show_grp(self.loading_grp, True)
        self.show_grp(self.view_grp, False)
        self.show_grp(self.capture_grp, False)

    def load_completed(self, *args):
        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, True)
        self.show_grp(self.capture_grp, False)

    def show_grp(self, grp, show):
        for c in grp:
            c.setVisible(show)

    def on_capture(self, *args):
        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))

        self._view.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lable_img_capture.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.lable_img_capture.image = QImage(self._view.grab(self._view.rect()))
        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, False)
        self.show_grp(self.capture_grp, True)

        # self.lable_img_capture.setVisible(True)

    def on_view(self, *args):
        QApplication.restoreOverrideCursor()
        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, True)
        self.show_grp(self.capture_grp, False)
        self.viewing.emit()
        self._view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.lable_img_capture.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def save_img(self, *args):
        self.img_saving.emit(self.lable_img_capture.image)
        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, True)
        self.show_grp(self.capture_grp, False)
        self._view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.lable_img_capture.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def cropped(self):
        QApplication.restoreOverrideCursor()
        self.show_grp(self.loading_grp, False)
        self.show_grp(self.view_grp, False)
        self.show_grp(self.capture_grp, True)

        if SyncConfig.auto_save:
            self.save_img()
            self.save_img_button.setShortcutEnabled(Qt.Key_C, False)
        else:
            self.save_img_button.setShortcutEnabled(Qt.Key_C, True)

    def crop_canceled(self):
        self.return_button.click()


class ModelDialog(aqt.models.Models):
    def __init__(self, mw, parent=None, fromMain=False):
        # region copied from original codes in aqt.models.Models
        self.mw = mw
        self.parent = parent or mw
        self.fromMain = fromMain
        QDialog.__init__(self, self.parent, Qt.Window)
        self.col = mw.col
        self.mm = self.col.models
        self.mw.checkpoint(_("Note Types"))
        self.form = aqt.forms.models.Ui_Dialog()
        self.form.setupUi(self)
        self.form.buttonBox.helpRequested.connect(lambda: openHelp("notetypes"))
        self.setupModels()
        restoreGeom(self, "models")
        # endregion

        # add additional button
        self.button_tab_visibility = QPushButton("Web Query Tab Visibility", self)
        self.button_tab_visibility.clicked.connect(self.onWebQueryTabConfig)
        self.button_tab_visibility.setEnabled(False)
        self.form.modelsList.itemClicked.connect(
            partial(lambda item: self.button_tab_visibility.setEnabled(True if item else False)))
        self.form.gridLayout_2.addWidget(self.button_tab_visibility, 2, 0, 1, 1)

    @property
    def mid(self):
        return self.model['id']

    @property
    def default_config(self):
        return {str(self.mid):
                # name, provider_url, visibility
                    [[n, u, True] for n, u in UserConfig.provider_urls]
                }

    def onWebQueryTabConfig(self, clicked):
        self.config = self.default_config
        if os.path.isfile(webq_model_config_json_file):
            with open(webq_model_config_json_file, "r") as f:
                try:
                    self.config = json.load(f)
                    default_config_items = self.default_config[str(self.mid)]
                    config_items = self.config[str(self.mid)]
                    if config_items.__len__() < default_config_items.__len__():
                        self.config[str(self.mid)].extend(default_config_items[config_items.__len__():])
                    else:
                        self.config[str(self.mid)] = self.config[str(self.mid)][:default_config_items.__len__()]
                except:
                    pass

        class _dlg(QDialog):
            def __init__(inner_self):
                super(_dlg, inner_self).__init__(self)
                inner_self.setWindowTitle("Toggle Visibility")

                inner_self.mode_config_items = self.config.get(str(self.mid), self.default_config[str(self.mid)])

                # shown check boxes
                inner_self.checkboxes = list(map(
                    lambda args: QCheckBox("{}: {}".format(args[0], args[1]), inner_self),
                    inner_self.mode_config_items)
                )
                list(map(lambda args: args[1].setChecked(inner_self.mode_config_items[args[0]][2]),
                         enumerate(inner_self.checkboxes)))
                list(map(lambda args: args[1].toggled.connect(partial(inner_self.on_visibility_checked, args[0])),
                         enumerate(inner_self.checkboxes)))

                ly = QVBoxLayout(inner_self)
                list(map(ly.addWidget, inner_self.checkboxes))
                inner_self.setLayout(ly)

            def on_visibility_checked(inner_self, index, checked):
                inner_self.mode_config_items[index][2] = checked
                with open(webq_model_config_json_file, "w+") as f:
                    self.config[self.mid] = inner_self.mode_config_items
                    json.dump(self.config, f)

        _dlg().exec_()


class WebQryAddon:

    def __init__(self):
        self.shown = False

        # region variables
        self.current_index = 0
        self._first_show = True
        # endregion

        self.dock = None
        self.pages = []
        self.webs = []
        self._display_widget = None

        addHook("showQuestion", self.start_query)
        addHook("showAnswer", self.show_widget)
        addHook("deckClosing", self.hide)
        addHook("reviewCleanup", self.hide)
        addHook("profileLoaded", self.profileLoaded)

        self.init_menu()

    def cur_tab_index_changed(self, tab_index):
        self.current_index = tab_index
        if not UserConfig.preload:
            self.show_widget()

    @property
    def page(self):
        return self.pages[self.current_index]

    @property
    def web(self):
        return self.webs[self.current_index]

    def init_menu(self):
        action = QAction(mw.form.menuTools)
        action.setText("Web Query")
        action.setShortcut(QKeySequence("ALT+W"))
        mw.form.menuTools.addAction(action)
        action.triggered.connect(self.toggle)

    # region replace mw onNoteTypes
    def profileLoaded(self):

        # region owverwrite note type management
        def onNoteTypes():
            ModelDialog(mw, mw, fromMain=True).exec_()

        mw.form.actionNoteTypes.triggered.disconnect()
        mw.form.actionNoteTypes.triggered.connect(onNoteTypes)
        # eng region

    # endregion

    @property
    def reviewer(self):
        """

        :rtype: Reviewer
        """
        return mw.reviewer

    @property
    def card(self):
        """

        :rtype: Card
        """
        return self.reviewer.card

    @property
    def note(self):
        """

        :rtype: Note
        """
        return self.reviewer.card.note()

    @property
    def word(self):
        if not mw.reviewer:
            return None
        qry_field = SyncConfig.qry_field_map.get(str(self.note.mid), 0)
        word = re.sub('<[^<]+?>', '', self.note.fields[qry_field]).strip()
        return word

    @property
    def model_config(self):
        default_empty = {str(self.note.mid): {}}
        if os.path.isfile(webq_model_config_json_file):
            with open(webq_model_config_json_file, "r") as f:
                try:
                    config = json.load(f)
                except:
                    config = default_empty
        else:
            config = default_empty
        try:
            return config[str(self.note.mid)]
        except KeyError:
            config = default_empty

        return config[str(self.note.mid)]

    @property
    def model_hidden_tab_index(self):
        if self.model_config:
            model_hidden_tab_index = [i for i, args in enumerate(self.model_config) if not args[2]]
        else:
            model_hidden_tab_index = []
        return model_hidden_tab_index

    def add_dock(self, title):
        class DockableWithClose(QDockWidget):
            closed = pyqtSignal()

            def __init__(self, title, parent):
                super(DockableWithClose, self).__init__(title, parent)

            def closeEvent(self, evt):
                self.closed.emit()
                QDockWidget.closeEvent(self, evt)

            def resizeEvent(self, evt):
                assert isinstance(evt, QResizeEvent)
                SyncConfig.doc_size = (evt.size().width(),
                                       evt.size().height())
                super(DockableWithClose, self).resizeEvent(evt)
                evt.accept()

            def sizeHint(self):
                return QSize(SyncConfig.doc_size[0], SyncConfig.doc_size[1])

        dock = DockableWithClose(title, mw)
        dock.setObjectName(title)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

        # region dock widgets
        available_urls = [url for i, (n, url) in enumerate(UserConfig.provider_urls)
                          if i not in self.model_hidden_tab_index]
        self.webs = list(
            map(lambda x: WebQueryWidget(dock, ), range(available_urls.__len__()))
        )
        self.pages = list(
            map(lambda params: _Page(parent=self.webs[params[0]], provider_url=params[1]),
                enumerate(available_urls))
        )

        for web in self.webs:
            web.img_saving.connect(self.save_img)

        # region main / tab widgets
        self._display_widget = QWidget(dock)
        if UserConfig.provider_urls.__len__() - self.model_hidden_tab_index.__len__() > 1:
            self._display_widget = QTabWidget(dock)
            self._display_widget.setTabPosition(self._display_widget.East)
            added_web = 0
            for i, (nm, url) in enumerate(UserConfig.provider_urls):
                if i in self.model_hidden_tab_index:
                    continue
                try:
                    self._display_widget.addTab(self.webs[added_web], nm)
                    added_web += 1
                except IndexError:
                    continue
            self._display_widget.currentChanged.connect(self.cur_tab_index_changed)
        else:
            l = QVBoxLayout(self._display_widget)
            try:
                l.addWidget(self.web)
            except IndexError:
                QMessageBox.warning(
                    mw, "No Provider URL", "You have no <em>[Provider URL]</em>"
                                           " selected<br><br>Go to Tools > Manage Note Types > Web Query Tab Visibility")
                return
            self._display_widget.setLayout(l)
        self._display_widget.setVisible(False)

        # endregion
        dock.setWidget(self._display_widget)
        mw.addDockWidget(Qt.RightDockWidgetArea, dock)

        return dock

    def start_query(self):
        if not self.ensure_dock():
            return
        if not self.word:
            return
        if UserConfig.preload:
            self.start_pages()
        if not UserConfig.load_on_question:
            self.hide_widget()
        else:
            self.show_widget()

    def start_pages(self):
        QApplication.restoreOverrideCursor()
        for wi, web in enumerate(self.webs, ):
            page = self.pages[wi]
            page.load(self.word)
            page.loadFinished.connect(lambda s: web.reload)
            web.add_query_page(page)
            if self.reviewer:
                image_field = SyncConfig.image_field_map.get(str(self.note.mid), 1)
                qry_field = SyncConfig.qry_field_map.get(str(self.note.mid), 0)
                web.capture_option_btn.setup_image_field(self.note.keys(), image_field)
                web.capture_option_btn.setup_query_field(self.note.keys(), qry_field)
                web.capture_option_btn.field_changed.connect(self.img_field_changed)
                web.capture_option_btn.query_field_change.connect(self.qry_field_changed)

    def hide_widget(self):
        self._display_widget.setVisible(False)

    def show_widget(self):
        if not self.dock:
            return
        self._display_widget.setVisible(True)
        if self._first_show:
            self.web.reload()
            self._first_show = False
        if not UserConfig.preload:
            self.start_pages()

    def hide(self):
        if self.dock:
            mw.removeDockWidget(self.dock)
            self.dock.destroy()
        self.dock = None

    def show_dock(self):
        self.dock.setVisible(True)

    def ensure_dock(self):
        if ProfileConfig.is_first_webq_run:
            QMessageBox.warning(
                mw, "Web Query", """
                <p>
                    <b>Welcome !</b>
                </p>
                <p>This is your first run of <EM><b>Web Query</b></EM>, please read below items carefully:</p>
                <ul>
                    <li>
                        Choose proper <em>[Image]</em> field in "Options" button in right dock widget 
                        BEFORE YOU SAVING ANY IMAGES, by default its set to the 2nd
                        field of your current note.
                    </li>
                    <li>
                        You are able to change the <em>[Query]</em> field in "Options" also, 
                        which is set to the 1st field by default.
                    </li>
                </ul>
                """)
            ProfileConfig.is_first_webq_run = False
        if not self.dock:
            self.dock = self.add_dock(_('Web Query'), )
            if not self.dock:
                return False
            self.dock.closed.connect(self.on_closed)
        self.dock.setVisible(SyncConfig.visible)
        return True

    def toggle(self):
        if not self.ensure_dock():
            return
        if self.dock.isVisible():
            SyncConfig.visible = False
            self.hide()
        else:
            SyncConfig.visible = True
            self.show_dock()

    def on_closed(self):
        mw.progress.timer(100, self.hide, False)

    def img_field_changed(self, index):
        if index == -1:
            return
        _mp = SyncConfig.image_field_map
        _mp[str(self.note.mid)] = index
        SyncConfig.image_field_map = _mp

        for web in self.webs:
            if not web is self.web:
                web.capture_option_btn.setup_image_field(self.note.keys(), index)

    def qry_field_changed(self, index):
        if index == -1:
            return
        _mp = SyncConfig.qry_field_map
        _mp[str(self.note.mid)] = index
        SyncConfig.qry_field_map = _mp
        for web in self.webs:
            if not web is self.web:
                web.capture_option_btn.setup_query_field(self.note.keys(), index)

    def save_img(self, img):
        """

        :type img: QImage
        :return:
        """
        img = img.convertToFormat(QImage.Format_RGB32, Qt.ThresholdDither | Qt.AutoColor)
        if not self.reviewer:
            return
        fld_index = self.web.capture_option_btn.selected_index
        anki_label = '<img src="{}">'
        fn = "web_qry_{}.jpg".format(uuid4().hex.upper())
        if SyncConfig.append_mode:
            self.note.fields[fld_index] += anki_label.format(fn)
        else:
            self.note.fields[fld_index] = anki_label.format(fn)
        if img.save(fn, 'jpg', UserConfig.image_quality):
            self.note.flush()
            self.card.flush()
            tooltip("Saved image to current card: {}".format(fn), 5000)
        # self.reviewer.show()


WebQryAddon()
