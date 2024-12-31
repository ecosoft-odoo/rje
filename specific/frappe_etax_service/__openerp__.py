# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################


{
    'name': 'Connector to Frappe eTax service',
    'version': '1.0',
    'author': 'Kitti U., Ecosoft',
    'license': 'AGPL-3',
    'website': 'https://github.com/ecosoft-odoo/ecosoft-addons',
    'category': 'Accounting',
    'description': """
    Connector to Frappe eTax service.
    """,
    'depends': [
        'account', 'account_debitnote'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/purpose_code_data.xml',
        'data/cron.xml',
        'wizards/wizard_select_etax_doctype_view.xml',
        'wizards/account_debitnote_view.xml',
        'wizards/account_invoice_refund_view.xml',
        'wizards/wizard_select_replacement_purpose.xml',
        'views/account_move_views.xml',
        'views/account_voucher_views.xml',
        'views/res_config_settings.xml',
        'views/purpose_code_views.xml',
        'views/doctype_views.xml',
        'views/base_vat_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
