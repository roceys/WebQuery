# -*- coding: utf-8 -*-
# Copyright: kuangkuang <upday7@apl.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Project : WebQuery
Created: 1/4/2018
"""
import os
from pprint import pprint

mario_bytes = []
for dir_entry in os.scandir("."):
    if dir_entry.path.endswith("gif"):
        mario_bytes.append(bytearray(open(dir_entry.path, "rb").read()))
pprint(mario_bytes)

