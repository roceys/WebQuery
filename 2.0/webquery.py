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

__version__ = '1.2.0'


# USER PLEASE READ
# YOU MUST NOT CHANGE THE ORDER OF ** PROVIDER URLS **
# ONLY IF THE VISIBILITY OF TABS OF A MODEL IS TO BE RE-TOGGLED

def start():
    import WebQuery
    WebQuery.WebQryAddon(
        load_on_question=True,
        image_quality=50,
        preload=True,
        provider_urls=[
            ("Bing", "https://www.bing.com/images/search?q=%s"),
            ("Wiki", "https://en.wikipedia.org/wiki/?search=%s"),

            # REMOVE BELOW "#" IN FRONT OF A LINE TO ENABLE THE PROVIDER URL

            # ("Renren", "http://www.91dict.com/words?w=%s"),
            # ("DWDS", "https://www.dwds.de/wb/%s"),
            # ("Littre", "https://www.littre.org/definition/%s"),
            # ("vajehyab", "https://www.vajehyab.com/?q=%s"),
            # ("naver", "http://hanja.naver.com/search?query=%s"),
            # ("MFCCD", "http://humanum.arts.cuhk.edu.hk/Lexis/lexi-mf/search.php?word=%s"),
            # ("takuhon", "http://coe21.zinbun.kyoto-u.ac.jp/djvuchar?query=%s"),
            # ("shufa", "http://shufa.guoxuedashi.com/?sokeyshufa=%s&submit=&kz=70"),
            # ("hanviet", "http://hanviet.org/hv_timchu_ndv.php?unichar=%s"),
            # ("Etimo", "https://www.etimolojiturkce.com/kelime/%s"),
            # ("Nisanyan", "http://www.nisanyansozluk.com/?k=%s"),
            # ("etybank", "http://www.etymologiebank.nl/zoeken/%s"),
            # ("swahili", "http://siwaxili.com/%s"),
            # ("turner",
            #  "http://dsalsrv02.uchicago.edu/cgi-bin/philologic/search3advanced?dbname=turner&query=%s&matchtype=exact&display=utf8"),
            # ("schmidt", "http://dsalsrv02.uchicago.edu/cgi-bin/app/schmidt_query.py?qs=%s&searchhws=yes"),
            # ("chgis", "http://maps.cga.harvard.edu/tgaz/placename?fmt=html&n=%s"),
            # ("CVH", "http://www.cvh.ac.cn/ppbc/%s"),
            # ("CFH", "http://www.cfh.ac.cn/Spdb/spsearch.aspx?aname=%s"),
            # ("FRPS", "http://frps.eflora.cn/frps?id=%s"),
            # ("PPBC", "http://www.plantphoto.cn/list?keyword=%s")
        ]
    )


addHook("profileLoaded", start)
