# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################

from openerp.osv import osv, fields


class PurposeCode(osv.osv):
    _name = "purpose.code"
    _description = "Purpose Code follow INET convention."

    _columns = {
        'name': fields.char('Name', required=True),
        'code': fields.char('Code', required=True),
        'reason': fields.char('Reason', required=False),
        'is_tax_invoice': fields.boolean('Tax Invoice'),
        'is_credit_note': fields.boolean('Credit Note'),
        'is_debit_note': fields.boolean('Debit Note'),
        'is_receipt': fields.boolean('Receipt'),
        'is_replacement': fields.boolean('Replacement'),
    }

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        for rec in self.browse(cr, uid, ids, context=context):
            name = u"{} - {}".format(rec.code, rec.name).encode('utf-8')
            res.append((rec.id, name))
        return res
