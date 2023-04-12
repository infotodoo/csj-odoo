# Part of Odoo, Aktiv Software.
# See LICENSE file for full copyright & licensing details.

# Author: Aktiv Software.
# mail:   odoo@aktivsoftware.com
# Copyright (C) 2015-Present Aktiv Software PVT. LTD.
# Contributions:
#           Aktiv Software:
#              - Dhara Solanki
#              - Virendrasinh Dabhi
#              - Harshil Soni and Tanvi Gajera

{
    'name': "Odoo Microsoft Teams Integration",
    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'summary': """
        You can Generate Microsoft Teams Link for your Meetings in Calendar.
        """,
    'description': """
        Title: Odoo Microsoft Teams Integration \n
        Author: Aktiv Software \n
        mail: odoo@aktivsoftware.com \n
        Copyright (C) 2015-Present Aktiv Software PVT. LTD. \n
        Contributions: Aktiv Software
        """,
    "license": "OPL-1",
    "price": 25.00,
    "currency": "EUR",
    'category': 'Tools',
    'version': '15.0.1.0.1',
    'depends': ['calendar'],
    'installable': True,
    'application': False,
    'data': [
        'views/teams_calendar_event.xml',
        'views/res_users_views.xml',
        'views/res_company_views.xml',
        ],
    'images': [
        'static/description/banner.jpg'
        ],
}
