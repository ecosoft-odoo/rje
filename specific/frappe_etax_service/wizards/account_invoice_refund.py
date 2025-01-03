# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################


from openerp import models, fields, api, _


class account_invoice_refund(models.Model):
    _inherit = "account.invoice.refund"

    purpose_code_id = fields.Many2one(
        "purpose.code", string="Refund Reason", domain="[('is_credit_note', '=', True)]"
    )
    purpose_code = fields.Char(string='Purpose Code')

    @api.onchange("purpose_code_id")
    def _onchange_purpose_code_id(self):
        if self.purpose_code_id:
            self.purpose_code = self.purpose_code_id.code
            self.description = (
                (self.purpose_code_id.code != "DBNG99")
                and self.purpose_code_id.name
                or ""
            )
    
    def invoice_refund(self, cr, uid, ids, context=None):
        result = super(account_invoice_refund, self).invoice_refund(cr, uid, ids, context)
        inv_obj = self.pool.get('account.invoice')
        created_inv = inv_obj.browse(cr, uid, result['domain'][1][2], context=context)
        for form in self.browse(cr, uid, ids, context=context):
            purpose_code_id = form.purpose_code_id
            description = form.description
            origin = form.preprint_number
            if created_inv:
                for inv in created_inv:
                    inv.write({
                        'origin': origin,
                        'create_purpose_code': purpose_code_id.code,
                        'create_purpose': description,
                    })
        return result
