# -*- coding: utf-8 -*-
# Copyright 2014 wangbuke <wangbuke@gmail.com>
# Copyright 2017 Jarvis <jarvis@odoomod.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Web PDF Report Preview & Print",
    'version': '1.0',
    'category': 'Web',
    'description': """Web PDF Report Preview & Print

Preview & Print PDF report in your browser.

* For IE, Adobe Reader is required.
* For Chrome , nothing is requried.
* For Firefox, Adobe Reader is required.


If your brower prevented pop-up window, you should allow it.

功能：PDF 报表预览

    """,
    'author': 'wangbuke, OdooMod',
    'website': 'http://www.odoomod.com',
    'license': 'AGPL-3',
    'depends': ['web'],
    'data': [
        'views/web_pdf_preview.xml',
    ],

}
