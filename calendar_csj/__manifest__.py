# -*- coding: utf-8 -*-
{
    'name': "Appointments CSJ",

    'summary': "Appointments CSJ",

    'description': "Appointments CSJ",

    'author': "Todoo SAS",
    'contributors': ['Pablo Arcos pa@todoo.co', 'Oscar Bolaños ob@todoo.co', 'Jhair Escobar je@todoo.co'],
    'website': "http://www.todoo.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Marketing/Online Appointment',
    'version': '13.1.1',

    # any module necessary for this one to work correctly
    'depends': ['website_calendar','contacts','base_address_city','event', 'calendar'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/res_country.xml',
        'data/res_partner.xml',
        'data/mail_template.xml',
        'data/calendar_appointment.xml',
        'views/res_judged_view.xml',
        'views/res_entity_view.xml',
        'views/res_specialty_view.xml',
        'views/res_judged_room_view.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        'views/calendar_appointment_view.xml',
        'views/calendar_class_view.xml',
        'views/calendar_help_view.xml',
        'views/calendar_csj_templates.xml',
        'views/calendar_reception_view.xml',
        'views/calendar_event_view.xml',
        'views/template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
