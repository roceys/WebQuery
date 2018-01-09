# -*- coding:utf-8 -*-
#
# Copyright © 2016–2017 KuangKuang <upday7@163.com>
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version; http://www.gnu.org/copyleft/gpl.html.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from anki.hooks import addHook

__version__ = '1.2.33'


# USER PLEASE READ
# YOU MUST NOT CHANGE THE ORDER OF ** PROVIDER URLS **
# ONLY IF THE VISIBILITY OF TABS OF A MODEL IS TO BE RE-TOGGLED

def start():
    import WebQuery
    WebQuery.WebQryAddon(version=__version__)


addHook("profileLoaded", start)
