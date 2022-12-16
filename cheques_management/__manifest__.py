# -*- coding: utf-8 -*-
{
    'name': "Cheque Management",

    'summary': """
        To add cheque logs function to the system alongside partner ledgers info reading
        """,

    'description': """
        To add cheques and allocate them to one or more invoices and will be reflected in partner ledgers
    """,

    'author': "Computs Sdn Bhd",
    'website': "http://www.computs.com.my",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_reports','account_accountant'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/cheque_logs.xml',
        'views/account_move.xml',
        'views/sequences.xml',
        'views/account_payment.xml'
        # 'views/post_dated_cheque.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
