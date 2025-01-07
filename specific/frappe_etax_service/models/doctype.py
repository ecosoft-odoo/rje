# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################


from openerp.osv import osv, fields

class DocType(osv.osv):
    _name = 'doc.type'
    _description = 'For config doctype code that send to INET'
    _rec_name = 'name'

    _columns = {
        'name': fields.char(
            string='Form Name',
            required=True,
        ),
        'type': fields.selection(
            [
                ('out_invoice', 'Customer Invoice'),
                ('out_refund', 'Customer Credit Note'),
                ('out_invoice_debit', 'Customer Debit Note'),
                ('receipt', 'Customer Payment'),
            ],
            string='Type',
        ),
        'doc_source_template': fields.selection(
            string='Invoice template source',
            selection=[
                ('odoo', 'odoo'),
                ('frappe', 'frappe'),
            ],
            default='odoo',
            help='Select source template between Odoo and Frappe',
        ),
        'doctype_code': fields.selection(
            string='Code',
            selection=[
                ('388', '388 ใบกํากับภาษี'),
                ('T02', 'T02 ใบแจ้งหนี้/ใบกํากับภาษี'),
                ('T03', 'T03 ใบเสร็จรับเงิน/ใบกํากับภาษี'),
                ('T04', 'T04 ใบส่งของ/ใบกํากับภาษี'),
                ('T05', 'T05 ใบกํากับภาษี อย่างย่อ'),
                ('T01', 'T01 ใบรับ (ใบเสร็จรับเงิน)'),
                ('80', '80 ใบเพิมหนี้'),
                ('81', '81 ใบลดหนี้'),
            ],
            help="""
                380 : ใบแจ้งหนี้,
                388 : ใบกํากับภาษี,
                T02 : ใบแจ้งหนี้/ใบกํากับภาษี,
                T03 : ใบเสร็จรับเงิน/ใบกํากับภาษี,
                T04 : ใบส่งของ/ใบกํากับภาษี,
                T05 : ใบกํากับภาษี อย่างย่อ,
                T01 : ใบรับ (ใบเสร็จรับเงิน),
                80 : ใบเพิมหนี้,
                81 : ใบลดหนี้,
            """,
        ),
    }

    _sql_constraints = [
        (
            'code_uniq_per_doc',
            'UNIQUE(name)',
            'Doc name template must be unique',
        ),
    ]

