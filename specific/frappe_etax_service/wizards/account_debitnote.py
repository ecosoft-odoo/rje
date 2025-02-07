# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################

import logging
from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)

class AccountDebitNote(models.TransientModel):
    _inherit = "account.debitnote"

    purpose_code_id = fields.Many2one(
        "purpose.code", string="Refund Reason", domain="[('is_debit_note', '=', True)]"
    )
    purpose_code = fields.Char(string="Purpose Code")

    @api.onchange("purpose_code_id")
    def _onchange_purpose_code_id(self):
        if self.purpose_code_id:
            self.purpose_code = self.purpose_code_id.code
            self.description = (
                (self.purpose_code_id.code != "DBNG99")
                and self.purpose_code_id.name
                or ""
            )

    @api.multi
    def invoice_debitnote(self):
        result = super(AccountDebitNote, self).invoice_debitnote()
        inv_obj = self.pool.get('account.invoice')
        created_inv = inv_obj.browse(self._cr, self._uid, result['domain'][0][2])
        for form in self:
            purpose_code_id = form.purpose_code_id
            description = form.description
            origin = inv_obj.browse(self._cr, self._uid, self._context.get('active_id')).preprint_number
            if created_inv:
                for inv in created_inv:
                    inv.write(
                        {
                            "origin": origin,
                            "create_purpose_code": purpose_code_id.code,
                            "create_purpose": description,
                        }
                    )
        return result
