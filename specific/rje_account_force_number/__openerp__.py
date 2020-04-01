# -*- coding: utf-8 -*-
{
    'name': "RJE Force Number for Invoice, Payment and Bank Receipt",
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'summary': "Allows to force invoice numbering on specific invoices",
    'description': """
    """,
    'author': "Agile Business Group,Odoo Community Association (OCA)",
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends": [
        'account', 'account_voucher',
        'l10n_th_account', 'account_bank_receipt',
    ],
    "data": [
        'invoice_view.xml',
        'voucher_view.xml',
    ],
    "active": False,
    "installable": True,
}
